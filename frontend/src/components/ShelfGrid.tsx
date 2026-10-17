import { Tooltip, Typography, theme } from "antd";

import type { ShelfDetail, ShelfPlacement } from "../api/types";

interface ShelfGridProps {
  shelf: ShelfDetail;
  /** Exemplaires mis en évidence (ex : ceux de la bouteille en cours d'édition). */
  highlightedBottleId?: string;
  /** Si fourni, les cases libres sont cliquables (pour y ranger ou déplacer une bouteille). */
  onFreeSlotClick?: (row: number, column: number) => void;
}

function bottleLabel(placement: ShelfPlacement): string {
  const { cuvee, domain, vintage } = placement.bottle;
  return `${cuvee} — ${domain}${vintage ? ` (${vintage})` : ""}`;
}

/** Vue de l'étagère : une case par emplacement, rangée 1 en haut. */
export function ShelfGrid({ shelf, highlightedBottleId, onFreeSlotClick }: ShelfGridProps) {
  const { token } = theme.useToken();
  const placementsBySlot = new Map(shelf.placements.map((p) => [`${p.row}-${p.column}`, p]));

  const cells = [];
  for (let row = 1; row <= shelf.rows; row++) {
    for (let column = 1; column <= shelf.columns; column++) {
      const placement = placementsBySlot.get(`${row}-${column}`);
      const highlighted = placement !== undefined && placement.bottle.id === highlightedBottleId;
      const clickable = placement === undefined && onFreeSlotClick !== undefined;

      const cell = (
        <div
          key={`${row}-${column}`}
          onClick={clickable ? () => onFreeSlotClick(row, column) : undefined}
          style={{
            minHeight: 56,
            padding: 4,
            borderRadius: token.borderRadius,
            border: `1px ${placement ? "solid" : "dashed"} ${highlighted ? token.colorPrimary : token.colorBorder}`,
            background: highlighted
              ? token.colorPrimaryBg
              : placement
                ? token.colorFillSecondary
                : token.colorBgContainer,
            cursor: clickable ? "pointer" : "default",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",
            overflow: "hidden",
          }}
        >
          <Typography.Text type="secondary" style={{ fontSize: 10 }}>
            {row}·{column}
          </Typography.Text>
          {placement && (
            <Typography.Text ellipsis style={{ fontSize: 12, maxWidth: "100%" }}>
              {placement.bottle.cuvee}
            </Typography.Text>
          )}
        </div>
      );

      cells.push(
        placement ? (
          <Tooltip key={`${row}-${column}`} title={bottleLabel(placement)}>
            {cell}
          </Tooltip>
        ) : clickable ? (
          <Tooltip key={`${row}-${column}`} title={`Ranger ici (rangée ${row}, case ${column})`}>
            {cell}
          </Tooltip>
        ) : (
          cell
        ),
      );
    }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: `repeat(${shelf.columns}, minmax(64px, 1fr))`, gap: 6 }}>
      {cells}
    </div>
  );
}
