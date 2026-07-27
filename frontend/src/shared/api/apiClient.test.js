import { afterEach, describe, expect, it, vi } from "vitest";

import {
  api,
  ApiClientError,
  buildApiUrl,
  resolveApiBaseUrl,
} from "./apiClient";

afterEach(() => {
  vi.restoreAllMocks();
  window.history.replaceState({}, "", "/");
});

describe("apiClient", () => {
  it("maps the structured backend error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({
          error: {
            code: "integrity_conflict",
            message: "Hay datos relacionados.",
            details: null,
          },
        }),
      }),
    );

    await expect(api.deleteLibrary(7)).rejects.toEqual(
      expect.objectContaining({
        name: "ApiClientError",
        status: 409,
        code: "integrity_conflict",
        message: "Hay datos relacionados.",
      }),
    );
  });

  it("returns null for successful no-content responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 204,
      }),
    );

    await expect(api.deleteIgnoredTerm(3)).resolves.toBeNull();
  });

  it("exports a typed client error", () => {
    expect(new ApiClientError("message", 400, "code")).toBeInstanceOf(Error);
  });

  it("uses the loopback backend URL supplied by Electron at runtime", async () => {
    window.history.replaceState(
      {},
      "",
      "/?apiBaseUrl=http%3A%2F%2F127.0.0.1%3A43125",
    );
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: "ok" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    vi.resetModules();
    const { api: runtimeApi } = await import("./apiClient");

    await runtimeApi.health();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:43125/api/health",
      expect.any(Object),
    );
  });

  it("rejects non-loopback and malformed backend URLs", () => {
    expect(
      resolveApiBaseUrl({
        search: "?apiBaseUrl=https%3A%2F%2Fexample.com",
      }),
    ).toBe("");
    expect(
      resolveApiBaseUrl({
        search: "?apiBaseUrl=not-a-url",
      }),
    ).toBe("");
    expect(buildApiUrl("/health", { search: "" })).toBe("/api/health");
  });
});
