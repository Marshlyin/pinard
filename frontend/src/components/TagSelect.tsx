import { PlusOutlined } from "@ant-design/icons";
import { Tag as AntTag, Button, Divider, Select } from "antd";
import { useMemo, useState } from "react";

import { useTags } from "../api/tags";
import { TagFormModal } from "../features/tags/TagFormModal";
import { useIsMobile } from "../hooks/useIsMobile";
import { TagBadge } from "./TagBadge";

interface TagSelectProps {
  value?: string[];
  onChange?: (tagIds: string[]) => void;
  placeholder?: string;
  style?: React.CSSProperties;
  /** Bouton « Nouvelle étiquette » en bas de la liste : l'étiquette créée est cochée automatiquement. */
  allowCreate?: boolean;
}

/** Sélection multiple d'étiquettes, groupées par catégorie. Utilisable seul ou dans un Form.Item. */
export function TagSelect({ value, onChange, placeholder = "Étiquettes", style, allowCreate }: TagSelectProps) {
  const { data: tags = [], isLoading } = useTags();
  const isMobile = useIsMobile();

  // Texte recherché (ordinateur) : sert à pré-remplir le nom d'une nouvelle étiquette
  const [search, setSearch] = useState("");
  const [creating, setCreating] = useState<{ open: boolean; name?: string }>({ open: false });

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

  const typed = search.trim();

  return (
    <>
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
        showSearch={isMobile ? false : { optionFilterProp: "label", searchValue: search, onSearch: setSearch }}
        virtual={!isMobile}
        maxTagCount={isMobile ? "responsive" : undefined}
        classNames={{ popup: { root: "tag-select-popup" } }}
        notFoundContent={allowCreate && typed ? `Aucune étiquette « ${typed} »` : undefined}
        popupRender={
          allowCreate
            ? (menu) => (
                <>
                  {menu}
                  <Divider style={{ margin: "4px 0" }} />
                  <Button
                    type="text"
                    block
                    icon={<PlusOutlined />}
                    style={{ textAlign: "start" }}
                    onClick={() => setCreating({ open: true, name: typed || undefined })}
                  >
                    {typed ? `Créer « ${typed} »` : "Nouvelle étiquette"}
                  </Button>
                </>
              )
            : undefined
        }
        tagRender={({ value: tagId, label, closable, onClose, isMaxTag }) => {
          const tag = isMaxTag ? undefined : tagsById.get(tagId as string);
          if (!tag) {
            // Compteur « +N » des étiquettes masquées (maxTagCount)
            return <AntTag style={{ marginInlineEnd: 4 }}>{label}</AntTag>;
          }
          return (
            // mousedown : ne pas ouvrir / fermer la liste en touchant une étiquette déjà choisie.
            // Ordinateur : seule la croix retire l'étiquette. Mobile : pas de croix, trop facile à toucher par erreur
            // en voulant ouvrir la liste ; on décoche l'étiquette dans la liste.
            <span onMouseDown={(event) => event.preventDefault()}>
              <TagBadge tag={tag} onClose={closable && !isMobile ? onClose : undefined} />
            </span>
          );
        }}
      />

      {allowCreate && (
        <TagFormModal
          open={creating.open}
          defaultName={creating.name}
          // La liste des étiquettes est déjà rechargée à ce stade (voir useSaveTag) : la pastille s'affiche directement
          onSaved={(tag) => {
            onChange?.([...(value ?? []), tag.id]);
            setSearch("");
          }}
          onClose={() => setCreating({ open: false })}
        />
      )}
    </>
  );
}
