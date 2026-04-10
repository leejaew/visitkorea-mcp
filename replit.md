# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.
Also contains a standalone Python-based MCP (Model Context Protocol) server for the Korea Tourism Organization English Open Data API.

## Artifacts

- **`artifacts/api-server`** — Node.js Express server (port 8080). Handles `/api` health routes and `/mcp` proxy to the Python MCP server. Also spawns the Python subprocess.
- **`artifacts/landing`** — React+Vite landing page (root `/`). Static single-page app showing server status, all 14 MCP tools, and connection instructions for Claude AI, Claude Desktop, and Manus AI.
- **`artifacts/mockup-sandbox`** — Component preview server (design tool, not user-facing).
- **`visitkorea-mcp/`** — Python 3.11 MCP server (port 3001). The actual MCP implementation.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)
- **Python**: 3.11 (for MCP server)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

## VisitKorea MCP Server

Located at `visitkorea-mcp/` — a Python 3.11 MCP server for the Korea Tourism Organization (한국관광공사) English Open Data API.

### Environment Variables
- `VISITKOREA_API_KEY` — URL-encoded service key from data.go.kr (stored in Replit Secrets)

### Running
```bash
cd visitkorea-mcp
python3.11 server.py          # stdio mode (Claude Desktop, Manus AI)
python3.11 server.py --sse    # SSE mode (port 3000)
python3.11 server.py --http   # Streamable HTTP mode (port 3001)
```

### Tools (14 total)
1. `search_tourism_by_area` → `areaBasedList2` (supports both new lDongRegnCd and old areaCode/cat1-3)
2. `search_tourism_by_location` → `locationBasedList2`
3. `search_tourism_by_keyword` → `searchKeyword2`
4. `search_festivals_and_events` → `searchFestival2`
5. `search_accommodations` → `searchStay2`
6. `get_tourism_common_info` → `detailCommon2`
7. `get_tourism_intro_info` → `detailIntro2`
8. `get_tourism_detail_info` → `detailInfo2`
9. `get_tourism_images` → `detailImage2` (imageYN: Y=venue photos, N=restaurant menu photos)
10. `get_sync_list` → `areaBasedSyncList2` (params: modifiedtime, showflag, oldContentid)
11. `get_legal_district_codes` → `ldongCode2` (lDongListYn: N=code lookup, Y=full list)
12. `get_classification_codes` → `lclsSystmCode2`
13. `get_area_codes` → `areaCode2` (old-style area code lookup; 17 provinces + districts)
14. `get_category_codes` → `categoryCode2` (old-style cat1/cat2/cat3 3-level hierarchy)

### Dependencies
Installed via pip: `mcp>=1.27.0`, `httpx>=0.28.0`, `uvicorn>=0.44.0`, `starlette>=1.0.0`
