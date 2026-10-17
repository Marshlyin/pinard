import { Form, Input, InputNumber, Space } from "antd";

import { useSaveShelf } from "../../api/shelves";
import type { Shelf, ShelfInput } from "../../api/types";
import { FormModal } from "../../components/FormModal";
import { useFeedback } from "../../hooks/useFeedback";

interface ShelfFormModalProps {
  open: boolean;
  /** Étagère à modifier, absente pour une création. */
  shelf?: Shelf;
  onClose: () => void;
}

export function ShelfFormModal({ open, shelf, onClose }: ShelfFormModalProps) {
  const saveShelf = useSaveShelf();
  const feedback = useFeedback();

  const submit = (input: ShelfInput) =>
    saveShelf.mutate(
      { id: shelf?.id, input },
      {
        onSuccess: (saved) => {
          feedback.success(`Étagère « ${saved.name} » enregistrée`);
          onClose();
        },
        onError: feedback.error,
      },
    );

  return (
    <FormModal<ShelfInput>
      title={shelf ? `Modifier l'étagère « ${shelf.name} »` : "Nouvelle étagère"}
      open={open}
      initialValues={shelf ?? { rows: 3, columns: 4 }}
      confirmLoading={saveShelf.isPending}
      onCancel={onClose}
      onSubmit={submit}
    >
      <Form.Item label="Nom" name="name" rules={[{ required: true, whitespace: true, max: 100 }]}>
        <Input autoFocus placeholder="Étagère du haut" />
      </Form.Item>
      <Space size="large">
        <Form.Item label="Rangées" name="rows" rules={[{ required: true }]}>
          <InputNumber min={1} max={50} precision={0} />
        </Form.Item>
        <Form.Item label="Cases par rangée" name="columns" rules={[{ required: true }]}>
          <InputNumber min={1} max={50} precision={0} />
        </Form.Item>
      </Space>
    </FormModal>
  );
}
