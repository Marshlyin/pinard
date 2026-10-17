import { Form, Modal } from "antd";
import type { ReactNode } from "react";

interface FormModalProps<T> {
  title: string;
  open: boolean;
  initialValues?: Partial<T>;
  confirmLoading?: boolean;
  onCancel: () => void;
  onSubmit: (values: T) => void;
  children: ReactNode;
}

/** Modale de création / édition : un formulaire antd validé par le bouton « Enregistrer » ou la touche Entrée. */
export function FormModal<T extends object>({
  title,
  open,
  initialValues,
  confirmLoading,
  onCancel,
  onSubmit,
  children,
}: FormModalProps<T>) {
  const [form] = Form.useForm<T>();

  return (
    <Modal
      title={title}
      open={open}
      okText="Enregistrer"
      cancelText="Annuler"
      confirmLoading={confirmLoading}
      onOk={() => form.submit()}
      onCancel={onCancel}
      destroyOnHidden
    >
      {/* preserve=false + destroyOnHidden : formulaire réinitialisé avec les bonnes valeurs à chaque ouverture */}
      <Form form={form} layout="vertical" initialValues={initialValues} preserve={false} onFinish={onSubmit}>
        {children}
        <button type="submit" hidden />
      </Form>
    </Modal>
  );
}
