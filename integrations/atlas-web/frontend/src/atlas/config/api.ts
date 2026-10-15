const DEFAULT_API =
  "http://127.0.0.1:8000";

export const ATLAS_API =
  import.meta.env.VITE_ATLAS_API_URL ??
  DEFAULT_API;
