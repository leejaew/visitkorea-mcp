import { useState, useEffect } from "react";
import { Check, Copy, ExternalLink } from "lucide-react";

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

const CLAUDE_DESKTOP_JSON = `{
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

const MANUS_JSON = (url: string) => `{
  "name": "visitkorea",
  "qualifiedName": "visitkorea",
  "description": "VisitKorea Tourism MCP — 14 tools covering attractions, restaurants, accommodations, festivals, and more via Korea Tourism Organization Open API.",
  "category": "travel",
  "tools": [],
  "connections": [
    {
      "type": "streamable_http",
      "url": "${url}",
      "config": {},
      "security": {},
      "externalDocs": null
    }
  ]
}`;

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-700 transition-colors cursor-pointer"
    >
      {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

function CodeBlock({ code, label }: { code: string; label?: string }) {
  return (
    <div className="rounded-lg border border-slate-200 overflow-hidden text-sm">
      {label && (
        <div className="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-200">
          <span className="text-xs font-medium text-slate-500 tracking-wide">{label}</span>
          <CopyButton text={code} />
        </div>
      )}
      <pre className="p-4 bg-slate-900 text-slate-100 font-mono text-xs leading-relaxed overflow-x-auto whitespace-pre">
        {code}
      </pre>
    </div>
  );
}

export default function App() {
  const [mcpUrl, setMcpUrl] = useState("");
  const [urlCopied, setUrlCopied] = useState(false);

  useEffect(() => {
    setMcpUrl(`https://${window.location.hostname}/mcp`);
  }, []);

  const copyUrl = () => {
    navigator.clipboard.writeText(mcpUrl);
    setUrlCopied(true);
    setTimeout(() => setUrlCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans antialiased">

      {/* Top bar */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-blue-600 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4 text-white" stroke="currentColor" strokeWidth={2}>
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
                <circle cx="12" cy="9" r="2.5" />
              </svg>
            </div>
            <span className="font-semibold text-sm tracking-tight">visitkorea-mcp</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-600">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
            Live · Streamable HTTP
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12 space-y-16">

        {/* Intro */}
        <section>
          <h1 className="text-2xl font-bold tracking-tight mb-2">VisitKorea Tourism MCP</h1>
          <p className="text-slate-500 text-sm mb-6">
            AI-ready access to Korea's general tourism data — attractions, restaurants, accommodations, festivals, and more,
            via the Korea Tourism Organization English Open API.
          </p>

          {/* URL row */}
          <div className="flex items-center gap-0 border border-slate-200 rounded-lg overflow-hidden bg-slate-50 text-sm w-full max-w-xl">
            <span className="px-4 py-2.5 text-slate-500 text-xs font-medium border-r border-slate-200 shrink-0">MCP URL</span>
            <span className="px-4 py-2.5 font-mono text-slate-700 text-xs truncate flex-1">
              {mcpUrl || "https://{hostname}/mcp"}
            </span>
            <button
              onClick={copyUrl}
              className="px-4 py-2.5 border-l border-slate-200 text-slate-400 hover:text-slate-700 hover:bg-white transition-colors cursor-pointer shrink-0"
            >
              {urlCopied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
        </section>

        {/* Tools */}
        <section>
          <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
            {TOOLS.length} Tools
            <span className="text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">EngService2</span>
          </h2>
          <div className="border border-slate-200 rounded-lg overflow-hidden divide-y divide-slate-100">
            {TOOLS.map((tool, i) => (
              <div key={tool.name} className="flex gap-4 px-4 py-3 hover:bg-slate-50 transition-colors">
                <span className="text-xs text-slate-300 font-mono w-6 shrink-0 pt-0.5 text-right select-none">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-3 flex-wrap">
                    <span className="font-mono text-sm font-medium text-slate-900">{tool.name}</span>
                    <span className="font-mono text-xs text-slate-400">{tool.operation}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{tool.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Connect */}
        <section>
          <h2 className="text-base font-semibold mb-6">Connect your AI agent</h2>
          <div className="space-y-8">

            {/* Claude AI */}
            <div>
              <h3 className="text-sm font-medium mb-3 text-slate-700">Claude AI (claude.ai) — Custom Connector</h3>
              <div className="border border-slate-200 rounded-lg overflow-hidden text-sm divide-y divide-slate-100">
                {[
                  { field: "Name", value: "VisitKorea Tourism", mono: false },
                  { field: "Remote MCP server URL", value: mcpUrl || "https://{hostname}/mcp", mono: true },
                  { field: "OAuth Client ID", value: "leave blank", mono: false, muted: true },
                  { field: "OAuth Client Secret", value: "leave blank", mono: false, muted: true },
                ].map(({ field, value, mono, muted }) => (
                  <div key={field} className="flex items-center gap-4 px-4 py-2.5 bg-white">
                    <span className="text-xs text-slate-500 w-48 shrink-0">{field}</span>
                    <span className={`text-xs flex-1 ${mono ? "font-mono text-blue-700" : muted ? "text-slate-400 italic" : "text-slate-700"}`}>
                      {value}
                    </span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-2">No OAuth credentials needed — the API key is stored server-side.</p>
            </div>

            {/* Claude Desktop */}
            <div>
              <h3 className="text-sm font-medium mb-3 text-slate-700">Claude Desktop — claude_desktop_config.json</h3>
              <CodeBlock code={CLAUDE_DESKTOP_JSON} label="JSON" />
              <p className="text-xs text-slate-400 mt-2">
                Replace the path with the absolute path to <code className="bg-slate-100 px-1 rounded">server.py</code> on your machine.
              </p>
            </div>

            {/* Manus AI */}
            <div>
              <h3 className="text-sm font-medium mb-3 text-slate-700">Manus AI — MCP Connector JSON</h3>
              <CodeBlock code={MANUS_JSON(mcpUrl || "https://{hostname}/mcp")} label="JSON" />
            </div>
          </div>
        </section>

        {/* Meta */}
        <section>
          <div className="border border-slate-200 rounded-lg overflow-hidden text-sm divide-y divide-slate-100">
            {[
              { label: "Data Source", value: "Korea Tourism Organization (한국관광공사)" },
              { label: "API Base", value: "apis.data.go.kr/B551011/EngService2" },
              { label: "Transport", value: "Streamable HTTP (MCP protocol)" },
              { label: "Refresh Cycle", value: "Real-time (live API calls)" },
              { label: "Rate Limit", value: "1,000 requests / day (dev key)" },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center gap-4 px-4 py-2.5 bg-white">
                <span className="text-xs text-slate-400 w-40 shrink-0">{label}</span>
                <span className="text-xs text-slate-700 font-mono">{value}</span>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 mt-4">
            <a
              href="https://www.data.go.kr/data/15101753/openapi.do"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              Official API Reference <ExternalLink className="w-3 h-3" />
            </a>
            <a
              href="https://github.com/leejaew/visitkorea-mcp"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"
            >
              GitHub <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </section>

      </main>

      <footer className="border-t border-slate-100 py-6 text-center">
        <p className="text-xs text-slate-400">
          VisitKorea MCP · Korea Tourism Organization English Open API · MIT License
        </p>
      </footer>
    </div>
  );
}
