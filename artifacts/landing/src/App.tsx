import { useState, useEffect } from "react";
import { ExternalLink } from "lucide-react";

const TOOLS = [
  {
    name: "search_tourism_by_area",
    operation: "areaBasedList2",
    desc: "Search tourism attractions, restaurants, accommodations, shopping, cultural facilities, leisure spots, and festivals by province or city.",
  },
  {
    name: "search_tourism_by_location",
    operation: "locationBasedList2",
    desc: "Find tourism content within a GPS radius using WGS84 coordinates. Supports all content types.",
  },
  {
    name: "search_tourism_by_keyword",
    operation: "searchKeyword2",
    desc: "Search across all tourism content types by keyword. Returns matching places, events, and facilities.",
  },
  {
    name: "search_festivals_and_events",
    operation: "searchFestival2",
    desc: "Search festivals, performances, and cultural events by date range and area.",
  },
  {
    name: "search_accommodations",
    operation: "searchStay2",
    desc: "Search hotels, guesthouses, pensions, and other accommodation by area.",
  },
  {
    name: "get_tourism_common_info",
    operation: "detailCommon2",
    desc: "Fetch common details for a content ID: title, address, GPS coordinates, phone, homepage URL, and overview text.",
  },
  {
    name: "get_tourism_intro_info",
    operation: "detailIntro2",
    desc: "Fetch introductory details: opening hours, admission fees, rest days, parking, and type-specific intro fields.",
  },
  {
    name: "get_tourism_detail_info",
    operation: "detailInfo2",
    desc: "Fetch detailed type-specific information (e.g. room types for accommodation, menu items for restaurants).",
  },
  {
    name: "get_tourism_images",
    operation: "detailImage2",
    desc: "Get image gallery for an attraction. imageYN=Y returns venue photos; N returns food menu photos (restaurant type only).",
  },
  {
    name: "get_sync_list",
    operation: "areaBasedSyncList2",
    desc: "Retrieve content updated since a given modification timestamp. Useful for syncing cached data.",
  },
  {
    name: "get_legal_district_codes",
    operation: "ldongCode2",
    desc: "Look up legal district codes (lDongRegnCd / lDongSignguCd) by province, city, or county name.",
  },
  {
    name: "get_classification_codes",
    operation: "lclsSystmCode2",
    desc: "Retrieve the tourism classification system code hierarchy (3 levels). Use lclsSystmListYn=Y for full list.",
  },
  {
    name: "get_area_codes",
    operation: "areaCode2",
    desc: "Get area codes and sub-area (sigungu) codes used for areaCode-based filtering queries.",
  },
  {
    name: "get_category_codes",
    operation: "categoryCode2",
    desc: "Get category hierarchy codes (cat1 / cat2 / cat3) for filtering by tourism content category.",
  },
];

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="text-xs px-2 py-1 rounded bg-white/10 hover:bg-white/20 transition-colors font-mono border border-white/20 cursor-pointer"
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

