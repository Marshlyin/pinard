import { Tag as AntTag, Select } from "antd";
import { useMemo } from "react";

import { useTags } from "../api/tags";
import { useIsMobile } from "../hooks/useIsMobile";
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
  const isMobile = useIsMobile();

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
      loading={isLoading}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      options={options}
      style={style}
      // Sur mobile (iOS en particulier) :
      // - pas de recherche : le clavier qui s'ouvre réduit l'écran et fait sauter la liste ;
      // - défilement natif plutôt que la liste virtuelle d'antd, qui gère mal les gestes tactiles (liste bloquée) ;
      // - champ sur une seule ligne (« +N ») : il ne grandit plus à chaque sélection, la liste ouverte ne se décale pas.
      showSearch={isMobile ? false : { optionFilterProp: "label" }}
      virtual={!isMobile}
      maxTagCount={isMobile ? "responsive" : undefined}
      classNames={{ popup: { root: "tag-select-popup" } }}
      tagRender={({ value: tagId, label, closable, onClose, isMaxTag }) => {
        const tag = isMaxTag ? undefined : tagsById.get(tagId as string);
        if (!tag) {
          // Compteur « +N » des étiquettes masquées (maxTagCount)
          return <AntTag style={{ marginInlineEnd: 4 }}>{label}</AntTag>;
        }
        return (
          // mousedown : ne pas ouvrir / fermer la liste en touchant une étiquette déjà choisie.
          // Seule la croix retire l'étiquette (un toucher sur la pastille ne la supprime plus par erreur).
          <span onMouseDown={(event) => event.preventDefault()}>
            <TagBadge tag={tag} onClose={closable ? onClose : undefined} />
          </span>
        );
      }}
    />
  );
}
