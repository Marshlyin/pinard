import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Popconfirm, Select, Space, Table, Tooltip, Typography } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useDeleteTag, useTagCategories, useTags } from "../../api/tags";
import type { Tag } from "../../api/types";
import { TagBadge } from "../../components/TagBadge";
import { useFeedback } from "../../hooks/useFeedback";
import { TagFormModal } from "./TagFormModal";

export function TagsTab() {
  const [categoryId, setCategoryId] = useState<string>();
  const { data: tags = [], isLoading } = useTags(categoryId);
  const { data: categories = [] } = useTagCategories();
  const deleteTag = useDeleteTag();
  const feedback = useFeedback();

  const [form, setForm] = useState<{ open: boolean; tag?: Tag }>({ open: false });

  const remove = (tag: Tag) =>
    deleteTag.mutate(tag.id, {
      onSuccess: () => feedback.success(`Étiquette « ${tag.name} » supprimée`),
      onError: feedback.error,
    });

  const columns: TableProps<Tag>["columns"] = [
    {
      title: "Étiquette",
      key: "name",
      render: (_, tag) => <TagBadge tag={tag} />,
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: "Catégorie",
      key: "category",
      render: (_, tag) => tag.category.name,
      sorter: (a, b) => a.category.name.localeCompare(b.category.name),
    },
    {
      title: "Couleur",
      dataIndex: "color",
      render: (color: string) => <Typography.Text code>{color}</Typography.Text>,
    },
    {
      title: "Actions",
      key: "actions",
      width: 110,
      render: (_, tag) => (
        <Space>
          <Tooltip title="Modifier">
            <Button icon={<EditOutlined />} onClick={() => setForm({ open: true, tag })} />
          </Tooltip>
          <Popconfirm
            title={`Supprimer l'étiquette « ${tag.name} » ?`}
            description="Elle sera retirée de toutes les bouteilles."
            okText="Supprimer"
            cancelText="Annuler"
            okButtonProps={{ danger: true }}
            onConfirm={() => remove(tag)}
          >
            <Button danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Flex justify="space-between" gap="middle" wrap style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Toutes les catégories"
          value={categoryId}
          onChange={setCategoryId}
          options={categories.map((category) => ({ label: category.name, value: category.id }))}
          style={{ minWidth: 240 }}
        />
        <Tooltip title={categories.length === 0 ? "Créez d'abord une catégorie" : undefined}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            disabled={categories.length === 0}
            onClick={() => setForm({ open: true })}
          >
            Nouvelle étiquette
          </Button>
        </Tooltip>
      </Flex>

      <Table<Tag> rowKey="id" columns={columns} dataSource={tags} loading={isLoading} pagination={false} />

      <TagFormModal
        open={form.open}
        tag={form.tag}
        defaultCategoryId={categoryId}
        onClose={() => setForm({ open: false })}
      />
    </>
  );
}