function DarkCodeBlock({ label, code }: { label: string; code: string }) {
  return (
    <div className="rounded-xl bg-slate-900 text-slate-100 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/10">
        <span className="text-xs font-medium text-slate-400">{label}</span>
        <CopyButton text={code} />
      </div>
      <pre className="px-4 py-4 text-sm font-mono overflow-x-auto leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export default function App() {
  const [mcpUrl, setMcpUrl] = useState<string | null>(null);
  const [isProd, setIsProd] = useState(false);

  const [host, setHost] = useState(window.location.host);

  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then((data) => {
        setMcpUrl(data.mcpUrl ?? null);
        setIsProd(!!data.mcpUrl);
        if (data.host) setHost(data.host);
      })
      .catch(() => {
        setMcpUrl(null);
        setIsProd(false);
      });
  }, []);

  const manusJson = `{
  "name": "visitkorea",
  "qualifiedName": "visitkorea",
  "description": "VisitKorea Tourism MCP — ${TOOLS.length} tools via Korea Tourism Organization English Open API.",
  "category": "travel",
  "tools": [],
  "connections": [
    {
      "type": "streamable_http",
      "url": "https://${host}/mcp",
      "config": {},
      "security": {},
      "externalDocs": null
    }
  ]
}`;

  const claudeDesktopJson = `{
  "mcpServers": {
    "visitkorea": {
      "command": "python3",
      "args": ["/absolute/path/to/visitkorea-mcp/server.py"],
      "env": {
        "VISITKOREA_API_KEY": "your_url_encoded_service_key_here"
      }
    }
  }
}`;

  const claudeConnectorJson = `{
  "name": "VisitKorea Tourism",
  "url": "https://${host}/mcp"
}`;

  return (
    <div className="min-h-screen bg-[hsl(220,20%,97%)]">

      {/* Header */}
      <header className="border-b border-border bg-white">
        <div className="max-w-4xl mx-auto px-6 py-5 flex items-center gap-3">
          <span className="text-2xl">🇰🇷</span>
          <div>
            <h1 className="text-lg font-semibold text-foreground leading-tight">visitkorea-mcp</h1>
            <p className="text-xs text-muted-foreground">Korea Tourism Organization · English Open API · MCP Server</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full bg-green-50 text-green-700 border border-green-200">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              Live · Streamable HTTP
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10 space-y-10">

        {/* Hero */}
        <section>
          <h2 className="text-2xl font-bold text-foreground">AI-ready access to Korea's general tourism data</h2>
          <p className="mt-2 text-muted-foreground max-w-2xl">
            This MCP (Model Context Protocol) server wraps the official Korea Tourism Organization{" "}
            <code className="text-xs bg-muted px-1 py-0.5 rounded">EngService2</code>{" "}
            API, exposing {TOOLS.length} structured tools that Manus AI, Claude, and other MCP-compatible agents
            can call directly via Streamable HTTP.
          </p>
        </section>

        {/* Connect */}
        <section>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Connect your AI agent
          </h3>
          <div className="space-y-6">

            {/* Claude AI (claude.ai) */}
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Claude AI (claude.ai) — Custom Connector</p>
              <div className="bg-white border border-border rounded-xl overflow-hidden divide-y divide-border text-sm">
                {[
                  { field: "Name", value: "VisitKorea Tourism", mono: false },
                  { field: "Remote MCP server URL", value: `https://${host}/mcp`, mono: true },
                  { field: "OAuth Client ID", value: "leave blank", muted: true },
                  { field: "OAuth Client Secret", value: "leave blank", muted: true },
                ].map(({ field, value, mono, muted }) => (
                  <div key={field} className="flex items-center gap-4 px-5 py-3">
                    <span className="text-xs text-muted-foreground w-52 shrink-0">{field}</span>
                    <span className={`text-xs flex-1 ${mono ? "font-mono text-primary" : muted ? "text-muted-foreground italic" : "text-foreground"}`}>
                      {value}
                    </span>
                  </div>
                ))}
              </div>
              <p className="mt-2 text-xs text-muted-foreground">No OAuth credentials needed — the API key is stored server-side.</p>
            </div>

            {/* Claude Desktop */}
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Claude Desktop — claude_desktop_config.json</p>
              <DarkCodeBlock label="JSON" code={claudeDesktopJson} />
              <p className="mt-2 text-xs text-muted-foreground">
                Replace the path with the absolute path to{" "}
                <code className="bg-muted px-1 py-0.5 rounded">server.py</code> on your machine.
              </p>
            </div>

            {/* Manus AI */}
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-2">Manus AI — MCP Connector JSON</p>
              <DarkCodeBlock label="MCP Connector JSON" code={manusJson} />
            </div>

            {!isProd && (
              <p className="text-xs text-amber-600">
                This is the development URL. Deploy the project to get your permanent{" "}
                <code className="bg-muted px-1 py-0.5 rounded">.replit.app</code> production URL.
              </p>
            )}
          </div>
        </section>

        {/* Tools */}
        <section>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Available Tools ({TOOLS.length})
          </h3>
          <div className="grid gap-3">
            {TOOLS.map((tool, i) => (
              <div key={tool.name} className="bg-white border border-border rounded-xl px-5 py-4 flex gap-4 items-start">
                <span className="mt-0.5 text-xs font-mono font-bold text-muted-foreground bg-muted rounded px-1.5 py-0.5 shrink-0">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <code className="text-sm font-mono font-semibold text-primary">{tool.name}</code>
                    <span className="text-xs text-muted-foreground font-mono bg-muted px-1.5 py-0.5 rounded">{tool.operation}</span>
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{tool.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Meta */}
        <section className="grid sm:grid-cols-3 gap-4">
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Data Source</p>
            <p className="text-sm font-medium text-foreground">Korea Tourism Organization</p>
            <p className="text-xs text-muted-foreground mt-0.5">한국관광공사 · EngService2</p>
          </div>
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Refresh Cycle</p>
            <p className="text-sm font-medium text-foreground">Real-time</p>
            <p className="text-xs text-muted-foreground mt-0.5">Live API calls on every request</p>
          </div>
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Transport</p>
            <p className="text-sm font-medium text-foreground">Streamable HTTP</p>
            <p className="text-xs text-muted-foreground mt-0.5">MCP protocol · MIT License</p>
          </div>
        </section>

        {/* Links */}
        <div className="flex items-center gap-4 pb-2">
          <a
            href="https://www.data.go.kr/data/15101753/openapi.do"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
          >
            Official API Reference <ExternalLink className="w-3 h-3" />
          </a>
          <a
            href="https://github.com/leejaew/visitkorea-mcp"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
          >
            GitHub <ExternalLink className="w-3 h-3" />
          </a>
        </div>

      </main>
    </div>
  );
}
