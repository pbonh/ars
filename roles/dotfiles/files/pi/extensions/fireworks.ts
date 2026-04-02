import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.registerProvider("fireworks", {
    baseUrl: "https://api.fireworks.ai/inference/v1",
    apiKey: "FIREWORKS_API_KEY",
    api: "openai-completions",
    authHeader: true,
    models: [
      {
        id: "accounts/fireworks/models/kimi-k2.5-turbo",
        name: "Kimi K2.5 Turbo",
        reasoning: true,
        input: ["text", "image"],
        cost: {
          input: 0.70,
          output: 2.80,
          cacheRead: 0.07,
          cacheWrite: 0.70
        },
        contextWindow: 256000,
        maxTokens: 16384
      },
      {
        id: "accounts/fireworks/models/kimi-k2.5",
        name: "Kimi K2.5",
        reasoning: true,
        input: ["text", "image"],
        cost: {
          input: 2.00,
          output: 8.00,
          cacheRead: 0.20,
          cacheWrite: 2.00
        },
        contextWindow: 256000,
        maxTokens: 16384
      }
    ]
  });
}
