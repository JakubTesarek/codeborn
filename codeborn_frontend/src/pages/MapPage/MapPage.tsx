import { useState } from 'react'
import { MapViewport } from './MapViewport'
import { MapSidebar } from './MapSidebar'
import { Tile, Terrain, GRID_SIZE } from './types'

function generateTiles(): Tile[] {
  const out: Tile[] = []
  for (let y = 0; y < GRID_SIZE; y++)
    for (let x = 0; x < GRID_SIZE; x++) {
      const r = Math.random()
      let terrain: Terrain = 'plains'
      if (r < 0.15) terrain = 'forest'
      else if (r < 0.25) terrain = 'swamp'
      else if (r < 0.3) terrain = 'village'
      out.push({ x, y, terrain })
    }
  return out
}

export function MapPage() {
  const [tiles] = useState(generateTiles)
  const [selected, setSelected] = useState<Tile | null>(null)

  return (
    <div className="flex justify-center items-start gap-6 p-4">
      <div className="flex flex-col items-center">
        <h1 className="text-xl font-semibold mb-4">Map (Scrollable Prototype)</h1>
        <MapViewport tiles={tiles} selected={selected} onSelect={setSelected} />
      </div>
      <MapSidebar tile={selected} />
    </div>
  )
}
