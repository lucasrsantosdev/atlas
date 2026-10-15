/**
 * ATLAS TOOL ADAPTER
 *
 * As capacidades externas passam sempre
 * pela arquitetura e pelas politicas do Atlas.
 *
 * MCP, filesystem, hardware e futuras ferramentas
 * nao devem ser chamadas diretamente pela UI.
 */

export interface AtlasToolStatus {
  name: string;
  available: boolean;
  risk?: "low" | "medium" | "high";
}

export function normalizeToolStatus(
  input: unknown
): AtlasToolStatus[] {

  if (!Array.isArray(input)) {
    return [];
  }

  return input as AtlasToolStatus[];
}
