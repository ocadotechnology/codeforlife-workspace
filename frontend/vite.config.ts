/**
 * Shared Vite configuration for all frontend services.
 *
 * Vite: https://vitest.dev/config/
 * Vitest: https://vitest.dev/config/
 */

import {
  defineConfig as defineVitestConfig,
  mergeConfig,
  defaultExclude as defaultTestExclude,
} from "vitest/config"
import { defineConfig as defineViteConfig } from "vite"
import react from "@vitejs/plugin-react"
import { readFile } from "node:fs/promises"
import stripJsonComments from "strip-json-comments"

const cwd = process.cwd()
const workspaceDir = cwd.startsWith("/workspace") ? "/workspace" : ".workspace"
const vitestSetupPath = `${workspaceDir}/frontend/vitest.setup.ts`
const serverFsAllow = [cwd]

const codeWorkspace = JSON.parse(
  stripJsonComments(
    await readFile(`${workspaceDir}/codeforlife.code-workspace`, "utf-8"),
  ),
) as Record<string, any>

// Read the service's package.json (not /workspace/frontend/package.json).
const packageJson = JSON.parse(await readFile("./package.json", "utf-8"))

const SERVICE_NAME = packageJson.name as string
const SERVICE_TITLE = SERVICE_NAME.replace(/(\s|_|-)+/g, " ")
  .trim()
  .split(" ")
  .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
  .join(" ")

function defineEnv(env: Record<string, string>) {
  return Object.entries(env).reduce(
    (vite_env, [key, value]) => {
      vite_env[`import.meta.env.VITE_${key}`] = value
      return vite_env
    },
    {} as Record<string, string>,
  )
}

export const viteConfig = defineViteConfig({
  plugins: [react()],
  envDir: "env",
  server: {
    // Automatically open the app in the browser on server start.
    open: true,
    // Listen on all addresses, including LAN and public addresses.
    host: true,
    watch: {
      // Don't watch for changes in unnecessary files.
      ignored: Object.keys(codeWorkspace.settings["files.watcherExclude"]),
    },
    fs: { allow: serverFsAllow },
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
  define: defineEnv({ SERVICE_NAME, SERVICE_TITLE }),
})

// TODO: investigate browser mode https://vitest.dev/guide/browser/
export const vitestConfig = defineVitestConfig({
  server: { fs: { allow: [...serverFsAllow, vitestSetupPath] } },
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
    setupFiles: [vitestSetupPath],
    // Automatically resets mocks before each test. This means any mock
    // implementation or mock call history is cleared, ensuring that the state
    // of your mocks from a previous test doesn't affect the next one.
    mockReset: true,
    // Only includes test files that match the expected naming convention.
    include: ["**/src/**/*.test.{j,t}s{x,}"],
    exclude: [...defaultTestExclude, "**/.workspace/**"],
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
