import js from "@eslint/js"
import globals from "globals"
import react from "eslint-plugin-react"
import reactHooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"
import eslintConfigPrettier from "eslint-config-prettier/flat"
import ts from "typescript-eslint"

// Base off of:
// https://github.com/vitejs/vite/blob/main/packages/create-vite/template-react-ts/eslint.config.js
export default ts.config(
  {
    // https://eslint.org/docs/latest/use/configure/configuration-files#globally-ignoring-files-with-ignores
    ignores: ["dist", "**/*.d.ts", "eslint.config.js", "server.js"],
  },
  {
    files: ["**/*.{js,mjs,cjs,jsx,mjsx,ts,tsx,mtsx}"],
    extends: [
      // Recommended config for JavaScript.
      // https://www.npmjs.com/package/@eslint/js
      js.configs.recommended,
      // Recommended config for TypeScript.
      // https://typescript-eslint.io/users/configs/#recommended-type-checked
      ...ts.configs.recommendedTypeChecked,
      // Recommended config for React.
      // https://github.com/jsx-eslint/eslint-plugin-react?tab=readme-ov-file#flat-configs
      react.configs.flat.recommended,
      react.configs.flat["jsx-runtime"], // Add when using React 17+
      // Enforces the rules of react hooks.
      // https://www.npmjs.com/package/eslint-plugin-react-hooks
      reactHooks.configs["recommended-latest"],
      // Enforces that your components are structured in a way that support HMR.
      // https://www.npmjs.com/package/eslint-plugin-react-refresh
      reactRefresh.configs.vite,
      // Turns off all rules that might conflict with Prettier.
      // https://www.npmjs.com/package/eslint-config-prettier
      eslintConfigPrettier,
    ],
    settings: { react: { version: "18.3" } },
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
      parser: ts.parser,
      parserOptions: {
        // Expects each submodule to have theses tsconfigs present in the root.
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
      },
    },
    rules: {
      "sort-imports": ["error", { allowSeparatedGroups: true }],
      "@typescript-eslint/no-empty-object-type": "off",
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { fixStyle: "inline-type-imports" },
      ],
      "@typescript-eslint/no-restricted-imports": [
        "error",
        {
          paths: [
            {
              name: "react-redux",
              importNames: ["useSelector", "useStore", "useDispatch"],
              message:
                "Please use pre-typed versions from `src/app/hooks.ts` instead.",
            },
          ],
          patterns: [
            {
              group: ["codeforlife/src"],
              message: "Please use `codeforlife` instead of `codeforlife/src`.",
            },
          ],
        },
      ],
    },
  },
)
