import { Form, Input, InputNumber } from "antd";

import { useSaveBottle } from "../../api/bottles";
import type { Bottle, BottleInput } from "../../api/types";
import { FormModal } from "../../components/FormModal";
import { TagSelect } from "../../components/TagSelect";
import { useFeedback } from "../../hooks/useFeedback";

interface BottleFormModalProps {
  open: boolean;
  bottle?: Bottle;
  onClose: () => void;
}

export function BottleFormModal({ open, bottle, onClose }: BottleFormModalProps) {
  const saveBottle = useSaveBottle();
  const feedback = useFeedback();

  const submit = (values: BottleInput) =>
    saveBottle.mutate(
      // Champs vides du formulaire → valeurs attendues par l'API (millésime absent, aucune étiquette)
      { id: bottle?.id, input: { ...values, vintage: values.vintage ?? null, tag_ids: values.tag_ids ?? [] } },
      {
        onSuccess: (saved) => {
          feedback.success(`Bouteille « ${saved.cuvee} » enregistrée`);
          onClose();
        },
        onError: feedback.error,
      },
    );

  return (
    <FormModal<BottleInput>
      title={bottle ? `Modifier « ${bottle.cuvee} »` : "Nouvelle bouteille"}
      open={open}
      initialValues={
        bottle && {
          cuvee: bottle.cuvee,
          domain: bottle.domain,
          vintage: bottle.vintage,
          tag_ids: bottle.tags.map((tag) => tag.id),
        }
      }
      confirmLoading={saveBottle.isPending}
      onCancel={onClose}
      onSubmit={submit}
    >
      <Form.Item label="Domaine" name="domain" rules={[{ required: true, whitespace: true, max: 100 }]}>
        <Input autoFocus placeholder="Olga Raffault" />
      </Form.Item>
      <Form.Item label="Cuvée" name="cuvee" rules={[{ required: true, whitespace: true, max: 100 }]}>
        <Input placeholder="Les Picasses" />
      </Form.Item>
      <Form.Item label="Millésime" name="vintage" extra="Laisser vide pour un vin non millésimé">
        <InputNumber min={1800} max={2100} precision={0} placeholder="2020" style={{ width: 140 }} />
      </Form.Item>
      <Form.Item label="Étiquettes" name="tag_ids">
        <TagSelect allowCreate placeholder="Type, garde, goûts, odeurs…" />
      </Form.Item>
    </FormModal>
  );
}
