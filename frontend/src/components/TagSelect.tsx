import { Select } from "antd";
import { useMemo } from "react";

import { useTags } from "../api/tags";
import type { Tag } from "../api/types";
import { TagBadge } from "./TagBadge";

interface TagSelectProps {
  value?: string[];
  onChange?: (tagIds: string[]) => void;
  placeholder?: string;
  style?: React.CSSProperties;
}

/** Sélection multiple d'étiquettes, groupées par catégorie. Utilisable seul ou dans un Form.Item. */
export function TagSelect({ value, onChange, placeholder = "Étiquettes", style }: TagSelectProps) {
  const { data: tags = [], isLoading } = useTags();

  const tagsById = useMemo(() => new Map(tags.map((tag) => [tag.id, tag])), [tags]);
  const options = useMemo(() => {
    const groups = new Map<string, { label: string; options: { label: string; value: string }[] }>();
    for (const tag of tags) {
      const group = groups.get(tag.category.id) ?? { label: tag.category.name, options: [] };
      group.options.push({ label: tag.name, value: tag.id });
      groups.set(tag.category.id, group);
    }
    return [...groups.values()];
  }, [tags]);

  return (
    <Select
      mode="multiple"
      allowClear
      showSearch={{ optionFilterProp: "label" }}
      loading={isLoading}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      options={options}
      style={style}
      tagRender={({ value: tagId, closable, onClose }) => {
        const tag: Tag | undefined = tagsById.get(tagId as string);
        return tag ? (
          <span onMouseDown={(event) => event.preventDefault()} onClick={closable ? onClose : undefined}>
            <TagBadge tag={tag} />
          </span>
        ) : (
          <span />
        );
      }}
    />
  );
}
