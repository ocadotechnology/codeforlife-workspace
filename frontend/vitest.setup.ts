import { vi } from "vitest"

// Provides a set of custom jest matchers that you can use to extend jest.
// These will make your tests more declarative, clear to read and to maintain.
// https://github.com/testing-library/jest-dom?tab=readme-ov-file#with-vitest
import "@testing-library/jest-dom/vitest"

// Allows us to mock calls to fetch. This is useful whenever we're calling our
// API and needs to return predetermined HTTP status codes and response bodies.
// https://github.com/IanVS/vitest-fetch-mock?tab=readme-ov-file#vitest-fetch-mock
import createFetchMock from "vitest-fetch-mock"
const fetchMocker = createFetchMock(vi)
// Sets globalThis.fetch and globalThis.fetchMock to mocked version.
fetchMocker.enableMocks()
