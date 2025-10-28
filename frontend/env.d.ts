/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // add more variables as needed, e.g.:
  // readonly VITE_SOME_FLAG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}