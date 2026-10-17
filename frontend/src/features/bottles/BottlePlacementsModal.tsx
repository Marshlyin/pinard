import { DeleteOutlined, DragOutlined } from "@ant-design/icons";
import { Alert, Button, Divider, Empty, Modal, Popconfirm, Select, Space, Spin, Table, Tooltip, Typography } from "antd";
import type { TableProps } from "antd";
import { useState } from "react";

import { useAddPlacement, useBottle, useMovePlacement, useRemovePlacement } from "../../api/bottles";
import { useShelf, useShelves } from "../../api/shelves";
import type { BottleLocation } from "../../api/types";
import { ShelfGrid } from "../../components/ShelfGrid";
import { useFeedback } from "../../hooks/useFeedback";

interface BottlePlacementsModalProps {
  bottleId?: string;
  onClose: () => void;
}

/**
 * Bouteilles physiques d'une référence : liste des emplacements, et grille d'une étagère pour ranger un nouvel
 * exemplaire ou déplacer un exemplaire existant (clic sur une case libre).
 */
export function BottlePlacementsModal({ bottleId, onClose }: BottlePlacementsModalProps) {
  const { data: bottle, isLoading } = useBottle(bottleId);
  const { data: shelves = [] } = useShelves();
  const [shelfId, setShelfId] = useState<string>();
  const { data: shelf } = useShelf(shelfId);
  const [movingPlacement, setMovingPlacement] = useState<BottleLocation>();

  const addPlacement = useAddPlacement();
  const movePlacement = useMovePlacement();
  const removePlacement = useRemovePlacement();
  const feedback = useFeedback();

  const close = () => {
    setShelfId(undefined);
    setMovingPlacement(undefined);
    onClose();
  };

  const onFreeSlotClick = (row: number, column: number) => {
    if (!bottle || !shelf) return;
    const input = { shelf_id: shelf.id, row, column };
    const slot = `« ${shelf.name} », rangée ${row}, case ${column}`;

    if (movingPlacement) {
      movePlacement.mutate(
        { bottleId: bottle.id, placementId: movingPlacement.id, input },
        {
          onSuccess: () => {
            feedback.success(`Bouteille déplacée dans ${slot}`);
            setMovingPlacement(undefined);
          },
          onError: feedback.error,
        },
      );
    } else {
      addPlacement.mutate(
        { bottleId: bottle.id, input },
        { onSuccess: () => feedback.success(`Bouteille rangée dans ${slot}`), onError: feedback.error },
      );
    }
  };

  const remove = (placement: BottleLocation) =>
    removePlacement.mutate(
      { bottleId: bottleId!, placementId: placement.id },
      { onSuccess: () => feedback.success("Bouteille retirée"), onError: feedback.error },
    );

  const columns: TableProps<BottleLocation>["columns"] = [
    { title: "Étagère", key: "shelf", render: (_, placement) => placement.shelf.name },
    { title: "Rangée", dataIndex: "row" },
    { title: "Case", dataIndex: "column" },
    {
      title: "Actions",
      key: "actions",
      width: 110,
      render: (_, placement) => (
        <Space>
          <Tooltip title="Déplacer">
            <Button
              icon={<DragOutlined />}
              type={movingPlacement?.id === placement.id ? "primary" : "default"}
              onClick={() => {
                setMovingPlacement(placement);
                setShelfId(shelfId ?? placement.shelf.id);
              }}
            />
          </Tooltip>
          <Popconfirm
            title="Retirer cette bouteille ?"
            description="Bouteille bue ou sortie de la cave."
            okText="Retirer"
            cancelText="Annuler"
            onConfirm={() => remove(placement)}
          >
            <Button danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Modal
      title={bottle ? `Emplacements de « ${bottle.cuvee} » (${bottle.domain})` : "Emplacements"}
      open={bottleId !== undefined}
      onCancel={close}
      footer={null}
      width={900}
      destroyOnHidden
    >
      {isLoading || !bottle ? (
        <Spin />
      ) : (
        <>
          <Table<BottleLocation>
            rowKey="id"
            size="small"
            columns={columns}
            dataSource={bottle.placements}
            pagination={false}
            locale={{ emptyText: <Empty description="Aucune bouteille rangée" /> }}
          />

          <Divider titlePlacement="start">
            {movingPlacement ? "Déplacer une bouteille" : "Ranger une bouteille"}
          </Divider>

          <Space orientation="vertical" size="middle" style={{ width: "100%" }}>
            {movingPlacement && (
              <Alert
                type="info"
                showIcon
                title={`Déplacement de la bouteille rangée dans « ${movingPlacement.shelf.name} », rangée ${movingPlacement.row}, case ${movingPlacement.column} : cliquez sur une case libre.`}
                action={
                  <Button size="small" onClick={() => setMovingPlacement(undefined)}>
                    Annuler
                  </Button>
                }
              />
            )}
            <Select
              placeholder="Choisir une étagère"
              value={shelfId}
              onChange={setShelfId}
              options={shelves.map((s) => ({ label: `${s.name} (${s.rows} × ${s.columns})`, value: s.id }))}
              style={{ minWidth: 280 }}
            />
            {shelf && (
              <>
                <Typography.Text type="secondary">
                  Cliquez sur une case libre pour y {movingPlacement ? "déplacer" : "ranger"} la bouteille. Les
                  exemplaires de cette bouteille sont mis en évidence.
                </Typography.Text>
                <ShelfGrid shelf={shelf} highlightedBottleId={bottle.id} onFreeSlotClick={onFreeSlotClick} />
              </>
            )}
          </Space>
        </>
      )}
    </Modal>
  );
}
