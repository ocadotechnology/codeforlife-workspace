/// <reference types="vite/client" />

type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue }

declare module "*.jsonc" {
  const value: { [key: string]: JSONValue } | JSONValue[]
  export default value
}
