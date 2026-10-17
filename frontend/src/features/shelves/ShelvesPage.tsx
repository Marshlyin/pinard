import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Input, Table, Typography } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useDeleteShelf, useShelves } from "../../api/shelves";
import type { Shelf } from "../../api/types";
import { RowActions } from "../../components/RowActions";
import { useFeedback } from "../../hooks/useFeedback";
import { useIsMobile } from "../../hooks/useIsMobile";
import { ShelfDetailModal } from "./ShelfDetailModal";
import { ShelfFormModal } from "./ShelfFormModal";

const shapeOf = (shelf: Shelf) => `${shelf.rows} rangées × ${shelf.columns} cases`;

export function ShelvesPage() {
  const { data: shelves = [], isLoading } = useShelves();
  const deleteShelf = useDeleteShelf();
  const feedback = useFeedback();
  const isMobile = useIsMobile();

  const [search, setSearch] = useState("");
  const [form, setForm] = useState<{ open: boolean; shelf?: Shelf }>({ open: false });
  const [detailShelfId, setDetailShelfId] = useState<string>();

  const filtered = shelves.filter((shelf) => shelf.name.toLowerCase().includes(search.trim().toLowerCase()));

  const remove = (shelf: Shelf) =>
    deleteShelf.mutate(shelf.id, {
      onSuccess: () => feedback.success(`Étagère « ${shelf.name} » supprimée`),
      onError: feedback.error,
    });

  const actionsColumn: NonNullable<TableProps<Shelf>["columns"]>[number] = {
    title: isMobile ? undefined : "Actions",
    key: "actions",
    width: isMobile ? 56 : 140,
    render: (_, shelf) => (
      <RowActions
        actions={[
          { key: "view", label: "Voir le contenu", icon: <EyeOutlined />, onClick: () => setDetailShelfId(shelf.id) },
          { key: "edit", label: "Modifier", icon: <EditOutlined />, onClick: () => setForm({ open: true, shelf }) },
          {
            key: "delete",
            label: "Supprimer",
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => remove(shelf),
            confirm: {
              title: `Supprimer l'étagère « ${shelf.name} » ?`,
              description: "Uniquement possible si elle est vide.",
              okText: "Supprimer",
            },
          },
        ]}
      />
    ),
  };

  // Mobile : forme et capacité affichées sous le nom
  const columns: TableProps<Shelf>["columns"] = isMobile
    ? [
        {
          title: "Étagère",
          key: "shelf",
          sorter: (a, b) => a.name.localeCompare(b.name),
          render: (_, shelf) => (
            <Flex vertical>
              <Typography.Text strong>{shelf.name}</Typography.Text>
              <Typography.Text type="secondary">
                {shapeOf(shelf)} · {shelf.capacity} places
              </Typography.Text>
            </Flex>
          ),
        },
        actionsColumn,
      ]
    : [
        { title: "Nom", dataIndex: "name", sorter: (a, b) => a.name.localeCompare(b.name) },
        { title: "Forme", key: "shape", render: (_, shelf) => shapeOf(shelf) },
        { title: "Capacité", dataIndex: "capacity", sorter: (a, b) => a.capacity - b.capacity },
        actionsColumn,
      ];

  return (
    <>
      <Flex justify="space-between" gap="middle" wrap style={{ marginBottom: 16 }}>
        <Input.Search
          allowClear
          placeholder="Rechercher une étagère"
          onChange={(event) => setSearch(event.target.value)}
          style={{ flex: "1 1 220px", maxWidth: isMobile ? undefined : 320 }}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setForm({ open: true })} block={isMobile}>
          Nouvelle étagère
        </Button>
      </Flex>

      <Table<Shelf>
        rowKey="id"
        size={isMobile ? "small" : "middle"}
        columns={columns}
        dataSource={filtered}
        loading={isLoading}
        pagination={false}
      />

      <ShelfFormModal open={form.open} shelf={form.shelf} onClose={() => setForm({ open: false })} />
      <ShelfDetailModal shelfId={detailShelfId} onClose={() => setDetailShelfId(undefined)} />
    </>
  );
}
