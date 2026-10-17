import { MoreOutlined } from "@ant-design/icons";
import { App, Button, Dropdown, Popconfirm, Space, Tooltip } from "antd";
import type { ReactNode } from "react";

import { useIsMobile } from "../hooks/useIsMobile";

export interface RowAction {
  key: string;
  label: string;
  icon: ReactNode;
  onClick: () => void;
  danger?: boolean;
  /** Action mise en avant (ex : déplacement en cours). */
  active?: boolean;
  /** Demande une confirmation avant d'exécuter l'action. */
  confirm?: { title: string; description?: string; okText: string };
}

/**
 * Actions d'une ligne de tableau : boutons icônes (avec infobulle) sur ordinateur, menu « ⋯ » sur mobile pour ne pas
 * élargir le tableau.
 */
export function RowActions({ actions }: { actions: RowAction[] }) {
  const isMobile = useIsMobile();
  const { modal } = App.useApp();

  if (isMobile) {
    const run = (action: RowAction) =>
      action.confirm
        ? modal.confirm({
            title: action.confirm.title,
            content: action.confirm.description,
            okText: action.confirm.okText,
            okButtonProps: { danger: action.danger },
            cancelText: "Annuler",
            onOk: action.onClick,
          })
        : action.onClick();

    return (
      <Dropdown
        trigger={["click"]}
        menu={{
          items: actions.map(({ key, label, icon, danger }) => ({ key, label, icon, danger })),
          onClick: ({ key }) => run(actions.find((action) => action.key === key)!),
        }}
      >
        <Button icon={<MoreOutlined />} aria-label="Actions" />
      </Dropdown>
    );
  }

  return (
    <Space>
      {actions.map((action) => {
        const button = (
          <Button
            icon={action.icon}
            danger={action.danger}
            type={action.active ? "primary" : "default"}
            aria-label={action.label}
            onClick={action.confirm ? undefined : action.onClick}
          />
        );
        return action.confirm ? (
          <Popconfirm
            key={action.key}
            title={action.confirm.title}
            description={action.confirm.description}
            okText={action.confirm.okText}
            cancelText="Annuler"
            okButtonProps={{ danger: action.danger }}
            onConfirm={action.onClick}
          >
            <Tooltip title={action.label}>{button}</Tooltip>
          </Popconfirm>
        ) : (
          <Tooltip key={action.key} title={action.label}>
            {button}
          </Tooltip>
        );
      })}
    </Space>
  );
}
