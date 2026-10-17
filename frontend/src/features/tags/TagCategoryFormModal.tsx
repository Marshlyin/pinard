import { Form, Input } from "antd";

import { useSaveTagCategory } from "../../api/tags";
import type { TagCategory, TagCategoryInput } from "../../api/types";
import { FormModal } from "../../components/FormModal";
import { useFeedback } from "../../hooks/useFeedback";

interface TagCategoryFormModalProps {
  open: boolean;
  category?: TagCategory;
  onClose: () => void;
}

export function TagCategoryFormModal({ open, category, onClose }: TagCategoryFormModalProps) {
  const saveCategory = useSaveTagCategory();
  const feedback = useFeedback();

  const submit = (input: TagCategoryInput) =>
    saveCategory.mutate(
      { id: category?.id, input },
      {
        onSuccess: (saved) => {
          feedback.success(`Catégorie « ${saved.name} » enregistrée`);
          onClose();
        },
        onError: feedback.error,
      },
    );

  return (
    <FormModal<TagCategoryInput>
      title={category ? `Renommer la catégorie « ${category.name} »` : "Nouvelle catégorie"}
      open={open}
      initialValues={category}
      confirmLoading={saveCategory.isPending}
      onCancel={onClose}
      onSubmit={submit}
    >
      <Form.Item label="Nom" name="name" rules={[{ required: true, whitespace: true, max: 50 }]}>
        <Input autoFocus placeholder="Type, Garde, Goût, Odeur…" />
      </Form.Item>
    </FormModal>
  );
}
