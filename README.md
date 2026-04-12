# VisitKorea MCP Server

![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/node.js-20+-339933?logo=node.js&logoColor=white)
![MCP Transport](https://img.shields.io/badge/MCP-Streamable_HTTP-8B5CF6)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source **Model Context Protocol (MCP) server** that connects AI agents — Claude, Manus AI, and any MCP-compatible client — with the **Korea Tourism Organization (KTO) General Tourism Open Data API** (`EngService2`), published on [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do).

Exposes **14 structured MCP tools** covering area search, GPS-radius search, keyword search, festivals, accommodations, detailed venue info, image galleries, sync lists, and four reference code lookup tables — all in English.

---

## Architecture

```
MCP Client (Claude / Manus AI)
        │  Streamable HTTP  POST /mcp
        ▼
Node.js / Express  (port $PORT)
  ├─ helmet          — 11 security headers
  ├─ express-rate-limit — 120 req/min per IP
  ├─ pino-http       — structured request logging (no query strings)
  └─ http-proxy-middleware → http://127.0.0.1:3001/mcp
        │
        ▼
Python / Starlette + MCP SDK  (127.0.0.1:3001, loopback only)
  ├─ utils/api_client.py  — shared httpx connection pool, response parsing
  ├─ utils/cache.py       — in-memory TTL cache (1 h static / 5 min search)
  ├─ utils/rate_limiter.py — async token bucket (10 req/min upstream)
  ├─ utils/validation.py  — input sanitisation (GPS, radius, dates)
  ├─ schemas/             — MCP Tool definitions (14 tools)
  └─ tools/               — tool handler functions
        │
        ▼
KTO EngService2 API  (apis.data.go.kr)
```

The Python server binds only to `127.0.0.1` — it is never directly reachable from outside. All external traffic goes through the Node.js proxy, which applies security headers and rate limiting before forwarding.

---

## Features

| # | MCP Tool | KTO Endpoint | Description |
|---|---|---|---|
| 1 | `search_tourism_by_area` | `areaBasedList2` | Search tourism content by province, city, or district |
| 2 | `search_tourism_by_location` | `locationBasedList2` | Find venues within a GPS radius (up to 20 km), sorted by distance |
| 3 | `search_tourism_by_keyword` | `searchKeyword2` | Full-text English keyword search across all content types |
| 4 | `search_festivals_and_events` | `searchFestival2` | Search festivals and events by date range |
| 5 | `search_accommodations` | `searchStay2` | Browse hotels, pensions, guesthouses, condominiums, and camping sites |
| 6 | `get_tourism_common_info` | `detailCommon2` | Overview record: title, address, GPS, phone, homepage, description |
| 7 | `get_tourism_intro_info` | `detailIntro2` | Type-specific intro: opening hours, fees, rest days, parking |
| 8 | `get_tourism_detail_info` | `detailInfo2` | Repeating details: room types, menu items, programme schedules |
| 9 | `get_tourism_images` | `detailImage2` | All image URLs and copyright types for a venue |
| 10 | `get_sync_list` | `areaBasedSyncList2` | Delta sync list — content modified since a given timestamp |
| 11 | `get_legal_district_codes` | `ldongCode2` | New-system province/city codes (`lDongRegnCd`, `lDongSignguCd`) |
| 12 | `get_classification_codes` | `lclsSystmCode2` | New-system 3-level classification hierarchy (`lclsSystm1/2/3`) |
| 13 | `get_area_codes` | `areaCode2` | Legacy area codes (`areaCode`, `sigunguCode`) |
| 14 | `get_category_codes` | `categoryCode2` | Legacy category hierarchy (`cat1`, `cat2`, `cat3`) |

### Dual Code System

The API supports two parallel geographic and category code systems — both are fully supported:

| System | Look up codes with | Use in |
|---|---|---|
| **New** — `lDongRegnCd`, `lDongSignguCd`, `lclsSystm1/2/3` | `get_legal_district_codes`, `get_classification_codes` | All search tools |
| **Legacy** — `areaCode`, `sigunguCode`, `cat1/2/3` | `get_area_codes`, `get_category_codes` | `search_tourism_by_area` |

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+** with **pnpm** (the project uses a pnpm workspace)
- A **KTO Open API service key** from [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do)

---

## Quickstart on Replit

1. **Fork this project** into your Replit account.
2. **Get a KTO API key** — register at [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do) and apply for the `한국관광공사_영문_관광정보서비스` dataset (approval is usually instant).
3. **Add the secret** — open the **Secrets** panel in Replit and create:

   | Secret name | Value |
   |---|---|
   | `VISITKOREA_API_KEY` | Your service key (either the URL-encoded "Encoding key" or the plain "Decoding key" — both work) |

4. **Click Run** — Replit starts the Node.js proxy, which automatically installs Python dependencies and spawns the Python MCP server.

Endpoints once running:

| Path | Description |
|---|---|
| `/` | React landing page with connector JSON and setup instructions |
| `/mcp` | MCP Streamable HTTP endpoint for AI agents |

---

## Local Development Setup

### 1. Install Node.js dependencies

```bash
pnpm install
```

### 2. Install Python dependencies

```bash
pip install -r visitkorea-mcp/requirements.txt
```

Python dependencies:

| Package | Version | Purpose |
|---|---|---|
| `mcp` | ≥ 1.27.0 | MCP SDK — server, tools, Streamable HTTP transport |
| `httpx` | ≥ 0.28.0 | Async HTTP client with connection pooling |
| `uvicorn` | ≥ 0.44.0 | ASGI server |
| `starlette` | ≥ 1.0.0 | ASGI routing and lifespan management |

### 3. Set your API key

```bash
export VISITKOREA_API_KEY="your_service_key_here"
```

### 4. Start the server

**Option A — Full stack (Node.js proxy + Python MCP):**

```bash
pnpm --filter @workspace/api-server run dev
```

The Node.js proxy starts on `$PORT` (or 8080 by default) and spawns the Python server on `127.0.0.1:3001`.

**Option B — Python only, stdio mode (Claude Desktop / local CLI):**

```bash
python3 visitkorea-mcp/main.py
```

**Option C — Python only, HTTP mode:**

```bash
python3 visitkorea-mcp/main.py --http --port 3001
```

---

## Connecting an AI Agent

### MCP Connector JSON (Claude AI / Manus AI)

Paste this into your AI agent's custom connector settings:

```json
{
  "mcpServers": {
    "visitkorea": {
      "type": "streamableHttp",
      "url": "https://<your-repl-name>.replit.app/mcp"
    }
  }
}
```

Replace the URL with your own deployed Replit project URL.

---

### Claude AI (claude.ai) — Custom Connector

| Field | Value |
|---|---|
| **Name** | `VisitKorea Tourism` |
| **Remote MCP server URL** | `https://<your-repl-name>.replit.app/mcp` |
| **OAuth Client ID** | *(leave blank)* |
| **OAuth Client Secret** | *(leave blank)* |

---

### Claude Desktop — `claude_desktop_config.json`

Runs the Python server in stdio mode (no Node.js proxy needed):

```json
{
  "mcpServers": {
    "visitkorea": {
      "command": "python3",
      "args": ["/absolute/path/to/visitkorea-mcp/main.py"],
      "env": {
        "VISITKOREA_API_KEY": "your_service_key_here"
      }
    }
  }
}
```

Replace `/absolute/path/to/` with the actual path to the cloned repository on your machine.

---

## Tool Reference

### Tool 1 — `search_tourism_by_area`

List tourism spots filtered by administrative region, content type, and/or category codes.

**Endpoint:** `GET /areaBasedList2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `numOfRows` | int | No | Results per page (default 10, max 100) |
| `pageNo` | int | No | Page number (default 1) |
| `arrange` | string | No | Sort: `A`=title, `C`=modified (default), `D`=created; `O`/`Q`/`R`=image-only variants |
| `contentTypeId` | string | No | Content type filter (see Content Types table) |
| `lDongRegnCd` | string | No | Province code — use `get_legal_district_codes` |
| `lDongSignguCd` | string | No | City/county code — requires `lDongRegnCd` |
| `lclsSystm1` | string | No | Classification level-1 code |
| `lclsSystm2` | string | No | Classification level-2 code — requires `lclsSystm1` |
| `lclsSystm3` | string | No | Classification level-3 code — requires `lclsSystm1` + `lclsSystm2` |
| `modifiedtime` | string | No | Modified-date filter (YYYYMMDD) |
| `areaCode` | string | No | Legacy province code — use `get_area_codes` |
| `sigunguCode` | string | No | Legacy district code — requires `areaCode` |
| `cat1` / `cat2` / `cat3` | string | No | Legacy category hierarchy — use `get_category_codes` |

---

### Tool 2 — `search_tourism_by_location`

Find tourism spots within a GPS radius, sorted by proximity.

**Endpoint:** `GET /locationBasedList2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `mapX` | float | **Yes** | GPS longitude, WGS84 (e.g. `126.9784` for central Seoul) |
| `mapY` | float | **Yes** | GPS latitude, WGS84 (e.g. `37.5665` for central Seoul) |
| `radius` | int | **Yes** | Search radius in metres (1–20,000) |
| `numOfRows` | int | No | Results per page (default 10) |
| `pageNo` | int | No | Page number (default 1) |
| `arrange` | string | No | Sort: `A`/`C`/`D` or image variants `O`/`Q`/`R` |
| `contentTypeId` | string | No | Content type filter |
| `lDongRegnCd` | string | No | Province code filter |
| `lDongSignguCd` | string | No | City/county code filter |
| `lclsSystm1/2/3` | string | No | Classification hierarchy filters |

---

### Tool 3 — `search_tourism_by_keyword`

Full-text keyword search across all tourism content.

**Endpoint:** `GET /searchKeyword2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `keyword` | string | **Yes** | English search term (e.g. `"Gyeongbokgung"`, `"Jeju"`, `"temple"`) |
| `numOfRows` | int | No | Results per page (default 10) |
| `pageNo` | int | No | Page number (default 1) |
| `arrange` | string | No | Sort order |
| `contentTypeId` | string | No | Content type filter |
| `lDongRegnCd` | string | No | Province code filter |
| `lDongSignguCd` | string | No | City/county code filter |
| `lclsSystm1/2/3` | string | No | Classification hierarchy filters |

---

### Tool 4 — `search_festivals_and_events`

Search festivals, performances, and cultural events by date range.

**Endpoint:** `GET /searchFestival2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `eventStartDate` | string | **Yes** | Start date in YYYYMMDD format (e.g. `"20260101"`) |
| `eventEndDate` | string | No | End date in YYYYMMDD format |
| `numOfRows` | int | No | Results per page (default 10) |
| `pageNo` | int | No | Page number (default 1) |
| `arrange` | string | No | Sort order |
| `modifiedtime` | string | No | Modified-date filter (YYYYMMDD) |
| `lDongRegnCd` | string | No | Province code filter |
| `lDongSignguCd` | string | No | City/county code filter |
| `lclsSystm1/2/3` | string | No | Classification hierarchy filters |

---

### Tool 5 — `search_accommodations`

Search hotels, pensions, guesthouses, condominiums, and camping sites.

**Endpoint:** `GET /searchStay2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `numOfRows` | int | No | Results per page (default 10) |
| `pageNo` | int | No | Page number (default 1) |
| `arrange` | string | No | Sort order |
| `modifiedtime` | string | No | Modified-date filter (YYYYMMDD) |
| `lDongRegnCd` | string | No | Province code filter |
| `lDongSignguCd` | string | No | City/county code filter |
| `lclsSystm1/2/3` | string | No | Classification hierarchy filters |

---

### Tool 6 — `get_tourism_common_info`

Common overview record for any venue: title, full address, GPS coordinates, phone number, homepage URL, content type, category codes, and description text.

**Endpoint:** `GET /detailCommon2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `contentId` | string | **Yes** | Content ID from any search result |
| `defaultYN` | string | No | Include default fields (`Y`/`N`, default `Y`) |
| `firstImageYN` | string | No | Include representative image URL (`Y`/`N`, default `Y`) |
| `areacodeYN` | string | No | Include area codes (`Y`/`N`, default `Y`) |
| `catcodeYN` | string | No | Include category codes (`Y`/`N`, default `Y`) |
| `addrinfoYN` | string | No | Include full address (`Y`/`N`, default `Y`) |
| `mapinfoYN` | string | No | Include GPS coordinates (`Y`/`N`, default `Y`) |
| `overviewYN` | string | No | Include overview description (`Y`/`N`, default `Y`) |

---

### Tool 7 — `get_tourism_intro_info`

Type-specific introductory details. Fields vary by content type: opening hours, admission fees, rest days, parking info, facility descriptions, age suitability.

**Endpoint:** `GET /detailIntro2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `contentId` | string | **Yes** | Content ID from any search result |
| `contentTypeId` | string | **Yes** | Must match the item's type (see Content Types table) |

---

### Tool 8 — `get_tourism_detail_info`

Repeating structured sub-records that vary by content type: room types and rates for accommodations, menu items for restaurants, programme schedules for events.

**Endpoint:** `GET /detailInfo2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `contentId` | string | **Yes** | Content ID from any search result |
| `contentTypeId` | string | **Yes** | Must match the item's type (see Content Types table) |

---

### Tool 9 — `get_tourism_images`

All image URLs for a venue, including the copyright type for each image.

**Endpoint:** `GET /detailImage2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `contentId` | string | **Yes** | Content ID from any search result |
| `imageYN` | string | No | `Y` = venue/exterior photos (default); `N` = food menu images (restaurants only) |

---

### Tool 10 — `get_sync_list`

Delta sync list — retrieve content items that were added or modified after a given timestamp. Useful for maintaining a local cached copy of KTO data.

**Endpoint:** `GET /areaBasedSyncList2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `modifiedtime` | string | No | Return items modified on/after this date (YYYYMMDD). Omit for full list. |
| `showflag` | string | No | `1` = displayed content only; `0` = hidden only; omit for all |
| `contentTypeId` | string | No | Content type filter |
| `oldContentid` | string | No | Look up the current content ID for a legacy content ID |
| `lDongRegnCd` | string | No | Province code filter |
| `lDongSignguCd` | string | No | City/county code filter |
| `lclsSystm1/2/3` | string | No | Classification hierarchy filters |

---

### Tool 11 — `get_legal_district_codes`

Look up the new-system legal district codes used by `lDongRegnCd` and `lDongSignguCd` parameters. Response cached for 1 hour.

**Endpoint:** `GET /ldongCode2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `lDongRegnCd` | string | No | Province code. Omit to get all 17 provinces; pass to get its city/county codes. |
| `lDongListYn` | string | No | `Y` = return full flat list; `N` = paginated (default) |
| `numOfRows` | int | No | Results per page (default 100) |

---

### Tool 12 — `get_classification_codes`

Browse the new-system 3-level classification hierarchy. Response cached for 1 hour.

**Endpoint:** `GET /lclsSystmCode2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `lclsSystm1` | string | No | Level-1 code (e.g. `AC`, `EV`). Omit to get all level-1 codes. |
| `lclsSystm2` | string | No | Level-2 code — requires `lclsSystm1` |
| `lclsSystm3` | string | No | Level-3 code — requires `lclsSystm1` + `lclsSystm2` |
| `lclsSystmListYn` | string | No | `Y` = full flat list; `N` = paginated (default) |

---

### Tool 13 — `get_area_codes`

Look up the legacy-system area codes (`areaCode`, `sigunguCode`). Response cached for 1 hour.

**Endpoint:** `GET /areaCode2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `areaCode` | string | No | Province code. Omit to get all 17 provinces; pass to get its districts. |
| `numOfRows` | int | No | Results per page (default 50) |

---

### Tool 14 — `get_category_codes`

Browse the legacy 3-level category hierarchy (`cat1`/`cat2`/`cat3`). Response cached for 1 hour.

**Endpoint:** `GET /categoryCode2`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `cat1` | string | No | Level-1 code (e.g. `A01`=Nature, `A02`=Culture). Omit for all. |
| `cat2` | string | No | Level-2 code — requires `cat1` |
| `contentTypeId` | string | No | Filter categories to a specific content type |
| `numOfRows` | int | No | Results per page (default 100) |

---

## Reference Tables

### Content Types (`contentTypeId`)

| ID | English | Korean |
|---|---|---|
| `75` | Leisure / Sports | 레포츠 |
| `76` | Tourist Attraction | 관광지 |
| `78` | Cultural Facility | 문화시설 |
| `79` | Shopping | 쇼핑 |
| `80` | Accommodation | 숙박 |
| `82` | Restaurant / Food | 음식점 |
| `85` | Festival / Performance / Event | 축제공연행사 |

### Province Codes (`lDongRegnCd`)

| Code | Province / City |
|---|---|
| `11` | Seoul (서울) |
| `26` | Busan (부산) |
| `27` | Daegu (대구) |
| `28` | Incheon (인천) |
| `29` | Gwangju (광주) |
| `30` | Daejeon (대전) |
| `31` | Ulsan (울산) |
| `36` | Sejong (세종) |
| `41` | Gyeonggi (경기) |
| `42` | Gangwon (강원) |
| `43` | Chungbuk (충북) |
| `44` | Chungnam (충남) |
| `45` | Jeonbuk (전북) |
| `46` | Jeonnam (전남) |
| `47` | Gyeongbuk (경북) |
| `48` | Gyeongnam (경남) |
| `50` | Jeju Island (제주) |

### Classification Codes (`lclsSystm1`)

| Code | Category |
|---|---|
| `AC` | Accommodation |
| `EV` | Festivals / Performances / Events |
| `EX` | Experience Tourism |
| `FO` | Food & Dining |
| `LC` | Leisure & Sports |
| `SH` | Shopping |
| `TR` | Transportation |
| `VE` | Culture / Arts / History |

---

## Project Structure

```
visitkorea-mcp/          Python MCP server package
├── main.py              Entry point — argparse, stdio + Streamable HTTP transports
├── config.py            Constants (BASE_URL, content type map)
├── requirements.txt     Python dependencies
├── .env.example         Local setup reference (do not commit real keys)
├── utils/
│   ├── api_client.py    Shared httpx client, API key loading, response parsing
│   ├── cache.py         TTL response cache (1 h for reference data, 5 min for search)
│   ├── rate_limiter.py  Async token bucket (10 req/min upstream, burst 5)
│   └── validation.py    Input validators (GPS bounds, radius, date format, pagination)
├── schemas/             MCP Tool schema definitions (what tools look like to clients)
│   ├── search_schema.py
│   ├── events_schema.py
│   ├── accommodations_schema.py
│   ├── detail_schema.py
│   ├── sync_schema.py
│   └── codes_schema.py
└── tools/               Tool handlers (what happens when tools are called)
    ├── __init__.py      register_all_tools() — wires all handlers into the MCP Server
    ├── search.py        search_tourism_by_area / by_location / by_keyword
    ├── events.py        search_festivals_and_events
    ├── accommodations.py search_accommodations
    ├── detail.py        get_tourism_common / intro / detail_info + images
    ├── sync.py          get_sync_list
    └── codes.py         get_legal_district / classification / area / category_codes

artifacts/
├── api-server/          Node.js reverse proxy
│   └── src/
│       ├── app.ts       Express — helmet, rate limiting, pino-http, /mcp proxy
│       └── index.ts     Spawns Python server on port 3001, starts Express on $PORT
└── landing/             React landing page (Vite)
    └── src/App.tsx      Connector JSON, Claude/Manus setup, tool list
```

---

## Security & Performance

| Layer | Feature | Detail |
|---|---|---|
| Node.js | Security headers | `helmet` — sets 11 HTTP security headers on every response |
| Node.js | Rate limiting | `express-rate-limit` — 120 req/min per IP on `/mcp`; loopback exempt |
| Node.js | Structured logging | `pino-http` — query strings stripped from logs (no API key leakage) |
| Node.js | Proxy timeout | 35 s — slightly above Python's 30 s httpx timeout |
| Python | Loopback binding | Server binds `127.0.0.1` only — not reachable directly from outside |
| Python | Connection pool | Shared `httpx.AsyncClient` — TCP keep-alive reused across all tool calls |
| Python | Response cache | In-memory TTL cache — 1 h for static reference endpoints, 5 min for search |
| Python | Token bucket | 10 upstream req/min (burst 5) — protects the 1,000 req/day KTO quota |
| Python | Retry logic | 3 attempts with exponential back-off on 5xx / network errors |
| Python | API key masking | Raw key redacted from all error messages and log output |
| Python | Input validation | GPS bounding box, radius [1–20,000 m], date YYYYMMDD, pagination clamp |
| Python | Access log off | `uvicorn access_log=False` — request URLs (containing `serviceKey`) never logged |

---

## API Key Registration

1. Visit [https://www.data.go.kr/data/15101753/openapi.do](https://www.data.go.kr/data/15101753/openapi.do)
2. Sign in or create a 공공데이터포털 account
3. Click **활용신청** (Request API access)
4. After approval (usually instant), go to My Page and copy your **일반 인증키 (Encoding)** service key
5. Add it to Replit Secrets as `VISITKOREA_API_KEY`

> Both the URL-encoded "Encoding key" and the plain "Decoding key" work. The server normalises whichever form you provide using `urllib.parse.unquote()` at startup.

> Never commit the key to any source file. Always store it via the Replit Secrets panel or a `.env` file that is listed in `.gitignore`.

---

## Contributing

Contributions are welcome. Please open an issue before submitting a pull request. Ensure all changes are tested against the live API and that no API keys are committed to the repository.

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

Tourism data provided by the **Korea Tourism Organization (KTO)** via the 공공데이터포털 open API platform (`data.go.kr`). Data usage is subject to KTO terms — attribution is required for `Type1` content; `Type3` content additionally prohibits modification.
