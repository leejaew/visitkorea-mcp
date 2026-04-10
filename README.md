# VisitKorea MCP Server

An open-source [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects AI agents — including Claude Desktop and Manus AI — to the **Korea Tourism Organization (KTO) English Open Data API**. Ask any MCP-compatible AI about Korean tourist attractions, restaurants, accommodations, festivals, and more, in English.

**API Data Source:** [Korea Tourism Organization English Open API](https://www.data.go.kr/data/15101753/openapi.do)
> This is also where you apply for and obtain your API key.

---

## Architecture

```
AI Agent (Claude / Manus AI)
        │  MCP over HTTP (Streamable HTTP)
        ▼
Node.js Express Proxy  (port 8080, path /mcp)
        │  localhost:3001
        ▼
Python MCP Server  (Starlette + uvicorn, port 3001)
        │  HTTPS
        ▼
Korea Tourism Organization Open API
(apis.data.go.kr/B551011/EngService2)
```

The Node.js server acts as the public-facing entry point (handling Replit's routing and deployment lifecycle). It spawns the Python MCP server as a subprocess and proxies all `/mcp` requests to it.

---

## Features

### 14 MCP Tools

| Tool | Description |
|------|-------------|
| `search_tourism_by_area` | Search attractions, restaurants, accommodations, shopping, cultural facilities, leisure spots, and festivals by province or district |
| `search_tourism_by_location` | Find tourism spots near a GPS coordinate within a specified radius — ideal for "things to do near me" queries |
| `search_tourism_by_keyword` | Full-text keyword search across all content types in English |
| `search_festivals_and_events` | Discover Korean festivals, performances, and events by date range |
| `search_accommodations` | Browse hotels, pensions, hostels, condominiums, and camping sites |
| `get_tourism_common_info` | Retrieve title, address, GPS, phone, homepage, and overview for any content item by ID |
| `get_tourism_intro_info` | Get type-specific details: heritage info for attractions, check-in/out for hotels, menu specialties for restaurants, etc. |
| `get_tourism_detail_info` | Get repeating sub-data: room types with pricing for hotels, menu items for restaurants, program schedules for events |
| `get_tourism_images` | Fetch all photo URLs (original + thumbnail) associated with a content item |
| `get_sync_list` | List content items created or modified since a given date — useful for keeping local databases in sync |
| `get_legal_district_codes` | Look up province and city/county codes (법정동) used to filter search results |
| `get_classification_codes` | Browse the new 3-level classification hierarchy (AC=Accommodation, EV=Events, FO=Food, VE=Culture, etc.) |
| `get_area_codes` | Look up the legacy area codes (17 provinces) used by older API parameters |
| `get_category_codes` | Browse the legacy 3-level category hierarchy (A01=Nature, A02=Culture, A05=Cuisine, etc.) |

### Content Types

| ID | Type |
|----|------|
| 75 | Leisure / Sports |
| 76 | Tourist Attraction |
| 78 | Cultural Facility |
| 79 | Shopping |
| 80 | Accommodation |
| 82 | Restaurant / Food |
| 85 | Festival / Performance / Event |

---

## Prerequisites

- A **Korea Tourism Organization API key** from [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do)
  - Register for a free account, apply for the "영문 관광정보 서비스" (English Tourism Information Service), and copy the URL-encoded service key from your application.
- A [Replit](https://replit.com) account (free tier works)

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/leejaew/custom-visitkorea-mcp.git
cd custom-visitkorea-mcp
```

### 2. Install Node.js dependencies

```bash
npm install -g pnpm
pnpm install
```

### 3. Install Python dependencies

```bash
pip install -r visitkorea-mcp/requirements.txt
```

### 4. Set the API key environment variable

```bash
export VISITKOREA_API_KEY="your_url_encoded_service_key_here"
```

> The service key from data.go.kr is already URL-encoded. Copy it exactly as shown on your application page.

### 5. Run the Python MCP server directly (stdio mode — for Claude Desktop)

```bash
python3 visitkorea-mcp/server.py
```

### 6. Run the Python MCP server in HTTP mode (for web-based clients)

```bash
python3 visitkorea-mcp/server.py --http --port 3001
```

The server will be available at `http://localhost:3001/mcp`.

---

## Connecting to Claude AI (claude.ai)

After deploying your own instance to Replit, add a custom connector directly from the claude.ai web interface:

1. Go to [claude.ai](https://claude.ai) → **Settings** → **Connectors** → **Add custom connector**
2. Fill in the fields as follows:

| Field | Value |
|-------|-------|
| **Name** | `VisitKorea Tourism` |
| **Remote MCP server URL** | `https://<your-repl-name>.replit.app/mcp` |
| **OAuth Client ID** | *(leave blank)* |
| **OAuth Client Secret** | *(leave blank)* |

3. Click **Add**.

> No OAuth credentials are needed — the `VISITKOREA_API_KEY` is stored server-side and never exposed to the client.

---

## Connecting to Claude Desktop

For local use without a deployed server, add the following to your Claude Desktop `claude_desktop_config.json`:

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

> Replace `/absolute/path/to/visitkorea-mcp/server.py` with the actual path on your machine. The `VISITKOREA_API_KEY` value must be the URL-encoded service key from [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do).

---

## Connecting to Manus AI

After deploying your own instance to Replit (see the deployment steps below), import the following JSON when adding a new custom MCP connector in Manus AI. Replace `<your-repl-name>` with the actual subdomain of your deployed Replit app.

```json
{
  "name": "visitkorea",
  "display_name": "VisitKorea Tourism",
  "description": "Korea Tourism Organization English Open Data API — search attractions, restaurants, hotels, festivals, and more across Korea.",
  "transport": {
    "type": "streamable-http",
    "url": "https://<your-repl-name>.replit.app/mcp"
  },
  "authentication": {
    "type": "none"
  },
  "metadata": {
    "version": "1.0.0",
    "provider": "Korea Tourism Organization (한국관광공사)",
    "data_source": "https://www.data.go.kr/data/15101753/openapi.do"
  }
}
```

> **Note:** No authentication token is required from the client — the `VISITKOREA_API_KEY` is stored and used server-side only.

---

## Deploying to Replit

Follow these steps to deploy your own fully functional instance of this MCP server on Replit.

> **New to Replit?** Sign up for a free account using this referral link: [https://replit.com/refer/leejaew](https://replit.com/refer/leejaew)

### Step 1 — Import the repository

1. Go to [replit.com](https://replit.com) and sign in.
2. Click **Create Repl** → **Import from GitHub**.
3. Paste the repository URL: `https://github.com/leejaew/custom-visitkorea-mcp`
4. Replit will detect the workspace configuration automatically.

### Step 2 — Add your API key as a Secret

1. In your Repl, open the **Secrets** panel (lock icon in the sidebar, or Tools → Secrets).
2. Create a new secret:
   - **Key:** `VISITKOREA_API_KEY`
   - **Value:** Your URL-encoded service key from [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do)

> Do not paste the key into any source file. Always use the Secrets panel so it is never committed to version control.

### Step 3 — Run the development server

Click the **Run** button (or press the green Play button). Replit will:
1. Install all Node.js and Python dependencies automatically.
2. Build the Node.js proxy server.
3. Start both the Node.js server (port 8080) and the Python MCP server (port 3001).

### Step 4 — Verify it works

Open the Replit Shell and run:

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

You should receive a JSON response listing all 14 tools.

### Step 5 — Deploy to production

1. Click **Deploy** in the top-right corner of Replit.
2. Choose **Autoscale** deployment.
3. Click **Deploy** to publish.

Your MCP server will be publicly accessible at:
```
https://<your-repl-name>.replit.app/mcp
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VISITKOREA_API_KEY` | Yes | URL-encoded service key from data.go.kr |
| `PORT` | Set by Replit | Port for the Node.js proxy (default 8080 in dev, assigned by Replit in production) |

---

## Project Structure

```
├── visitkorea-mcp/
│   ├── server.py          # Python MCP server (all 14 tools)
│   └── requirements.txt   # Python dependencies
├── artifacts/
│   └── api-server/
│       ├── src/
│       │   ├── app.ts     # Express app with wait middleware + MCP proxy
│       │   ├── index.ts   # Entry point — spawns Python server, starts Express
│       │   ├── lib/
│       │   │   └── logger.ts
│       │   └── routes/
│       │       ├── index.ts
│       │       └── health.ts
│       ├── build.mjs      # esbuild bundler config
│       ├── package.json
│       └── tsconfig.json
├── lib/                   # Shared TypeScript libraries
│   ├── api-spec/          # OpenAPI specification
│   ├── api-zod/           # Generated Zod schemas
│   ├── db/                # Drizzle ORM database layer
│   └── api-client-react/  # Generated React hooks
├── .replit                # Replit workspace configuration
├── pnpm-workspace.yaml    # pnpm monorepo configuration
└── README.md
```

---

## Data Source

This project uses the **Korea Tourism Organization English Open Data API**:

- **Portal:** [https://www.data.go.kr/data/15101753/openapi.do](https://www.data.go.kr/data/15101753/openapi.do)
- **Provider:** Korea Tourism Organization (한국관광공사) via the Korean Public Data Portal (공공데이터포털)
- **API Base URL:** `https://apis.data.go.kr/B551011/EngService2`
- **Language:** English
- **License:** Public Data, free for commercial and non-commercial use with attribution

To obtain an API key:
1. Visit [data.go.kr](https://www.data.go.kr/data/15101753/openapi.do)
2. Sign up for a free account
3. Click **활용신청** (Apply for Use) on the dataset page
4. After approval (usually instant), copy your **인증키 (Service Key)** — use the URL-encoded version

---

## License

MIT License — open source, free to use, modify, and distribute.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
