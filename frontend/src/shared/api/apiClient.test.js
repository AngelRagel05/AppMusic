import { afterEach, describe, expect, it, vi } from "vitest";

import { api, ApiClientError } from "./apiClient";

afterEach(() => {
  vi.restoreAllMocks();
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
});
