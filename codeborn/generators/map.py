from __future__ import annotations

import asyncio
from pathlib import Path
import random

import numpy as np
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt

from codeborn.logger import get_logger, init_logging
from codeborn.model import Army, Location, TerrainType
from codeborn.database import init_db, close_db
from codeborn.config import CodebornConfig, MapGeneratorConfig, get_config


COLOR_MAP = {
    TerrainType.plains: (0.8, 0.9, 0.5),
    TerrainType.forest: (0.1, 0.6, 0.1),
    TerrainType.swamp: (0.5, 0.5, 0.5),
}
MAP_PATH = Path('map.png')


async def random_location(config: MapGeneratorConfig) -> Location:
    """Find new random location in an least occupied chunk chunk."""

    rng = np.random.default_rng()

    async def find_unoccupied_location(
        x_bounds: tuple[int, int],
        y_bounds: tuple[int, int],
        occupied: set[tuple[int, int]]
    ) -> Location | None:
        """Randomly select an unoccupied location."""
        for _ in range(16):
            x = rng.integers(*x_bounds)
            y = rng.integers(*y_bounds)
            if (x, y) not in occupied:
                return await Location.get(x=x, y=y)

    chunk_x_count = (config.width + config.chunk_size - 1) // config.chunk_size
    chunk_y_count = (config.height + config.chunk_size - 1) // config.chunk_size

    chunk_counts = np.zeros((chunk_x_count, chunk_y_count), dtype=int)

    for x, y in await Army.all().values_list('location__x', 'location__y'):
        chunk_x = x // config.chunk_size
        chunk_y = y // config.chunk_size
        chunk_counts[chunk_x, chunk_y] += 1

    weights = 1 / (chunk_counts + 1)
    flat_weights = weights.flatten()
    flat_weights /= flat_weights.sum()

    chunk_index = rng.choice(len(flat_weights), p=flat_weights)
    chunk_x, chunk_y = np.unravel_index(chunk_index, weights.shape)
    chunk_x = int(chunk_x)
    chunk_y = int(chunk_y)

    x_bounds = (chunk_x * config.chunk_size, min((chunk_x + 1) * config.chunk_size, config.width))
    y_bounds = (chunk_y * config.chunk_size, min((chunk_y + 1) * config.chunk_size, config.height))
    occupied = set(
        await Army.filter(
            location__x__gte=x_bounds[0], location__x__lt=x_bounds[1],
            location__y__gte=y_bounds[0], location__y__lt=y_bounds[1],
        ).values_list('location__x', 'location__y')
    )
    if location := await find_unoccupied_location(x_bounds, y_bounds, occupied):
        return location

    occupied = set(await Army.all().values_list('location__x', 'location__y'))
    x_bounds = (0, config.width)
    y_bounds = (0, config.height)
    if location := await find_unoccupied_location(x_bounds, y_bounds, occupied):
        return location

    raise RuntimeError('Cannot find an unoccupied location.')


def generate_terrain(config: MapGeneratorConfig) -> np.ndarray:
    """Generate terrain data."""

    elevation = generate_noise_map(
        config.octaves,
        config.width,
        config.height,
        config.elevation_scale,
        config.elevation_contrast_enhancement,
        config.seed + 1
    )

    moisture = generate_noise_map(
        config.octaves,
        config.width,
        config.height,
        config.moisture_scale,
        config.moisture_contrast_enhancement,
        config.seed + 2
    )

    terrain = np.empty((config.height, config.width), dtype=object)

    for y in range(config.height):
        for x in range(config.width):
            terrain[y][x] = classify_terrain(elevation[y][x], moisture[y][x], config.ranges)
    return terrain


def generate_noise_map(
    octaves: int,
    width: int,
    height: int,
    scale: float,
    contrast_enhancement: float,
    seed: int
) -> np.ndarray:
    """Generate 2d array filled with perlin noise"""
    noise = PerlinNoise(octaves=octaves, seed=seed)
    noise_map = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            noise_map[y][x] = noise([x / scale, y / scale])
    noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
    noise_map = np.power(noise_map, contrast_enhancement)
    return noise_map


def classify_terrain(
    elevation: float,
    moisture: float,
    config: dict[TerrainType, dict[str, tuple[float, float]]]
) -> str:
    """Get a terrain for given location based on elevation and moisture."""
    candidates = set()

    for terrain, ranges in config.items():
        elev_range = ranges['elevation']
        mois_range = ranges['moisture']
        if elev_range[0] <= elevation <= elev_range[1] and mois_range[0] <= moisture <= mois_range[1]:
            candidates.add(terrain)

    if not candidates:
        raise ValueError(f'No terrain available for elevation: {elevation}, moisture: {moisture}.')

    return random.choice(tuple(candidates))


def save_map_image(terrain: np.ndarray, path: Path) -> None:
    rgb = np.zeros((terrain.shape[0], terrain.shape[1], 3))
    for name, color in COLOR_MAP.items():
        rgb[np.where(terrain == name)] = color

    plt.imshow(rgb, interpolation='nearest')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()


async def main(config: CodebornConfig) -> None:
    await init_db(config.database)
    map_config = config.generators.map
    logger = get_logger(generator='map', seed=map_config.seed)

    try:
        logger.info('Generating map.')

        terrain_map = generate_terrain(map_config)

        logger.info(f'Map image saved to "{MAP_PATH.absolute()}".')
        save_map_image(terrain_map, MAP_PATH)

        locations = []
        height, width = terrain_map.shape
        for y in range(height):
            for x in range(width):
                locations.append(Location(
                    x=x, y=y, terrain=terrain_map[y, x]
                ))

        logger.info(f'Saving {len(locations)} locations to DB.')
        await Location.bulk_create(locations)

    finally:
        await close_db()


if __name__ == '__main__':
    config = get_config()
    init_logging(config.logging)
    asyncio.run(main(config))
