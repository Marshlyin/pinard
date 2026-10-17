import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Table } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useDeleteTagCategory, useTagCategories } from "../../api/tags";
import type { TagCategory } from "../../api/types";
import { RowActions } from "../../components/RowActions";
import { useFeedback } from "../../hooks/useFeedback";
import { useIsMobile } from "../../hooks/useIsMobile";
import { TagCategoryFormModal } from "./TagCategoryFormModal";

export function TagCategoriesTab() {
  const { data: categories = [], isLoading } = useTagCategories();
  const deleteCategory = useDeleteTagCategory();
  const feedback = useFeedback();
  const isMobile = useIsMobile();

  const [form, setForm] = useState<{ open: boolean; category?: TagCategory }>({ open: false });

  const remove = (category: TagCategory) =>
    deleteCategory.mutate(category.id, {
      onSuccess: () => feedback.success(`Catégorie « ${category.name} » supprimée`),
      onError: feedback.error,
    });

  const columns: TableProps<TagCategory>["columns"] = [
    { title: "Nom", dataIndex: "name", sorter: (a, b) => a.name.localeCompare(b.name) },
    {
      title: isMobile ? undefined : "Actions",
      key: "actions",
      width: isMobile ? 56 : 110,
      render: (_, category) => (
        <RowActions
          actions={[
            {
              key: "edit",
              label: "Renommer",
              icon: <EditOutlined />,
              onClick: () => setForm({ open: true, category }),
            },
            {
              key: "delete",
              label: "Supprimer",
              icon: <DeleteOutlined />,
              danger: true,
              onClick: () => remove(category),
              confirm: {
                title: `Supprimer la catégorie « ${category.name} » ?`,
                description: "Uniquement possible si elle ne contient aucune étiquette.",
                okText: "Supprimer",
              },
            },
          ]}
        />
      ),
    },
  ];

  return (
    <>
      <Flex justify="end" style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setForm({ open: true })} block={isMobile}>
          Nouvelle catégorie
        </Button>
      </Flex>

      <Table<TagCategory>
        rowKey="id"
        size={isMobile ? "small" : "middle"}
        columns={columns}
        dataSource={categories}
        loading={isLoading}
        pagination={false}
      />

      <TagCategoryFormModal open={form.open} category={form.category} onClose={() => setForm({ open: false })} />
    </>
  );
}
