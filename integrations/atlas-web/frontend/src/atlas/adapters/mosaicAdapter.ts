/**
 * MOSAIC ADAPTER
 *
 * Mosaic pode enriquecer contexto, entidades,
 * intencao e relevancia.
 *
 * Ele NAO define:
 *
 * - identidade do Atlas
 * - politicas do Atlas
 * - memoria soberana
 * - seguranca
 * - modelo principal
 * - comportamento final
 *
 * O Atlas Core permanece soberano.
 */

export interface MosaicContext {
  intent?: string;
  entities?: unknown[];
  relevance?: number;
  metadata?: Record<string, unknown>;
}

export function normalizeMosaicContext(
  input: unknown
): MosaicContext {

  if (!input || typeof input !== "object") {
    return {};
  }

  return input as MosaicContext;
}
