import { Tile } from './types'

interface SidebarProps {
  tile: Tile | null
}

export function MapSidebar({ tile }: SidebarProps) {
  return (
    <aside className="w-64 border-l border-border pl-4">
      <h2 className="text-lg font-semibold mb-2">Tile Info</h2>
      {tile ? (
        <div className="text-sm space-y-1">
          <div>
            <span className="font-medium">Coordinates:</span> ({tile.x}, {tile.y})
          </div>
          <div>
            <span className="font-medium">Terrain:</span> {tile.terrain}
          </div>
        </div>
      ) : (
        <p className="text-muted-foreground text-sm">
          Click a tile to see details
        </p>
      )}
    </aside>
  )
}
