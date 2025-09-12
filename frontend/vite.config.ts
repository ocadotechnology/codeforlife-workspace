/**
 * Shared Vite configuration for all frontend services.
 *
 * Vite: https://vitest.dev/config/
 * Vitest: https://vitest.dev/config/
 */

import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [
    // @ts-expect-error is a valid plugin option
    react(),
  ],
  envDir: "env",
  server: {
    open: true,
    host: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "src/setupTests",
    mockReset: true,
    coverage: {
      enabled: true,
      provider: "istanbul",
      reporter: ["html", "cobertura"],
    },
  },
  optimizeDeps: {
    // TODO: investigate which of these are needed
    include: [
      "@mui/x-date-pickers",
      "@mui/x-date-pickers/AdapterDayjs",
      "dayjs",
      "dayjs/locale/en-gb",
      "@mui/icons-material",
      "yup",
      "formik",
    ],
  },
})
