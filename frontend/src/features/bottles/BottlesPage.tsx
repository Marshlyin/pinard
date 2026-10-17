import { AppstoreOutlined, DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Input, Popconfirm, Space, Switch, Table, Tooltip, Typography } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useBottles, useDeleteBottle } from "../../api/bottles";
import type { Bottle } from "../../api/types";
import { TagBadge } from "../../components/TagBadge";
import { TagSelect } from "../../components/TagSelect";
import { useFeedback } from "../../hooks/useFeedback";
import { BottleFormModal } from "./BottleFormModal";
import { BottlePlacementsModal } from "./BottlePlacementsModal";

export function BottlesPage() {
  // Filtre par étiquettes : appliqué par le backend (OU dans une catégorie, ET entre catégories)
  const [tagIds, setTagIds] = useState<string[]>([]);
  const { data: bottles = [], isLoading } = useBottles(tagIds);
  const deleteBottle = useDeleteBottle();
  const feedback = useFeedback();

  // Filtres appliqués localement
  const [search, setSearch] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);

  const [form, setForm] = useState<{ open: boolean; bottle?: Bottle }>({ open: false });
  const [placementsBottleId, setPlacementsBottleId] = useState<string>();

  const searchText = search.trim().toLowerCase();
  const filtered = bottles.filter(
    (bottle) =>
      (!inStockOnly || bottle.quantity > 0) &&
      (bottle.cuvee.toLowerCase().includes(searchText) || bottle.domain.toLowerCase().includes(searchText)),
  );
  const totalQuantity = filtered.reduce((total, bottle) => total + bottle.quantity, 0);

  const remove = (bottle: Bottle) =>
    deleteBottle.mutate(bottle.id, {
      onSuccess: () => feedback.success(`Bouteille « ${bottle.cuvee} » supprimée`),
      onError: feedback.error,
    });

  const columns: TableProps<Bottle>["columns"] = [
    { title: "Domaine", dataIndex: "domain", sorter: (a, b) => a.domain.localeCompare(b.domain) },
    { title: "Cuvée", dataIndex: "cuvee", sorter: (a, b) => a.cuvee.localeCompare(b.cuvee) },
    {
      title: "Millésime",
      dataIndex: "vintage",
      render: (vintage: number | null) => vintage ?? <Typography.Text type="secondary">—</Typography.Text>,
      sorter: (a, b) => (a.vintage ?? 0) - (b.vintage ?? 0),
    },
    {
      title: "Étiquettes",
      key: "tags",
      render: (_, bottle) => bottle.tags.map((tag) => <TagBadge key={tag.id} tag={tag} />),
    },
    {
      title: "Quantité",
      dataIndex: "quantity",
      sorter: (a, b) => a.quantity - b.quantity,
      render: (quantity: number) => (quantity === 0 ? <Typography.Text type="secondary">0</Typography.Text> : quantity),
    },
    {
      title: "Actions",
      key: "actions",
      width: 140,
      render: (_, bottle) => (
        <Space>
          <Tooltip title="Emplacements (ranger, déplacer, retirer)">
            <Button icon={<AppstoreOutlined />} onClick={() => setPlacementsBottleId(bottle.id)} />
          </Tooltip>
          <Tooltip title="Modifier">
            <Button icon={<EditOutlined />} onClick={() => setForm({ open: true, bottle })} />
          </Tooltip>
          <Popconfirm
            title={`Supprimer « ${bottle.cuvee} » ?`}
            description={
              bottle.quantity > 0
                ? `Ses ${bottle.quantity} bouteille(s) rangée(s) seront retirées des étagères.`
                : undefined
            }
            okText="Supprimer"
            cancelText="Annuler"
            okButtonProps={{ danger: true }}
            onConfirm={() => remove(bottle)}
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
        <Flex gap="middle" wrap align="center">
          <Input.Search
            allowClear
            placeholder="Domaine ou cuvée"
            onChange={(event) => setSearch(event.target.value)}
            style={{ width: 240 }}
          />
          <Tooltip title="OU entre les étiquettes d'une même catégorie, ET entre les catégories">
            <span>
              <TagSelect value={tagIds} onChange={setTagIds} placeholder="Filtrer par étiquettes" style={{ minWidth: 300 }} />
            </span>
          </Tooltip>
          <Space>
            <Switch checked={inStockOnly} onChange={setInStockOnly} />
            En stock uniquement
          </Space>
        </Flex>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setForm({ open: true })}>
          Nouvelle bouteille
        </Button>
      </Flex>

      <Table<Bottle>
        rowKey="id"
        columns={columns}
        dataSource={filtered}
        loading={isLoading}
        pagination={{ pageSize: 50, hideOnSinglePage: true }}
        footer={() => `${filtered.length} référence(s), ${totalQuantity} bouteille(s) rangée(s)`}
      />

      <BottleFormModal open={form.open} bottle={form.bottle} onClose={() => setForm({ open: false })} />
      <BottlePlacementsModal bottleId={placementsBottleId} onClose={() => setPlacementsBottleId(undefined)} />
    </>
  );
}
