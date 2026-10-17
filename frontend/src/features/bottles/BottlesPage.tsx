import { AppstoreOutlined, DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Flex, Input, Space, Switch, Table, Tooltip, Typography } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useBottles, useDeleteBottle } from "../../api/bottles";
import type { Bottle } from "../../api/types";
import { RowActions } from "../../components/RowActions";
import { TagBadge } from "../../components/TagBadge";
import { TagSelect } from "../../components/TagSelect";
import { useFeedback } from "../../hooks/useFeedback";
import { useIsMobile } from "../../hooks/useIsMobile";
import { BottleFormModal } from "./BottleFormModal";
import { BottlePlacementsModal } from "./BottlePlacementsModal";

const NO_VINTAGE = <Typography.Text type="secondary">—</Typography.Text>;

export function BottlesPage() {
  // Filtre par étiquettes : appliqué par le backend (OU dans une catégorie, ET entre catégories)
  const [tagIds, setTagIds] = useState<string[]>([]);
  const { data: bottles = [], isLoading } = useBottles(tagIds);
  const deleteBottle = useDeleteBottle();
  const feedback = useFeedback();
  const isMobile = useIsMobile();

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

  const tagsOf = (bottle: Bottle) => bottle.tags.map((tag) => <TagBadge key={tag.id} tag={tag} />);
  const quantityOf = (bottle: Bottle) =>
    bottle.quantity === 0 ? <Typography.Text type="secondary">0</Typography.Text> : bottle.quantity;

  const actionsColumn: NonNullable<TableProps<Bottle>["columns"]>[number] = {
    title: isMobile ? undefined : "Actions",
    key: "actions",
    width: isMobile ? 56 : 140,
    render: (_, bottle) => (
      <RowActions
        actions={[
          {
            key: "placements",
            label: "Emplacements (ranger, déplacer, retirer)",
            icon: <AppstoreOutlined />,
            onClick: () => setPlacementsBottleId(bottle.id),
          },
          { key: "edit", label: "Modifier", icon: <EditOutlined />, onClick: () => setForm({ open: true, bottle }) },
          {
            key: "delete",
            label: "Supprimer",
            icon: <DeleteOutlined />,
            danger: true,
            onClick: () => remove(bottle),
            confirm: {
              title: `Supprimer « ${bottle.cuvee} » ?`,
              description:
                bottle.quantity > 0
                  ? `Ses ${bottle.quantity} bouteille(s) rangée(s) seront retirées des étagères.`
                  : undefined,
              okText: "Supprimer",
            },
          },
        ]}
      />
    ),
  };

  // Mobile : une colonne « Vin » regroupe domaine, cuvée, millésime et étiquettes
  const columns: TableProps<Bottle>["columns"] = isMobile
    ? [
        {
          title: "Vin",
          key: "wine",
          sorter: (a, b) => a.domain.localeCompare(b.domain),
          render: (_, bottle) => (
            <Flex vertical gap={4}>
              <Typography.Text strong>{bottle.domain}</Typography.Text>
              <Typography.Text>
                {bottle.cuvee} · {bottle.vintage ?? NO_VINTAGE}
              </Typography.Text>
              {bottle.tags.length > 0 && <div>{tagsOf(bottle)}</div>}
            </Flex>
          ),
        },
        {
          title: "Qté",
          key: "quantity",
          width: 64,
          align: "center",
          sorter: (a, b) => a.quantity - b.quantity,
          render: (_, bottle) => quantityOf(bottle),
        },
        actionsColumn,
      ]
    : [
        { title: "Domaine", dataIndex: "domain", sorter: (a, b) => a.domain.localeCompare(b.domain) },
        { title: "Cuvée", dataIndex: "cuvee", sorter: (a, b) => a.cuvee.localeCompare(b.cuvee) },
        {
          title: "Millésime",
          dataIndex: "vintage",
          render: (vintage: number | null) => vintage ?? NO_VINTAGE,
          sorter: (a, b) => (a.vintage ?? 0) - (b.vintage ?? 0),
        },
        { title: "Étiquettes", key: "tags", render: (_, bottle) => tagsOf(bottle) },
        {
          title: "Quantité",
          key: "quantity",
          sorter: (a, b) => a.quantity - b.quantity,
          render: (_, bottle) => quantityOf(bottle),
        },
        actionsColumn,
      ];

  return (
    <>
      <Flex justify="space-between" gap="middle" wrap style={{ marginBottom: 16 }}>
        <Flex gap="middle" wrap align="center" style={{ flex: "1 1 auto" }}>
          {/* flex-basis : côte à côte sur grand écran, l'un sous l'autre (pleine largeur) sur mobile */}
          <Input.Search
            allowClear
            placeholder="Domaine ou cuvée"
            onChange={(event) => setSearch(event.target.value)}
            style={{ flex: "1 1 220px", maxWidth: isMobile ? undefined : 260 }}
          />
          <Tooltip title="OU entre les étiquettes d'une même catégorie, ET entre les catégories">
            <div style={{ flex: "1 1 260px", maxWidth: isMobile ? undefined : 360 }}>
              <TagSelect
                value={tagIds}
                onChange={setTagIds}
                placeholder="Filtrer par étiquettes"
                style={{ width: "100%" }}
              />
            </div>
          </Tooltip>
          <Space>
            <Switch checked={inStockOnly} onChange={setInStockOnly} />
            En stock uniquement
          </Space>
        </Flex>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setForm({ open: true })}
          block={isMobile}
        >
          Nouvelle bouteille
        </Button>
      </Flex>

      <Table<Bottle>
        rowKey="id"
        size={isMobile ? "small" : "middle"}
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
