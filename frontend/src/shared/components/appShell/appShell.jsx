import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import styles from "./appShell.module.css";

const navigation = [
  {
    to: "/comparison",
    label: "Comparación",
    description: "Cruza playlist y biblioteca",
    icon: "compare",
  },
  {
    to: "/metadata",
    label: "Metadata",
    description: "Revisa y edita tags MP3",
    icon: "tag",
  },
  {
    to: "/downloads",
    label: "Descargas",
    description: "Gestiona la cola local",
    icon: "download",
  },
];

function NavigationIcon({ name }) {
  const paths = {
    compare: (
      <>
        <path d="M7 7h11M15 4l3 3-3 3" />
        <path d="M17 17H6M9 14l-3 3 3 3" />
      </>
    ),
    tag: (
      <>
        <path d="M4 5v6l8 8 7-7-8-8H5a1 1 0 0 0-1 1Z" />
        <circle cx="8.5" cy="8.5" r="1.25" />
      </>
    ),
    download: (
      <>
        <path d="M12 3v12M7.5 10.5 12 15l4.5-4.5" />
        <path d="M5 20h14" />
      </>
    ),
  };
  return (
    <svg
      aria-hidden="true"
      className={styles.navIcon}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {paths[name]}
    </svg>
  );
}

export function AppShell() {
  const location = useLocation();
  const sidebarRef = useRef(null);
  const previousFocusRef = useRef(null);
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem("soundshelf:sidebarCollapsed") === "true",
  );
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem("soundshelf:sidebarCollapsed", String(collapsed));
  }, [collapsed]);

  useEffect(() => {
    if (["/comparison", "/metadata", "/downloads"].includes(location.pathname)) {
      localStorage.setItem("soundshelf:lastModule", location.pathname);
    }
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!mobileOpen) {
      previousFocusRef.current?.focus?.();
      return undefined;
    }
    previousFocusRef.current = document.activeElement;
    const sidebar = sidebarRef.current;
    const focusable = sidebar?.querySelectorAll(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
    );
    focusable?.[0]?.focus();

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setMobileOpen(false);
        return;
      }
      if (event.key !== "Tab" || !focusable?.length) {
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [mobileOpen]);

  return (
    <div className={styles.shell}>
      {mobileOpen && (
        <button
          aria-label="Cerrar navegación"
          className={styles.backdrop}
          onClick={() => setMobileOpen(false)}
          type="button"
        />
      )}
      <aside
        aria-label="Navegación principal"
        className={[
          styles.sidebar,
          collapsed ? styles.collapsed : "",
          mobileOpen ? styles.mobileOpen : "",
        ].join(" ")}
        ref={sidebarRef}
      >
        <div className={styles.brand}>
          <div className={styles.brandMark} aria-hidden="true">
            S
          </div>
          <div className={styles.brandCopy}>
            <strong>SoundShelf</strong>
            <span>Music toolkit</span>
          </div>
        </div>

        <nav className={styles.navigation}>
          <span className={styles.navEyebrow}>Herramientas</span>
          {navigation.map((item) => (
            <NavLink
              className={({ isActive }) =>
                `${styles.navLink} ${isActive ? styles.active : ""}`
              }
              key={item.to}
              to={item.to}
              title={collapsed ? item.label : undefined}
            >
              <NavigationIcon name={item.icon} />
              <span className={styles.navCopy}>
                <strong>{item.label}</strong>
                <small>{item.description}</small>
              </span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.localBadge}>
            <span />
            <div>
              <strong>Solo local</strong>
              <small>127.0.0.1</small>
            </div>
          </div>
          <button
            aria-label={collapsed ? "Expandir barra lateral" : "Contraer barra lateral"}
            className={styles.collapseButton}
            onClick={() => setCollapsed((value) => !value)}
            type="button"
          >
            <span aria-hidden="true">{collapsed ? "›" : "‹"}</span>
            <span className={styles.collapseLabel}>Contraer</span>
          </button>
        </div>
      </aside>

      <div className={styles.workspace}>
        <header className={styles.mobileHeader}>
          <button
            aria-expanded={mobileOpen}
            aria-label="Abrir navegación"
            className={styles.mobileMenu}
            onClick={() => setMobileOpen(true)}
            type="button"
          >
            <span />
            <span />
            <span />
          </button>
          <strong>SoundShelf</strong>
          <span className={styles.mobileStatus}>Local</span>
        </header>
        <main className={styles.main} id="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
