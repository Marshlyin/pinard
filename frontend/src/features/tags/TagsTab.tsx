import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Select, Table, Tooltip, Typography } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useDeleteTag, useTagCategories, useTags } from "../../api/tags";
import type { Tag } from "../../api/types";
import { RowActions } from "../../components/RowActions";
import { TagBadge } from "../../components/TagBadge";
import { useFeedback } from "../../hooks/useFeedback";
import { useIsMobile } from "../../hooks/useIsMobile";
import { TagFormModal } from "./TagFormModal";

export function TagsTab() {
  const [categoryId, setCategoryId] = useState<string>();
  const { data: tags = [], isLoading } = useTags(categoryId);
  const { data: categories = [] } = useTagCategories();
  const deleteTag = useDeleteTag();
  const feedback = useFeedback();
  const isMobile = useIsMobile();

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
      sorter: (a, b) => a.name.localeCompare(b.name),
      // Mobile : la catégorie est affichée sous l'étiquette (la colonne Catégorie est masquée)
      render: (_, tag) =>
        isMobile ? (
          <Flex vertical align="start" gap={2}>
            <TagBadge tag={tag} />
            <Typography.Text type="secondary">{tag.category.name}</Typography.Text>
          </Flex>
        ) : (
          <TagBadge tag={tag} />
        ),
    },
    ...(isMobile
      ? []
      : [
          {
            title: "Catégorie",
            key: "category",
            render: (_: unknown, tag: Tag) => tag.category.name,
            sorter: (a: Tag, b: Tag) => a.category.name.localeCompare(b.category.name),
          },
          {
            title: "Couleur",
            dataIndex: "color",
            render: (color: string) => <Typography.Text code>{color}</Typography.Text>,
          },
        ]),
    {
      title: isMobile ? undefined : "Actions",
      key: "actions",
      width: isMobile ? 56 : 110,
      render: (_, tag) => (
        <RowActions
          actions={[
            { key: "edit", label: "Modifier", icon: <EditOutlined />, onClick: () => setForm({ open: true, tag }) },
            {
              key: "delete",
              label: "Supprimer",
              icon: <DeleteOutlined />,
              danger: true,
              onClick: () => remove(tag),
              confirm: {
                title: `Supprimer l'étiquette « ${tag.name} » ?`,
                description: "Elle sera retirée de toutes les bouteilles.",
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
      <Flex justify="space-between" gap="middle" wrap style={{ marginBottom: 16 }}>
        <Select
          allowClear
          placeholder="Toutes les catégories"
          value={categoryId}
          onChange={setCategoryId}
          options={categories.map((category) => ({ label: category.name, value: category.id }))}
          style={{ flex: "1 1 220px", maxWidth: isMobile ? undefined : 280 }}
        />
        <Tooltip title={categories.length === 0 ? "Créez d'abord une catégorie" : undefined}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            disabled={categories.length === 0}
            onClick={() => setForm({ open: true })}
            block={isMobile}
          >
            Nouvelle étiquette
          </Button>
        </Tooltip>
      </Flex>

      <Table<Tag>
        rowKey="id"
        size={isMobile ? "small" : "middle"}
        columns={columns}
        dataSource={tags}
        loading={isLoading}
        pagination={false}
      />

      <TagFormModal
        open={form.open}
        tag={form.tag}
        defaultCategoryId={categoryId}
        onClose={() => setForm({ open: false })}
      />
    </>
  );
}
