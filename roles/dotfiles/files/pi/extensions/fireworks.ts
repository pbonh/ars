import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerProvider("fireworks", {
    baseUrl: "https://api.fireworks.ai/inference/v1",
    apiKey: "FIREWORKS_API_KEY",
    api: "openai-completions",
    authHeader: true,
    models: [
      {
        id: "accounts/fireworks/models/kimi-k2p5-turbo",
        name: "Kimi K2.5",
        reasoning: true,
        input: ["text", "image"],
        cost: {
          input: 0.60,
          output: 3.00,
          cacheRead: 0.10,
          cacheWrite: 0.60
        },
        contextWindow: 256000,
        maxTokens: 16384
      }
    ]
  });
}
