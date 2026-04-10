import { useState, useEffect } from "react";
import { Check, Copy, Activity, Code, Server, Map, Globe, Cpu, LayoutList, LocateFixed, Search, LayoutGrid, Clock, Image as ImageIcon, MapPin, Hash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { motion } from "framer-motion";

const tools = [
  { id: 1, name: "search_festivals", description: "Search festivals and cultural events by area and date range", icon: Globe },
  { id: 2, name: "search_attractions", description: "Find tourist attractions by area and category", icon: Map },
  { id: 3, name: "search_accommodations", description: "Find hotels and lodging options by area", icon: Server },
  { id: 4, name: "search_restaurants", description: "Find dining options by area and cuisine type", icon: Globe },
  { id: 5, name: "search_shopping", description: "Find shopping areas and markets by area", icon: MapPin },
  { id: 6, name: "search_leisure", description: "Find leisure and sports activities by area", icon: Activity },
  { id: 7, name: "get_area_based_list", description: "Get paginated list of any content type filtered by area", icon: LayoutList },
  { id: 8, name: "get_location_based_list", description: "Find attractions within a GPS radius (WGS84 coordinates)", icon: LocateFixed },
  { id: 9, name: "search_by_keyword", description: "Search across all content types by keyword", icon: Search },
  { id: 10, name: "get_detail_common", description: "Get title, address, GPS coordinates, phone, homepage, and overview", icon: LayoutGrid },
  { id: 11, name: "get_detail_intro", description: "Get opening hours, admission fees, rest days, and parking info", icon: Clock },
  { id: 12, name: "get_detail_image", description: "Get image gallery for an attraction", icon: ImageIcon },
  { id: 13, name: "get_nearby_attractions", description: "Get nearby attractions within a given radius", icon: LocateFixed },
  { id: 14, name: "get_area_codes", description: "Get area and sub-area codes used for filtering queries", icon: Hash }
];

export default function App() {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [mcpUrl, setMcpUrl] = useState("");

  useEffect(() => {
    setMcpUrl(`https://${window.location.hostname}/mcp`);
  }, []);

  const copyToClipboard = (text: string, setter: (val: boolean) => void) => {
    navigator.clipboard.writeText(text);
    setter(true);
    setTimeout(() => setter(false), 2000);
  };

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-white text-slate-900 font-sans selection:bg-blue-100">
        
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/50">
          <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold">
                <Map className="w-4 h-4" />
              </div>
              <span className="font-semibold tracking-tight">VisitKorea MCP</span>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 flex gap-1.5 items-center">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Server Live
              </Badge>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="pt-40 pb-20 px-6 min-h-[90vh] flex flex-col justify-center relative overflow-hidden">
          <div className="absolute inset-0 z-0">
            <img src="/hero-bg.png" alt="Korean architectural tech abstract background" className="w-full h-full object-cover opacity-15" />
            <div className="absolute inset-0 bg-gradient-to-b from-white/40 via-white/80 to-white" />
            <div className="absolute inset-0 bg-slate-50/50 mix-blend-multiply" />
          </div>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto text-center relative z-10"
          >
            <Badge variant="outline" className="mb-6 px-4 py-1.5 rounded-full border-blue-200 bg-blue-50 text-blue-700 tracking-wide font-medium">
              v1.0 • Streamable HTTP
            </Badge>
            <h1 className="text-6xl md:text-8xl font-bold tracking-tight text-slate-900 leading-[1.05] mb-8">
              Korea Tourism <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 via-indigo-600 to-red-600">for AI Agents.</span>
            </h1>
            <p className="text-xl text-slate-600 mb-12 leading-relaxed max-w-2xl mx-auto font-medium">
              A high-performance Model Context Protocol (MCP) server wrapping the Korea Tourism Organization's English Open API.
            </p>

            <div className="p-1.5 rounded-2xl bg-white/60 backdrop-blur-xl border border-slate-200/60 inline-flex max-w-full shadow-xl shadow-blue-900/5">
              <div className="flex items-center bg-white rounded-xl border border-slate-200/80 overflow-hidden w-full max-w-lg">
                <div className="px-5 py-4 bg-slate-50/80 border-r border-slate-200/80 text-slate-500 flex items-center font-medium">
                  <Server className="w-4 h-4 mr-2.5 text-blue-600" />
                  URL
                </div>
                <div className="px-5 py-4 font-mono text-sm text-slate-700 truncate flex-1 min-w-[200px] text-left">
                  {mcpUrl || "Loading..."}
                </div>
                <button 
                  onClick={() => copyToClipboard(mcpUrl, setCopiedUrl)}
                  className="px-6 py-4 text-slate-500 hover:text-blue-700 hover:bg-blue-50 transition-all flex items-center border-l border-slate-200/80 h-full cursor-pointer group"
                >
                  {copiedUrl ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4 group-hover:scale-110 transition-transform" />}
                </button>
              </div>
            </div>
          </motion.div>
        </section>

        {/* Tools Section */}
        <section className="py-24 bg-slate-50 border-y border-slate-200/50 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="mb-16">
              <h2 className="text-3xl font-bold mb-4 tracking-tight">14 Powerful Tools</h2>
              <p className="text-slate-600 max-w-2xl text-lg">Comprehensive access to festivals, accommodations, restaurants, and precise location-based discovery. Everything an AI needs to plan a trip to Korea.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tools.map((tool, i) => (
                <motion.div
                  key={tool.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.05, duration: 0.4 }}
                >
                  <Card className="h-full border-slate-200/60 shadow-sm hover:shadow-md transition-shadow bg-white">
                    <CardHeader className="pb-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center mb-4 text-blue-600">
                        <tool.icon className="w-5 h-5" />
                      </div>
                      <CardTitle className="font-mono text-sm tracking-tight text-slate-900">{tool.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-slate-600 text-sm leading-relaxed">
                        {tool.description}
                      </CardDescription>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Connections Section */}
        <section className="py-24 px-6 max-w-4xl mx-auto">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold mb-4 tracking-tight">Connect your Agent</h2>
            <p className="text-slate-600 text-lg">Streamable HTTP setup instructions for popular AI platforms.</p>
          </div>

          <div className="space-y-12">
            {/* Claude AI */}
            <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-[#D97757] flex items-center justify-center text-white text-xs font-bold">C</div>
                <h3 className="font-semibold text-lg">Claude AI (claude.ai)</h3>
              </div>
              <div className="p-6">
                <p className="text-slate-600 mb-4 text-sm">Add a custom connector with the following details:</p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left border-collapse">
                    <tbody>
                      <tr className="border-b border-slate-100">
                        <th className="py-3 pr-4 font-medium text-slate-900 w-1/3">Name</th>
                        <td className="py-3 font-mono text-slate-600">VisitKorea Tourism</td>
                      </tr>
                      <tr className="border-b border-slate-100">
                        <th className="py-3 pr-4 font-medium text-slate-900">Remote MCP server URL</th>
                        <td className="py-3 font-mono text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block mt-2 mb-2">{mcpUrl || "https://{hostname}/mcp"}</td>
                      </tr>
                      <tr>
                        <th className="py-3 pr-4 font-medium text-slate-900">OAuth fields</th>
                        <td className="py-3 text-slate-500 italic">leave blank</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Claude Desktop */}
            <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-slate-900 flex items-center justify-center text-white"><Cpu className="w-3.5 h-3.5" /></div>
                <h3 className="font-semibold text-lg">Claude Desktop</h3>
              </div>
              <div className="p-6">
                <p className="text-slate-600 mb-4 text-sm">Add this to your <code className="bg-slate-100 px-1 py-0.5 rounded text-xs">claude_desktop_config.json</code>:</p>
                <pre className="bg-slate-900 text-slate-50 p-4 rounded-xl overflow-x-auto text-sm font-mono leading-relaxed">
{`{
  "mcpServers": {
    "visitkorea": {
      "command": "python3",
      "args": ["/absolute/path/to/visitkorea-mcp/server.py"],
      "env": { "VISITKOREA_API_KEY": "your_url_encoded_service_key_here" }
    }
  }
}`}
                </pre>
              </div>
            </div>

            {/* Manus AI */}
            <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-3">
                <div className="w-6 h-6 rounded bg-indigo-600 flex items-center justify-center text-white"><Code className="w-3.5 h-3.5" /></div>
                <h3 className="font-semibold text-lg">Manus AI</h3>
              </div>
              <div className="p-6">
                <p className="text-slate-600 mb-4 text-sm">Import this JSON connector configuration. Replace <code className="bg-slate-100 px-1 py-0.5 rounded text-xs">{`{hostname}`}</code> with your actual hostname in the URL.</p>
                <pre className="bg-slate-900 text-slate-50 p-4 rounded-xl overflow-x-auto text-sm font-mono leading-relaxed">
{`{
  "name": "visitkorea",
  "qualifiedName": "visitkorea",
  "description": "VisitKorea Tourism MCP — access Korea Tourism Organization's Open API through 14 MCP tools covering attractions, restaurants, accommodations, festivals, and more.",
  "logoUrl": "",
  "category": "travel",
  "tools": [],
  "connections": [
    {
      "type": "streamable_http",
      "url": "${mcpUrl || "https://{hostname}/mcp"}",
      "config": {},
      "security": {},
      "externalDocs": null
    }
  ]
}`}
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 border-t border-slate-200/50 bg-slate-50 text-center">
          <p className="text-slate-500 text-sm">Built for AI Agents. Powered by Korea Tourism Organization Open API.</p>
        </footer>

        <Toaster />
      </div>
    </TooltipProvider>
  );
}
