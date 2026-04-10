# VisitKorea MCP Server

![Python](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)
![MCP Transport](https://img.shields.io/badge/MCP-Streamable_HTTP-8B5CF6)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An MCP (Model Context Protocol) server that wraps the **Korea Tourism Organization (KTO) General Tourism Open API** (`EngService2`), published on [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do), exposing 14 structured tools that AI agents — including Claude and Manus AI — can call directly via Streamable HTTP.

## Features

- **Area-based search** — list tourism venues by province, city, or district
- **Location-based search** — find venues within a GPS radius (up to 20 km), sorted by distance
- **Keyword search** — full-text English keyword search across all tourism content types
- **Festival and event search** — discover events by date range, with optional region filter
- **Accommodation search** — browse hotels, pensions, guesthouses, condominiums, and camping sites
- **7 content type filters** — Tourist Attraction, Cultural Facility, Accommodation, Restaurant, Shopping, Leisure/Sports, Festival/Event
- **Sync list** — full dataset synchronisation list for building and maintaining local caches
- **Detail records** — common info, type-specific intro info, repeating structured data, and image galleries
- **Dual code system** — both new legal dong codes (`lDongRegnCd`) and legacy area codes (`areaCode`) are supported
- **14 MCP tools** — one per API operation, with full parameter documentation

## Prerequisites

- Python 3.11+
- A KTO Open API key from [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do) (Service ID: `15101753`)
- Replit account (for deployment)

## Installation & Replit Secrets Setup

1. **Clone or fork this repository** into your Replit account.
2. **Obtain your API key** by registering at [https://www.data.go.kr/data/15101753/openapi.do](https://www.data.go.kr/data/15101753/openapi.do).
3. **Set the Replit Secret** — open the Secrets tab in Replit and add:

   | Secret name | Description |
   |-------------|-------------|
   | `VISITKOREA_API_KEY` | URL-encoded service key from data.go.kr — used as `serviceKey` in all API requests |

4. **Install dependencies** (Replit handles this automatically on first run):
   ```bash
   pnpm install
   pip install -r visitkorea-mcp/requirements.txt
   ```
5. **Run the server** — click the Run button in Replit or:
   ```bash
   pnpm --filter @workspace/api-server run dev
   ```

The Node.js proxy starts on port `8080`. It spawns the Python MCP server on port `3001`.
- Landing page: `http://localhost:8080/`
- Streamable HTTP endpoint: `http://localhost:8080/mcp`

## MCP Connector JSON

Paste this into your AI agent's custom connector settings (Claude AI or Manus AI):

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

### Claude AI (claude.ai) — Custom Connector

| Field | Value |
|-------|-------|
| **Name** | `VisitKorea Tourism` |
| **Remote MCP server URL** | `https://<your-repl-name>.replit.app/mcp` |
| **OAuth Client ID** | *(leave blank)* |
| **OAuth Client Secret** | *(leave blank)* |

### Claude Desktop — `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "visitkorea": {
      "command": "python3",
      "args": ["/absolute/path/to/visitkorea-mcp/server.py"],
      "env": {
        "VISITKOREA_API_KEY": "your_url_encoded_service_key_here"
      }
    }
  }
}
```

## Tool Reference

### Tool 1 — `search_tourism_by_area`

List tourism spots filtered by administrative region, content type, and/or category codes.

**Endpoint:** `GET /areaBasedList2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `numOfRows` | int | Optional | Results per page (default: 10, max: 100) |
| `pageNo` | int | Optional | Page number (default: 1) |
| `arrange` | string | Optional | Sort: A=title, C=modified, D=created; O/Q/R=image-only variants |
| `contentTypeId` | string | Optional | Content type ID (see Content Types table) |
| `lDongRegnCd` | string | Optional | Province/city code |
| `lDongSignguCd` | string | Optional | District code (requires `lDongRegnCd`) |
| `lclsSystm1` | string | Optional | Classification level-1 code |
| `areaCode` | string | Optional | Legacy province code (alternative to `lDongRegnCd`) |
| `sigunguCode` | string | Optional | Legacy district code (requires `areaCode`) |
| `cat1` / `cat2` / `cat3` | string | Optional | Legacy category hierarchy codes |

