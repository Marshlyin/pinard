import { BgColorsOutlined } from "@ant-design/icons";
import { Button, ColorPicker, Form, Input, Select, Space } from "antd";
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
  /** Nom pré-rempli à la création (ex : texte recherché dans un TagSelect). */
  defaultName?: string;
  /** Appelé avec l'étiquette enregistrée, avant la fermeture (ex : la cocher sur la bouteille en cours). */
  onSaved?: (tag: Tag) => void;
  onClose: () => void;
}

export function TagFormModal({ open, tag, defaultCategoryId, defaultName, onSaved, onClose }: TagFormModalProps) {
  const { data: categories = [] } = useTagCategories();
  const saveTag = useSaveTag();
  const feedback = useFeedback();

  const submit = (input: TagInput) =>
    saveTag.mutate(
      { id: tag?.id, input },
      {
        onSuccess: (saved) => {
          feedback.success(`Étiquette « ${saved.name} » enregistrée`);
          onSaved?.(saved);
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
          : { name: defaultName, category_id: defaultCategoryId, color: DEFAULT_COLOR }
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
          notFoundContent="Aucune catégorie : créez-en une dans la page Étiquettes"
          options={categories.map((category) => ({ label: category.name, value: category.id }))}
        />
      </Form.Item>
      <Form.Item label="Couleur" required>
        <Space>
          <Form.Item
            name="color"
            noStyle
            rules={[{ required: true }]}
            // ColorPicker renvoie un objet couleur : le formulaire stocke directement le code #rrggbb attendu par l'API
            getValueFromEvent={(color) => color.toHexString()}
          >
            <ColorPicker disabledAlpha showText presets={COLOR_PRESETS} />
          </Form.Item>
          <RandomColorButton />
        </Space>
      </Form.Item>
    </FormModal>
  );
}

/** Remplit le champ « color » du formulaire englobant avec une couleur tirée au hasard. */
function RandomColorButton() {
  const form = Form.useFormInstance<TagInput>();
  return (
    <Button icon={<BgColorsOutlined />} onClick={() => form.setFieldValue("color", randomColor())}>
      Aléatoire
    </Button>
  );
}

/**
 * Couleur aléatoire agréable : teinte libre, mais saturation et luminosité modérées (ni terne, ni fluo, ni quasi noire
 * ou blanche), pour qu'une étiquette reste lisible et se distingue des autres.
 */
function randomColor(): string {
  const hue = Math.random() * 360;
  const saturation = 0.45 + Math.random() * 0.35; // 45 – 80 %
  const lightness = 0.35 + Math.random() * 0.25; // 35 – 60 %
  return hslToHex(hue, saturation, lightness);
}

/** Conversion HSL → #rrggbb (teinte en degrés, saturation et luminosité entre 0 et 1). */
function hslToHex(hue: number, saturation: number, lightness: number): string {
  const amplitude = saturation * Math.min(lightness, 1 - lightness);
  const channel = (n: number) => {
    const k = (n + hue / 30) % 12;
    const value = lightness - amplitude * Math.max(-1, Math.min(k - 3, 9 - k, 1));
    return Math.round(value * 255)
      .toString(16)
      .padStart(2, "0");
  };
  return `#${channel(0)}${channel(8)}${channel(4)}`;
}
