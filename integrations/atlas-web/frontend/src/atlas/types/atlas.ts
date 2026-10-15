export interface AtlasHealth {
  name: string;
  version: string;
  core?: string;
  status?: string;
}

export interface AtlasMessage {
  id?: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

export interface AtlasConversation {
  id: string;
  title?: string;
  messages?: AtlasMessage[];
}

export interface AtlasModel {
  id?: string;
  name: string;
  provider?: string;
  status?: string;
}

export interface AtlasProject {
  id: string;
  name: string;
  description?: string;
}