---

### Tool 2 — `search_tourism_by_location`

Find tourism spots within a GPS radius, sorted by proximity.

**Endpoint:** `GET /locationBasedList2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mapX` | float | **Required** | GPS longitude (WGS84) |
| `mapY` | float | **Required** | GPS latitude (WGS84) |
| `radius` | int | **Required** | Search radius in metres (max 20,000) |
| `arrange` | string | Optional | Sort: A/C/D or image variants O/Q/R |
| `contentTypeId` | string | Optional | Content type filter |

---

### Tool 3 — `search_tourism_by_keyword`

Full-text keyword search across all tourism content.

**Endpoint:** `GET /searchKeyword2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keyword` | string | **Required** | Search term in English |
| `contentTypeId` | string | Optional | Content type filter |
| `lDongRegnCd` | string | Optional | Province/city code filter |

---

### Tool 4 — `search_festivals_and_events`

Search Korean festivals, performances, and cultural events by date range.

**Endpoint:** `GET /searchFestival2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `eventStartDate` | string | **Required** | Start date in YYYYMMDD format |
| `eventEndDate` | string | Optional | End date in YYYYMMDD format |
| `lDongRegnCd` | string | Optional | Province/city code filter |

---

### Tool 5 — `search_accommodations`

Search hotels, pensions, hostels, condominiums, and camping sites.

**Endpoint:** `GET /searchStay2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lDongRegnCd` | string | Optional | Province/city code |
| `lDongSignguCd` | string | Optional | District code (requires `lDongRegnCd`) |
| `numOfRows` | int | Optional | Results per page |

---

### Tool 6 — `get_tourism_common_info`

Fetch complete common detail record for a venue: title, address, GPS, phone, homepage, overview.

**Endpoint:** `GET /detailCommon2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contentId` | string | **Required** | Content ID from any search result |

---

### Tool 7 — `get_tourism_intro_info`

Fetch type-specific introductory details. Fields vary by `contentTypeId`.

**Endpoint:** `GET /detailIntro2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contentId` | string | **Required** | Content ID |
| `contentTypeId` | string | **Required** | Must match the venue's category |

For tourist attractions (type `76`): `accomcount`, `chkcreditcard`, `expagerange`, `infocenter`, `opendate`, `parking`, `restdate`, `useseason`, `usetime`.

---

### Tool 8 — `get_tourism_detail_info`

Fetch repeating structured sub-records: room types for hotels, menu items for restaurants, programme schedules for events.

**Endpoint:** `GET /detailInfo2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contentId` | string | **Required** | Content ID |
| `contentTypeId` | string | **Required** | Must match the venue's category |

---

### Tool 9 — `get_tourism_images`

Retrieve all image URLs and copyright types for a venue.

**Endpoint:** `GET /detailImage2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contentId` | string | **Required** | Content ID |
| `imageYN` | string | Optional | `Y` = venue photos (default); `N` = food menu images (restaurants only) |

---

### Tool 10 — `get_sync_list`

Retrieve content items updated since a given timestamp — for local cache synchronisation.

**Endpoint:** `GET /areaBasedSyncList2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `modifiedtime` | string | Optional | ISO timestamp filter (e.g. `"20260101000000"`) |
| `contentTypeId` | string | Optional | Content type filter |
| `areaCode` | string | Optional | Province filter |

---

### Tool 11 — `get_legal_district_codes`

Retrieve legal administrative district codes (`lDongRegnCd`, `lDongSignguCd`) for new-system filtering.

