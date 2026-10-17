import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Input, Popconfirm, Space, Table, Tooltip } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useDeleteShelf, useShelves } from "../../api/shelves";
import type { Shelf } from "../../api/types";
import { useFeedback } from "../../hooks/useFeedback";
import { ShelfDetailModal } from "./ShelfDetailModal";
import { ShelfFormModal } from "./ShelfFormModal";

export function ShelvesPage() {
  const { data: shelves = [], isLoading } = useShelves();
  const deleteShelf = useDeleteShelf();
  const feedback = useFeedback();

  const [search, setSearch] = useState("");
  const [form, setForm] = useState<{ open: boolean; shelf?: Shelf }>({ open: false });
  const [detailShelfId, setDetailShelfId] = useState<string>();

  const filtered = shelves.filter((shelf) => shelf.name.toLowerCase().includes(search.trim().toLowerCase()));

  const remove = (shelf: Shelf) =>
    deleteShelf.mutate(shelf.id, {
      onSuccess: () => feedback.success(`Étagère « ${shelf.name} » supprimée`),
      onError: feedback.error,
    });

  const columns: TableProps<Shelf>["columns"] = [
    { title: "Nom", dataIndex: "name", sorter: (a, b) => a.name.localeCompare(b.name) },
    { title: "Forme", key: "shape", render: (_, shelf) => `${shelf.rows} rangées × ${shelf.columns} cases` },
    { title: "Capacité", dataIndex: "capacity", sorter: (a, b) => a.capacity - b.capacity },
    {
      title: "Actions",
      key: "actions",
      width: 140,
      render: (_, shelf) => (
        <Space>
          <Tooltip title="Voir le contenu">
            <Button icon={<EyeOutlined />} onClick={() => setDetailShelfId(shelf.id)} />
          </Tooltip>
          <Tooltip title="Modifier">
            <Button icon={<EditOutlined />} onClick={() => setForm({ open: true, shelf })} />
          </Tooltip>
          <Popconfirm
            title={`Supprimer l'étagère « ${shelf.name} » ?`}
            description="Uniquement possible si elle est vide."
            okText="Supprimer"
            cancelText="Annuler"
            okButtonProps={{ danger: true }}
            onConfirm={() => remove(shelf)}
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
        <Input.Search
          allowClear
          placeholder="Rechercher une étagère"
          onChange={(event) => setSearch(event.target.value)}
          style={{ maxWidth: 320 }}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setForm({ open: true })}>
          Nouvelle étagère
        </Button>
      </Flex>

      <Table<Shelf> rowKey="id" columns={columns} dataSource={filtered} loading={isLoading} pagination={false} />

      <ShelfFormModal open={form.open} shelf={form.shelf} onClose={() => setForm({ open: false })} />
      <ShelfDetailModal shelfId={detailShelfId} onClose={() => setDetailShelfId(undefined)} />
    </>
  );
}
