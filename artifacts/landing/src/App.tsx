import { useState, useEffect } from "react";
import { ChevronRight } from "lucide-react";
import { marked } from "marked";
import manusInstructions from "./MANUS_INSTRUCTIONS.md?raw";

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

function CopyButton({
  text,
  onClick,
  variant = "dark",
}: {
  text: string;
  onClick?: (e: React.MouseEvent) => void;
  variant?: "dark" | "light";
}) {
  const [copied, setCopied] = useState(false);
  const cls =
    variant === "light"
      ? "text-xs px-3 py-1 rounded-xl border border-border bg-white hover:bg-muted/50 transition-colors font-mono text-muted-foreground shrink-0 cursor-pointer"
      : "text-xs px-2 py-1 rounded bg-white/10 hover:bg-white/20 transition-colors font-mono border border-white/20 cursor-pointer";
  return (
    <button
      onClick={(e) => {
        onClick?.(e);
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className={cls}
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}


export default function App() {
  const [isProd, setIsProd] = useState(false);
  const [host, setHost] = useState(window.location.host);
  const [isManusOpen, setIsManusOpen] = useState(false);

  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then((data) => {
        // Update the connector URL to always show the best available host (production if deployed)
        if (data.host) setHost(data.host);
        // Only hide the dev warning when the user is *actually on* the production domain —
        // not just because the project happens to be deployed. A deployed project still
        // serves the dev workspace at a janeway URL, which is not the permanent URL.
        const onProductionDomain =
          !!data.mcpUrl && window.location.hostname.endsWith(".replit.app");
        setIsProd(onProductionDomain);
      })
      .catch(() => {
        setIsProd(false);
      });
  }, []);

  const manusJson = `{
  "mcpServers": {
    "visitkorea": {
      "type": "streamableHttp",
      "url": "https://${host}/mcp"
    }
  }
}`;

  const manusHtml = marked.parse(manusInstructions) as string;

  return (
    <div className="min-h-screen bg-[hsl(220,20%,97%)]">

      {/* Header */}
      <header className="border-b border-border bg-white">
        <div className="max-w-4xl mx-auto px-6 py-5 flex items-center gap-3">
          <span className="text-2xl">🇰🇷</span>
          <div>
            <h1 className="text-lg font-semibold text-foreground leading-tight">visitkorea-mcp</h1>
            <p className="text-xs text-muted-foreground">Korea Tourism Organization (KTO) · Open API via data.go.kr · MCP Server</p>
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
            This MCP (Model Context Protocol) server wraps the{" "}
            <code className="text-xs bg-muted px-1 py-0.5 rounded">EngService2</code>{" "}
            Open API published on{" "}
            <strong className="font-semibold text-foreground">data.go.kr</strong>{" "}
            (Korea's Public Data Portal), based on general tourism data curated by the{" "}
            <strong className="font-semibold text-foreground">Korea Tourism Organization (KTO)</strong>.
            It exposes {TOOLS.length} structured tools that Manus AI, Claude, and other MCP-compatible agents
            can call directly via Streamable HTTP.
          </p>
        </section>

        {/* Connect */}
        <section>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Connect your AI agent
          </h3>
          <div className="rounded-xl bg-slate-900 text-slate-100 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/10">
              <span className="text-xs font-medium text-slate-400">MCP Connector JSON</span>
              <CopyButton text={manusJson} />
            </div>
            <pre className="px-4 py-4 text-sm font-mono overflow-x-auto leading-relaxed">
              <code>{manusJson}</code>
            </pre>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Paste this into your AI agent's custom connector settings. The Streamable HTTP endpoint is at{" "}
            <code className="bg-muted px-1 py-0.5 rounded">https://{host}/mcp</code>
          </p>
          {!isProd && (
            <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
              This is the development URL. Deploy the project to get your permanent{" "}
              <code className="bg-muted px-1 py-0.5 rounded">.replit.app</code> production URL.
            </p>
          )}
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
        <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Data Owner</p>
            <p className="text-sm font-medium text-foreground">Korea Tourism Organization</p>
            <p className="text-xs text-muted-foreground mt-0.5">KTO (한국관광공사)</p>
          </div>
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">API Provider</p>
            <p className="text-sm font-medium text-foreground">data.go.kr</p>
            <p className="text-xs text-muted-foreground mt-0.5">Korea Public Data Portal</p>
          </div>
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Caching</p>
            <p className="text-sm font-medium text-foreground">TTL Cache</p>
            <p className="text-xs text-muted-foreground mt-0.5">1 h codes · 5 min search results</p>
          </div>
          <div className="bg-white border border-border rounded-xl px-5 py-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mb-1">Transport</p>
            <p className="text-sm font-medium text-foreground">Streamable HTTP</p>
            <p className="text-xs text-muted-foreground mt-0.5">MCP protocol · MIT License</p>
          </div>
        </section>

        {/* Manus AI Instructions (collapsible) */}
        <section>
          <div className="flex items-stretch gap-2">
            <div
              role="button"
              tabIndex={0}
              onClick={() => setIsManusOpen((v) => !v)}
              onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setIsManusOpen((v) => !v); }}
              aria-expanded={isManusOpen}
              className="flex-1 flex items-center gap-2 px-5 py-3.5 bg-white border border-border rounded-xl cursor-pointer text-left hover:bg-muted/50 transition-colors"
            >
              <ChevronRight
                className="w-3.5 h-3.5 text-muted-foreground shrink-0 transition-transform duration-200"
                style={{ transform: isManusOpen ? "rotate(90deg)" : "rotate(0deg)" }}
              />
              <span className="text-sm font-semibold text-foreground">
                Manus AI Instructions
              </span>
              <span className="text-xs text-muted-foreground">
                How and when to use this MCP — click to expand
              </span>
            </div>
            <CopyButton
              text={manusInstructions}
              variant="light"
            />
          </div>

          {isManusOpen && (
            <div className="mt-2 bg-white border border-border rounded-xl px-9 py-8 manus-content">
              <div
                className="prose prose-sm max-w-none
                  prose-headings:text-foreground
                  prose-h1:text-xl prose-h1:font-bold prose-h1:mb-4
                  prose-h2:text-base prose-h2:font-bold prose-h2:mt-7 prose-h2:mb-2.5 prose-h2:pb-1.5 prose-h2:border-b prose-h2:border-border
                  prose-h3:text-sm prose-h3:font-semibold prose-h3:mt-5 prose-h3:mb-1.5
                  prose-p:text-muted-foreground prose-p:leading-relaxed
                  prose-li:text-muted-foreground
                  prose-strong:text-foreground prose-strong:font-semibold
                  prose-code:text-primary prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:before:content-none prose-code:after:content-none
                  prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-pre:rounded-xl
                  prose-pre:p-4 prose-pre:text-xs
                  prose-blockquote:border-primary prose-blockquote:bg-muted prose-blockquote:rounded-r-md prose-blockquote:text-muted-foreground prose-blockquote:not-italic
                  prose-table:text-sm
                  prose-th:bg-muted prose-th:text-foreground prose-th:font-semibold
                  prose-td:text-muted-foreground
                  prose-a:text-primary
                  prose-hr:border-border"
                dangerouslySetInnerHTML={{ __html: manusHtml }}
              />
            </div>
          )}
        </section>

        {/* Footer links */}
        <section className="text-center py-4 border-t border-border">
          <a
            href="https://www.data.go.kr/data/15101753/openapi.do"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline"
          >
            data.go.kr API Reference →
          </a>
          <span className="mx-3 text-muted-foreground">·</span>
          <a
            href="https://github.com/leejaew/visitkorea-mcp"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline"
          >
            GitHub →
          </a>
        </section>

      </main>
    </div>
  );
}