**Endpoint:** `GET /ldongCode2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `areaCode` | string | Optional | Leave empty for all provinces; set to a code for its districts |

---

### Tool 12 — `get_classification_codes`

Browse the new 3-level classification hierarchy (AC=Accommodation, EV=Events, FO=Food, VE=Culture, etc.).

**Endpoint:** `GET /lclsSystmCode2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lclsSystm1` | string | Optional | Level-1 code (e.g. `AC`, `VE`, `FO`) |
| `lclsSystm2` | string | Optional | Level-2 code (requires `lclsSystm1`) |
| `lclsSystmListYn` | string | Optional | `Y` = return full list |

---

### Tool 13 — `get_area_codes`

Look up the legacy area codes (17 provinces) and their district codes (`sigunguCode`).

**Endpoint:** `GET /areaCode2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `areaCode` | string | Optional | Leave empty for province list; set to get districts |

---

### Tool 14 — `get_category_codes`

Browse the legacy 3-level category hierarchy (`cat1`/`cat2`/`cat3`) for content category filtering.

**Endpoint:** `GET /categoryCode2`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cat1` | string | Optional | Top-level code (e.g. `A01`=Nature, `A02`=Culture) |
| `cat2` | string | Optional | Second-level code (requires `cat1`) |
| `contentTypeId` | string | Optional | Filter category codes to a content type |

---

## Content Type Reference

| ID | Category (English) | Category (Korean) |
|----|--------------------|-------------------|
| `75` | Leisure / Sports | 레포츠 |
| `76` | Tourist Attraction | 관광지 |
| `78` | Cultural Facility | 문화시설 |
| `79` | Shopping | 쇼핑 |
| `80` | Accommodation | 숙박 |
| `82` | Restaurant / Food | 음식점 |
| `85` | Festival / Performance / Event | 축제공연행사 |

## Province Code Reference (`lDongRegnCd`)

| Code | Province / City |
|------|----------------|
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

## Classification System Codes (`lclsSystm1`)

| Code | Category |
|------|---------|
| `AC` | Accommodation |
| `EV` | Festivals / Performances / Events |
| `EX` | Experience Tourism |
| `FO` | Food & Dining |
| `LC` | Leisure & Sports |
| `SH` | Shopping |
| `TR` | Transportation |
| `VE` | Culture / Arts / History |

## API Key Registration

1. Visit [https://www.data.go.kr/data/15101753/openapi.do](https://www.data.go.kr/data/15101753/openapi.do)
2. Sign in or create a 공공데이터포털 account
3. Click **활용신청** (Request API access) on the dataset page
4. After approval (usually instant), copy your **일반 인증키 (Encoding)** URL-encoded service key from My Page
5. Add it to Replit Secrets as `VISITKOREA_API_KEY`

> Do not commit the key to any source file. Always store it via the Replit Secrets panel.

## Project Structure

```
visitkorea-mcp/
├── visitkorea-mcp/
│   ├── server.py          # Python MCP server — 14 tools, stdio + Streamable HTTP
│   └── requirements.txt   # Python dependencies
├── artifacts/
│   ├── api-server/
│   │   ├── src/
│   │   │   ├── app.ts     # Express app — MCP proxy middleware (/mcp)
│   │   │   ├── index.ts   # Entry point — spawns Python server, starts Express
│   │   │   └── routes/    # /api/config, /api/health
│   │   ├── build.mjs      # esbuild bundler config
│   │   └── package.json
│   └── landing/
│       └── src/
│           ├── App.tsx              # React landing page
│           └── MANUS_INSTRUCTIONS.md  # Manus AI usage instructions
├── pnpm-workspace.yaml
└── README.md
```

## Contributing

Contributions are welcome. Please open an issue before submitting a pull request. Ensure all changes are tested against the live API and that no API keys are committed to the repository.

## License

MIT License — see [LICENSE](LICENSE) for full text.

Tourism data provided by the **Korea Tourism Organization (KTO)** via the 공공데이터포털 open API platform (`data.go.kr`). Data usage is subject to KTO terms — attribution is required for `Type1` content; `Type3` content additionally prohibits modification.
