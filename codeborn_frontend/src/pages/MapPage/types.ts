export type Terrain = 'plains' | 'forest' | 'swamp' | 'village'

export interface Tile {
  x: number
  y: number
  terrain: Terrain
}

export const TILE_SIZE = 20
export const GRID_SIZE = 100
export const VIEW_SIZE = 50