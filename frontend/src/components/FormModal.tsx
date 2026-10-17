import { Form, Modal } from "antd";
import { type ReactNode, useId } from "react";

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
  const formId = useId();

  return (
    <Modal
      title={title}
      open={open}
      okText="Enregistrer"
      cancelText="Annuler"
      confirmLoading={confirmLoading}
      // Le bouton du pied de modale est hors du <form> : l'attribut HTML form="<id>" le rattache au formulaire
      okButtonProps={{ htmlType: "submit", form: formId }}
      onCancel={onCancel}
      destroyOnHidden
    >
      {/*
        Pas d'instance partagée (Form.useForm) : elle survivrait aux fermetures avec ses valeurs, qui l'emporteraient
        sur les nouvelles initialValues (la fiche précédente s'afficherait). Ici chaque ouverture crée un formulaire
        neuf (destroyOnHidden le détruit à la fermeture), initialisé avec les valeurs de la fiche ouverte.
      */}
      <Form<T> id={formId} layout="vertical" initialValues={initialValues} preserve={false} onFinish={onSubmit}>
        {children}
      </Form>
    </Modal>
  );
}
