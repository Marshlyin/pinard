import { Modal, Progress, Space, Spin, Typography } from "antd";

import { useShelf } from "../../api/shelves";
import { ShelfGrid } from "../../components/ShelfGrid";

interface ShelfDetailModalProps {
  shelfId?: string;
  onClose: () => void;
}

/** Contenu d'une étagère : grille des cases et bouteilles rangées. */
export function ShelfDetailModal({ shelfId, onClose }: ShelfDetailModalProps) {
  const { data: shelf, isLoading } = useShelf(shelfId);

  return (
    <Modal
      title={shelf ? `Étagère « ${shelf.name} »` : "Étagère"}
      open={shelfId !== undefined}
      onCancel={onClose}
      footer={null}
      width={900}
      destroyOnHidden
    >
      {isLoading || !shelf ? (
        <Spin />
      ) : (
        <Space orientation="vertical" size="middle" style={{ width: "100%" }}>
          <Space>
            <Typography.Text>
              {shelf.placements.length} / {shelf.capacity} bouteilles
            </Typography.Text>
            <Progress
              percent={Math.round((shelf.placements.length / shelf.capacity) * 100)}
              size="small"
              style={{ width: 200 }}
            />
          </Space>
          <ShelfGrid shelf={shelf} />
        </Space>
      )}
    </Modal>
  );
}
