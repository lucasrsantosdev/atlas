import { ATLAS_API } from "../config/api";

async function request<T = unknown>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${ATLAS_API}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {})
    }
  });

  if (!response.ok) {
    const details = await response.text();

    throw new Error(
      `Atlas API HTTP ${response.status}: ${details}`
    );
  }

  return (await response.json()) as T;
}

export interface AtlasConversationResponse {
  id: string;
  title?: string | null;
}

export const atlasApi = {
  health: () => request("/health"),

  models: () => request("/models"),

  modelStatus: () => request("/models/status"),

  projects: () => request("/projects"),

  conversations: () => request("/conversations"),

  conversation: (conversationId: string) =>
    request(`/conversations/${encodeURIComponent(conversationId)}`),

  messages: (conversationId: string) =>
    request(`/conversations/${encodeURIComponent(conversationId)}/messages`),

  createConversation: (
    payload: { title?: string; project_id?: string | number | null } = {}
  ) =>
    request<AtlasConversationResponse>("/conversations", {
      method: "POST",
      body: JSON.stringify(payload)
    }),

  chat: (conversationId: string, content: string) =>
    request(
      `/conversations/${encodeURIComponent(conversationId)}/chat`,
      {
        method: "POST",
        body: JSON.stringify({ content })
      }
    )
};