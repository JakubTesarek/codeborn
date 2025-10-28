import { useRef, useState, useEffect } from 'react'
import { Tile, Terrain, TILE_SIZE, GRID_SIZE, VIEW_SIZE } from './types'

interface MapViewportProps {
  tiles: Tile[]
  onSelect: (tile: Tile | null) => void
  selected: Tile | null
}

export function MapViewport({ tiles, onSelect, selected }: MapViewportProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [hovered, setHovered] = useState<Tile | null>(null)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const isDragging = useRef(false)
  const dragStart = useRef({ x: 0, y: 0 })
  const offsetStart = useRef({ x: 0, y: 0 })

  const MARGIN = 20 // px padding for coordinate labels

  const colors: Record<Terrain, string> = {
    plains: '#a8d08d',
    forest: '#38761d',
    swamp: '#6fa8dc',
    village: '#c27ba0',
  }

  // --- draw everything ---
  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // shift drawing by margin
    ctx.save()
    ctx.translate(MARGIN, MARGIN)

    // draw tiles
    for (let y = 0; y < VIEW_SIZE; y++) {
      for (let x = 0; x < VIEW_SIZE; x++) {
        const worldX = x + offset.x
        const worldY = y + offset.y
        const tile = tiles.find(t => t.x === worldX && t.y === worldY)
        if (!tile) continue

        ctx.fillStyle = colors[tile.terrain]
        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        ctx.strokeStyle = '#ccc'
        ctx.strokeRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
      }
    }

    const drawOutline = (tile: Tile | null, color: string) => {
      if (!tile) return
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(
        (tile.x - offset.x) * TILE_SIZE,
        (tile.y - offset.y) * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE
      )
    }

    drawOutline(hovered, 'yellow')
    drawOutline(selected, 'red')

    // draw coordinate labels (outside map)
    ctx.restore() // remove translate for clean label placement
    ctx.font = '10px sans-serif'
    ctx.fillStyle = '#555'

    // top X-axis labels
    ctx.textAlign = 'center'
    ctx.textBaseline = 'bottom'
    for (let x = 0; x < VIEW_SIZE; x++) {
      const worldX = x + offset.x
      if (worldX % 10 === 0) {
        const labelX = MARGIN + x * TILE_SIZE + TILE_SIZE / 2
        ctx.fillText(String(worldX), labelX, MARGIN - 4)
      }
    }

    // left Y-axis labels
    ctx.textAlign = 'right'
    ctx.textBaseline = 'middle'
    for (let y = 0; y < VIEW_SIZE; y++) {
      const worldY = y + offset.y
      if (worldY % 10 === 0) {
        const labelY = MARGIN + y * TILE_SIZE + TILE_SIZE / 2
        ctx.fillText(String(worldY), MARGIN - 4, labelY)
      }
    }
  }, [tiles, hovered, selected, offset])

  // --- helper to map mouse position to tile ---
  const getTile = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const localX = e.clientX - rect.left - MARGIN
    const localY = e.clientY - rect.top - MARGIN
    if (localX < 0 || localY < 0) return null
    const x = Math.floor(localX / TILE_SIZE) + offset.x
    const y = Math.floor(localY / TILE_SIZE) + offset.y
    return tiles.find(t => t.x === x && t.y === y) || null
  }

  // --- mouse handlers ---
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    isDragging.current = true
    dragStart.current = { x: e.clientX, y: e.clientY }
    offsetStart.current = offset
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging.current) {
      const dx = Math.floor((dragStart.current.x - e.clientX) / TILE_SIZE)
      const dy = Math.floor((dragStart.current.y - e.clientY) / TILE_SIZE)
      setOffset({
        x: Math.min(Math.max(offsetStart.current.x + dx, 0), GRID_SIZE - VIEW_SIZE),
        y: Math.min(Math.max(offsetStart.current.y + dy, 0), GRID_SIZE - VIEW_SIZE),
      })
      return
    }
    setHovered(getTile(e))
  }

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const moved = Math.hypot(
      dragStart.current.x - e.clientX,
      dragStart.current.y - e.clientY
    )
    if (moved < 5) onSelect(getTile(e))
    isDragging.current = false
  }

  // --- render canvas ---
  return (
  <canvas
    ref={canvasRef}
    width={VIEW_SIZE * TILE_SIZE + MARGIN + 2}
    height={VIEW_SIZE * TILE_SIZE + MARGIN + 2}
    onMouseDown={handleMouseDown}
    onMouseUp={handleMouseUp}
    onMouseMove={handleMouseMove}
    onMouseLeave={() => (isDragging.current = false)}
    className="cursor-grab active:cursor-grabbing bg-background"
  />
)
}
