# VisitKorea MCP Server

A Python-based **Model Context Protocol (MCP) server** that connects AI agents — such as Claude and Manus AI — with the **Korea Tourism Organization English Open Data API** (`data.go.kr`).

This server enables AI agents to search for Korean tourism attractions, accommodations, restaurants, events, festivals, and more — all in English.

---

## Features

| MCP Tool | API Endpoint | Description |
|---|---|---|
| `search_tourism_by_area` | `areaBasedList2` | Search tourism content by province/city |
| `search_tourism_by_location` | `locationBasedList2` | Search by GPS coordinates within a radius |
| `search_tourism_by_keyword` | `searchKeyword2` | Full-text keyword search |
| `search_festivals_and_events` | `searchFestival2` | Search festivals and events by date range |
| `search_accommodations` | `searchStay2` | Search hotels, pensions, hostels, etc. |
| `get_tourism_common_info` | `detailCommon2` | Get overview info by content ID |
| `get_tourism_intro_info` | `detailIntro2` | Get type-specific detail info (hours, fees, etc.) |
| `get_tourism_detail_info` | `detailInfo2` | Get repeating details (room types, menu items, etc.) |
| `get_tourism_images` | `detailImage2` | Get all images for a tourism content item |
| `get_sync_list` | `areaBasedSyncList2` | Get recently modified content (for sync) |
| `get_legal_district_codes` | `ldongCode2` | Look up province and city/county codes (new legal dong system) |
| `get_classification_codes` | `lclsSystmCode2` | Look up new classification hierarchy codes (lclsSystm1/2/3) |
| `get_area_codes` | `areaCode2` | Look up old-style area codes (areaCode/sigunguCode system) |
| `get_category_codes` | `categoryCode2` | Look up old-style category codes (cat1/cat2/cat3 hierarchy) |

### Dual Code System

The API supports **two parallel geographic and category code systems**:

| System | Tools to look up codes | Used in |
|---|---|---|
| **New system** — legal dong codes (`lDongRegnCd`, `lDongSignguCd`, `lclsSystm1/2/3`) | `get_legal_district_codes`, `get_classification_codes` | All search tools |
| **Old system** — area codes (`areaCode`, `sigunguCode`, `cat1`, `cat2`, `cat3`) | `get_area_codes`, `get_category_codes` | `search_tourism_by_area` |

Both systems work. The new legal dong code system is recommended for precise filtering.

---

## Prerequisites

- **Python 3.11+**
- A **Korea Tourism Organization API key** from [data.go.kr](https://data.go.kr/)
  - Register at `https://data.go.kr/` and apply for the `한국관광공사_영문_관광정보서비스` API
  - Your URL-encoded service key will be available in your application page immediately after approval

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

Set the `VISITKOREA_API_KEY` environment variable to your URL-encoded service key from data.go.kr:

```bash
export VISITKOREA_API_KEY="your_url_encoded_service_key_here"
```

> **Note:** If you are running this server on Replit, the `VISITKOREA_API_KEY` secret is already configured via Replit Secrets and will be automatically available as an environment variable.

---

## Running the Server

### stdio mode (default) — for Claude Desktop and local use

```bash
python3 server.py
```

### Streamable HTTP mode — for remote/web-based MCP clients

```bash
python3 server.py --http --port 3001
```

Server available at: `http://localhost:3001/mcp`

---

## MCP Client Configuration

### Claude Desktop (`claude_desktop_config.json`)

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

> Replace `/absolute/path/to/visitkorea-mcp/server.py` with the actual path on your system.

---

### Manus AI — Streamable HTTP (run server first with `--http`)

```json
{
  "mcpServers": {
    "visitkorea": {
      "type": "streamableHttp",
      "url": "http://localhost:3001/mcp"
    }
  }
}
```

> To connect to the hosted Replit deployment instead, use `https://<your-repl-name>.replit.app/mcp` as the URL.

---

## Tourism Content Types

| ID | Type |
|---|---|
| 75 | Leisure / Sports (레포츠) |
| 76 | Tourist Attraction (관광지) |
| 78 | Cultural Facility (문화시설) |
| 79 | Shopping (쇼핑) |
| 80 | Accommodation (숙박) |
| 82 | Restaurant / Food (음식점) |
| 85 | Festival / Performance / Event (축제공연행사) |

## Province Codes (lDongRegnCd)

| Code | Province |
|---|---|
| 11 | Seoul (서울) |
| 26 | Busan (부산) |
| 27 | Daegu (대구) |
| 28 | Incheon (인천) |
| 29 | Gwangju (광주) |
| 30 | Daejeon (대전) |
| 31 | Ulsan (울산) |
| 36 | Sejong (세종) |
| 41 | Gyeonggi (경기) |
| 42 | Gangwon (강원) |
| 43 | Chungbuk (충북) |
| 44 | Chungnam (충남) |
| 45 | Jeonbuk (전북) |
| 46 | Jeonnam (전남) |
| 47 | Gyeongbuk (경북) |
| 48 | Gyeongnam (경남) |
| 50 | Jeju (제주) |

## Classification System Codes (lclsSystm1)

| Code | Category |
|---|---|
| AC | Accommodation |
| EV | Festivals / Performances / Events |
| EX | Experience Tourism |
| FO | Food & Dining |
| LC | Leisure & Sports |
| SH | Shopping |
| TR | Transportation |
| VE | Culture / Arts / History |

---

## API Reference

This server wraps the **한국관광공사 영문 관광정보서비스 v4.4** API.

- API Provider: Korea Tourism Organization (한국관광공사)
- API Portal: [https://data.go.kr/](https://data.go.kr/)
- Base URL: `https://apis.data.go.kr/B551011/EngService2/`

### Operations implemented

| # | API Endpoint | MCP Tool |
|---|---|---|
| 1 | `areaBasedList2` | `search_tourism_by_area` |
| 2 | `locationBasedList2` | `search_tourism_by_location` |
| 3 | `searchKeyword2` | `search_tourism_by_keyword` |
| 4 | `searchFestival2` | `search_festivals_and_events` |
| 5 | `searchStay2` | `search_accommodations` |
| 6 | `detailCommon2` | `get_tourism_common_info` |
| 7 | `detailIntro2` | `get_tourism_intro_info` |
| 8 | `detailInfo2` | `get_tourism_detail_info` |
| 9 | `detailImage2` | `get_tourism_images` |
| 10 | `areaBasedSyncList2` | `get_sync_list` |
| 11 | `ldongCode2` | `get_legal_district_codes` |
| 12 | `lclsSystmCode2` | `get_classification_codes` |
| 13 | `areaCode2` | `get_area_codes` |
| 14 | `categoryCode2` | `get_category_codes` |
