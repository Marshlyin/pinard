import { Layout, Menu, Typography, theme } from "antd";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router";

import { BottlesPage } from "./features/bottles/BottlesPage";
import { ShelvesPage } from "./features/shelves/ShelvesPage";
import { TagsPage } from "./features/tags/TagsPage";

const SECTIONS = [
  { key: "/bottles", label: "Bouteilles" },
  { key: "/shelves", label: "Étagères" },
  { key: "/tags", label: "Étiquettes" },
];

export function App() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { token } = theme.useToken();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header style={{ display: "flex", alignItems: "center", gap: 32 }}>
        <Typography.Title level={4} style={{ color: "#fff", margin: 0, whiteSpace: "nowrap" }}>
          🍷 Pinard
        </Typography.Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={SECTIONS.filter((section) => pathname.startsWith(section.key)).map((s) => s.key)}
          items={SECTIONS}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Layout.Header>
      <Layout.Content style={{ padding: 24 }}>
        <div style={{ background: token.colorBgContainer, borderRadius: token.borderRadiusLG, padding: 24 }}>
          <Routes>
            <Route path="/bottles" element={<BottlesPage />} />
            <Route path="/shelves" element={<ShelvesPage />} />
            <Route path="/tags" element={<TagsPage />} />
            <Route path="*" element={<Navigate to="/bottles" replace />} />
          </Routes>
        </div>
      </Layout.Content>
    </Layout>
  );
}
