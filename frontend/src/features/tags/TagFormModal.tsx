import { ColorPicker, Form, Input, Select } from "antd";
import type { ColorPickerProps } from "antd";

import { useSaveTag, useTagCategories } from "../../api/tags";
import type { Tag, TagInput } from "../../api/types";
import { FormModal } from "../../components/FormModal";
import { useFeedback } from "../../hooks/useFeedback";

// Même couleur par défaut que le backend
const DEFAULT_COLOR = "#9e9e9e";

const COLOR_PRESETS: ColorPickerProps["presets"] = [
  {
    label: "Vins",
    colors: ["#8e1b3a", "#5b1a2e", "#f3e5ab", "#f4a6b7", "#e67e22", "#d4af37"],
  },
  {
    label: "Autres",
    colors: ["#9e9e9e", "#27ae60", "#2980b9", "#8e44ad", "#c0392b", "#2c3e50"],
  },
];

interface TagFormModalProps {
  open: boolean;
  tag?: Tag;
  /** Catégorie présélectionnée à la création (ex : filtre actif dans la liste). */
  defaultCategoryId?: string;
  onClose: () => void;
}

export function TagFormModal({ open, tag, defaultCategoryId, onClose }: TagFormModalProps) {
  const { data: categories = [] } = useTagCategories();
  const saveTag = useSaveTag();
  const feedback = useFeedback();

  const submit = (input: TagInput) =>
    saveTag.mutate(
      { id: tag?.id, input },
      {
        onSuccess: (saved) => {
          feedback.success(`Étiquette « ${saved.name} » enregistrée`);
          onClose();
        },
        onError: feedback.error,
      },
    );

  return (
    <FormModal<TagInput>
      title={tag ? `Modifier l'étiquette « ${tag.name} »` : "Nouvelle étiquette"}
      open={open}
      initialValues={
        tag
          ? { name: tag.name, category_id: tag.category.id, color: tag.color }
          : { category_id: defaultCategoryId, color: DEFAULT_COLOR }
      }
      confirmLoading={saveTag.isPending}
      onCancel={onClose}
      onSubmit={submit}
    >
      <Form.Item label="Nom" name="name" rules={[{ required: true, whitespace: true, max: 50 }]}>
        <Input autoFocus placeholder="rouge, longue garde, fruité…" />
      </Form.Item>
      <Form.Item label="Catégorie" name="category_id" rules={[{ required: true }]}>
        <Select
          placeholder="Choisir une catégorie"
          options={categories.map((category) => ({ label: category.name, value: category.id }))}
        />
      </Form.Item>
      <Form.Item
        label="Couleur"
        name="color"
        rules={[{ required: true }]}
        // ColorPicker renvoie un objet couleur : le formulaire stocke directement le code #rrggbb attendu par l'API
        getValueFromEvent={(color) => color.toHexString()}
      >
        <ColorPicker disabledAlpha showText presets={COLOR_PRESETS} />
      </Form.Item>
    </FormModal>
  );
}
