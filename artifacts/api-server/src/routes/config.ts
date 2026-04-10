import { Router, type IRouter } from "express";

const router: IRouter = Router();

router.get("/config", (_req, res) => {
  // Prefer an explicit override (set this Secret if you want to control the URL manually)
  const override = process.env.PRODUCTION_MCP_URL;
  if (override) {
    return res.json({ mcpUrl: override });
  }

  // REPLIT_DOMAINS is set by the platform. In a production deployment it contains
  // the public .replit.app hostname; in a dev workspace it contains the ephemeral
  // janeway domain. Only return the URL when it's a real production domain.
  const rawDomains = process.env.REPLIT_DOMAINS ?? "";
  const domains = rawDomains
    .split(",")
    .map((d) => d.trim())
    .filter(Boolean);

  const productionDomain = domains.find((d) => d.endsWith(".replit.app")) ?? null;

  return res.json({
    mcpUrl: productionDomain ? `https://${productionDomain}/mcp` : null,
  });
});

export default router;
