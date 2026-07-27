import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./app";

function renderApp(path = "/metadata") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
        initialEntries={[path]}
      >
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  localStorage.clear();
});

describe("App", () => {
  it("renders the three tool destinations in the persistent sidebar", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    );

    renderApp();

    expect(screen.getByRole("link", { name: /comparación/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /metadata/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /descargas/i })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Editor de metadata" }),
    ).toBeInTheDocument();
  });

  it("redirects the root route to the last visited module", async () => {
    localStorage.setItem("soundshelf:lastModule", "/downloads");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    );

    renderApp("/");

    expect(
      await screen.findByRole("heading", { name: "Descargas de audio" }),
    ).toBeInTheDocument();
  });

  it("persists the collapsed sidebar preference", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [],
      }),
    );

    renderApp();
    fireEvent.click(
      screen.getByRole("button", { name: "Contraer barra lateral" }),
    );

    expect(localStorage.getItem("soundshelf:sidebarCollapsed")).toBe("true");
    expect(
      screen.getByRole("button", { name: "Expandir barra lateral" }),
    ).toBeInTheDocument();
  });

  it("loads selectable missing items from a comparison id", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation(async (path) => {
        let body = [];
        if (path.includes("/capabilities")) {
          body = {
            ffmpegAvailable: true,
            ytDlpAvailable: true,
            metadataEditingAvailable: true,
            taskPollIntervalMs: 1000,
          };
        } else if (path.includes("/libraries")) {
          body = [
            {
              id: 3,
              displayName: "Biblioteca",
              path: "C:/Music",
              isActive: true,
            },
          ];
        } else if (path.includes("/comparisons/42")) {
          body = {
            items: [
              {
                youtubePlaylistItemId: 9,
                youtubeTitle: "Missing Song",
                youtubeArtist: "Artist",
                comparisonStatus: "missing",
              },
            ],
            total: 1,
            page: 1,
            pageSize: 100,
          };
        }
        return {
          ok: true,
          status: 200,
          json: async () => body,
        };
      }),
    );

    renderApp("/downloads?comparisonId=42");

    expect(
      await screen.findByRole("checkbox", { name: /missing song/i }),
    ).toBeChecked();
    expect(
      screen.getByRole("heading", {
        name: "Faltantes de la comparación #42",
      }),
    ).toBeInTheDocument();
  });
});
