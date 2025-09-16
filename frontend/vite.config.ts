/**
 * Shared Vite configuration for all frontend services.
 *
 * Vite: https://vitest.dev/config/
 * Vitest: https://vitest.dev/config/
 */

import { defineConfig as defineVitestConfig, mergeConfig } from "vitest/config"
import { defineConfig as defineViteConfig } from "vite"
import react from "@vitejs/plugin-react"

export const viteConfig = defineViteConfig({
  plugins: [react()],
  envDir: "env",
  server: {
    open: true,
    host: true,
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

// TODO: investigate browser mode https://vitest.dev/guide/browser/
export const vitestConfig = defineVitestConfig({
  server: {
    fs: {
      // Allow vitest setup to be served from submodule root.
      allow: ["../vitest.setup.ts"],
    },
  },
  test: {
    // This enables global APIs for your tests. Instead of importing test,
    // expect, vi, and other Vitest functions from vitest, you can use them
    // directly in your test files without an import statement.
    globals: true,
    // Creates a mock browser environment, including the document and window
    // objects, which is essential for testing front-end code that interacts
    // with the DOM.
    environment: "jsdom",
    // Files that will run before each test file is executed.
    setupFiles: ["./vitest.setup.ts"],
    // Automatically resets mocks before each test. This means any mock
    // implementation or mock call history is cleared, ensuring that the state
    // of your mocks from a previous test doesn't affect the next one.
    mockReset: true,
    // Only includes test files that match the expected naming convention.
    include: ["src/**/*.test.{j,t}s{x,}"],
    coverage: {
      enabled: true,
      provider: "istanbul",
      // `html` generates a human-readable website that you can view in your
      // browser. `cobertura` creates a machine-readable XML file, which is used
      // by Codecov in our CI/CD pipelines to analyze coverage trends.
      reporter: ["html", "cobertura"],
    },
  },
})

export default mergeConfig(viteConfig, vitestConfig)
