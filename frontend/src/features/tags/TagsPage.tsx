import { Tabs } from "antd";

import { TagCategoriesTab } from "./TagCategoriesTab";
import { TagsTab } from "./TagsTab";

export function TagsPage() {
  return (
    <Tabs
      items={[
        { key: "tags", label: "Étiquettes", children: <TagsTab /> },
        { key: "categories", label: "Catégories", children: <TagCategoriesTab /> },
      ]}
    />
  );
}
