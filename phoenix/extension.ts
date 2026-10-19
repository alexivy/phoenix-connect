import { request } from "node:http";
import { homedir } from "node:os";
import { join } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// A messaging-only command. It neither starts a second Core nor alters active tools.
export default function phoenixConnect(pi: ExtensionAPI) {
  pi.registerCommand("phoenix-connect", {
    description: "Inspect the Phoenix Connect messaging adapter",
    handler: async (_args, ctx) => {
      const socketPath = process.env.PHOENIX_CONNECT_SOCKET || join(homedir(), ".pi-connect/data/run/api.sock");
      const status = await new Promise<string>(resolve => {
        const req = request({ socketPath, path: "/sessions", method: "GET", timeout: 3000 }, res => {
          let body = "";
          res.on("data", chunk => { if (body.length < 16000) body += chunk.toString(); });
          res.on("end", () => {
            try { const sessions = JSON.parse(body); resolve(res.statusCode === 200 ? `Bridge reachable; ${Array.isArray(sessions) ? sessions.length : 0} active routes. This does not verify message delivery.` : "Bridge status request failed."); }
            catch { resolve("Bridge returned an invalid status response."); }
          });
        });
        req.on("timeout", () => req.destroy());
        req.on("error", () => resolve("Bridge unavailable; Core and A2A can continue independently."));
        req.end();
      });
      ctx.ui.notify(status, "info");
    },
  });
}
