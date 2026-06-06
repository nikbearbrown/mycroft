import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'

const COLORS = [
  '#3b82f6', '#22c55e', '#f59e0b', '#ef4444',
  '#8b5cf6', '#06b6d4', '#f97316', '#ec4899',
]

export default function SankeyChart({ data }) {
  const ref = useRef(null)

  useEffect(() => {
    if (!data || !data.nodes?.length || !data.links?.length) return
    const el = ref.current
    const width = el.clientWidth || 800
    const height = 420

    d3.select(el).selectAll('*').remove()

    const svg = d3.select(el)
      .append('svg')
      .attr('width', width)
      .attr('height', height)

    const sk = sankey()
      .nodeWidth(18)
      .nodePadding(14)
      .extent([[20, 20], [width - 20, height - 20]])

    const { nodes, links } = sk({
      nodes: data.nodes.map((d) => ({ ...d })),
      links: data.links.map((d) => ({ ...d })),
    })

    // Links
    svg.append('g')
      .selectAll('path')
      .data(links)
      .join('path')
      .attr('d', sankeyLinkHorizontal())
      .attr('stroke', (d) => COLORS[d.source.index % COLORS.length])
      .attr('stroke-width', (d) => Math.max(1, d.width))
      .attr('fill', 'none')
      .attr('opacity', 0.35)

    // Nodes
    svg.append('g')
      .selectAll('rect')
      .data(nodes)
      .join('rect')
      .attr('x', (d) => d.x0)
      .attr('y', (d) => d.y0)
      .attr('width', (d) => d.x1 - d.x0)
      .attr('height', (d) => Math.max(1, d.y1 - d.y0))
      .attr('fill', (d) => COLORS[d.index % COLORS.length])
      .attr('opacity', 0.9)

    // Labels
    svg.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .attr('x', (d) => (d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6))
      .attr('y', (d) => (d.y0 + d.y1) / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', (d) => (d.x0 < width / 2 ? 'start' : 'end'))
      .attr('font-size', 11)
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('fill', '#94a3b8')
      .text((d) => d.name)
  }, [data])

  if (!data?.nodes?.length) {
    return (
      <div className="flex items-center justify-center h-48 text-muted text-sm">
        No flow data. Ingest events first.
      </div>
    )
  }

  return <div ref={ref} className="w-full" style={{ minHeight: 420 }} />
}