import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Popconfirm, Space, Table, Tooltip } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useDeleteTagCategory, useTagCategories } from "../../api/tags";
import type { TagCategory } from "../../api/types";
import { useFeedback } from "../../hooks/useFeedback";
import { TagCategoryFormModal } from "./TagCategoryFormModal";

export function TagCategoriesTab() {
  const { data: categories = [], isLoading } = useTagCategories();
  const deleteCategory = useDeleteTagCategory();
  const feedback = useFeedback();

  const [form, setForm] = useState<{ open: boolean; category?: TagCategory }>({ open: false });

  const remove = (category: TagCategory) =>
    deleteCategory.mutate(category.id, {
      onSuccess: () => feedback.success(`Catégorie « ${category.name} » supprimée`),
      onError: feedback.error,
    });

  const columns: TableProps<TagCategory>["columns"] = [
    { title: "Nom", dataIndex: "name", sorter: (a, b) => a.name.localeCompare(b.name) },
    {
      title: "Actions",
      key: "actions",
      width: 110,
      render: (_, category) => (
        <Space>
          <Tooltip title="Renommer">
            <Button icon={<EditOutlined />} onClick={() => setForm({ open: true, category })} />
          </Tooltip>
          <Popconfirm
            title={`Supprimer la catégorie « ${category.name} » ?`}
            description="Uniquement possible si elle ne contient aucune étiquette."
            okText="Supprimer"
            cancelText="Annuler"
            okButtonProps={{ danger: true }}
            onConfirm={() => remove(category)}
          >
            <Button danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Flex justify="end" style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setForm({ open: true })}>
          Nouvelle catégorie
        </Button>
      </Flex>

      <Table<TagCategory>
        rowKey="id"
        columns={columns}
        dataSource={categories}
        loading={isLoading}
        pagination={false}
      />

      <TagCategoryFormModal open={form.open} category={form.category} onClose={() => setForm({ open: false })} />
    </>
  );
}
