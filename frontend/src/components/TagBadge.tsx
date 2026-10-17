import { Tag as AntTag, Tooltip } from "antd";

import type { Tag } from "../api/types";

/** Texte noir ou blanc selon la luminosité de la couleur de fond (lisibilité sur les couleurs claires). */
function readableTextColor(hex: string): string {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
  return luminance > 0.6 ? "rgba(0, 0, 0, 0.88)" : "#fff";
}

export function TagBadge({ tag }: { tag: Tag }) {
  return (
    <Tooltip title={tag.category.name}>
      {/* variant="solid" : fond plein de la couleur de l'étiquette (par défaut, antd n'applique qu'une teinte pâle) */}
      <AntTag
        color={tag.color}
        variant="solid"
        style={{ color: readableTextColor(tag.color), marginInlineEnd: 4 }}
      >
        {tag.name}
      </AntTag>
    </Tooltip>
  );
}
