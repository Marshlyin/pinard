import { Tag as AntTag, Tooltip } from "antd";

import type { Tag } from "../api/types";
import { useIsMobile } from "../hooks/useIsMobile";

/** Texte noir ou blanc selon la luminosité de la couleur de fond (lisibilité sur les couleurs claires). */
function readableTextColor(hex: string): string {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
  const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
  return luminance > 0.6 ? "rgba(0, 0, 0, 0.88)" : "#fff";
}

interface TagBadgeProps {
  tag: Tag;
  /** Affiche une croix de suppression (ex : étiquette choisie dans un TagSelect). */
  onClose?: () => void;
}

export function TagBadge({ tag, onClose }: TagBadgeProps) {
  const isMobile = useIsMobile();
  const textColor = readableTextColor(tag.color);

  const badge = (
    // variant="solid" : fond plein de la couleur de l'étiquette (par défaut, antd n'applique qu'une teinte pâle)
    <AntTag
      color={tag.color}
      variant="solid"
      closable={onClose !== undefined}
      onClose={(event) => {
        event.preventDefault();
        onClose?.();
      }}
      styles={{ close: { color: textColor } }}
      style={{ color: textColor, marginInlineEnd: 4 }}
    >
      {tag.name}
    </AntTag>
  );

  // Pas d'infobulle sur écran tactile : sans survol, elle s'afficherait au toucher et resterait par-dessus le contenu
  return isMobile ? badge : <Tooltip title={tag.category.name}>{badge}</Tooltip>;
}
