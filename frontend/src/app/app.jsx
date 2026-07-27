import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "../shared/components/appShell/appShell";
import { ComparisonPage } from "../features/comparison/comparisonPage";
import { DownloadsPage } from "../features/downloads/downloadsPage";
import { MetadataPage } from "../features/metadata/metadataPage";

function HomeRedirect() {
  const lastModule = localStorage.getItem("soundshelf:lastModule");
  const target = ["/comparison", "/metadata", "/downloads"].includes(lastModule)
    ? lastModule
    : "/comparison";
  return <Navigate to={target} replace />;
}

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomeRedirect />} />
        <Route path="/comparison" element={<ComparisonPage />} />
        <Route path="/metadata" element={<MetadataPage />} />
        <Route path="/downloads" element={<DownloadsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
