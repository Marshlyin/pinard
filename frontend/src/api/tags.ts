import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, queryString } from "./client";
import type { Tag, TagCategory, TagCategoryInput, TagInput } from "./types";

export const tagCategoriesKeys = { all: ["tag-categories"] as const };
export const tagsKeys = {
  all: ["tags"] as const,
  list: (categoryId?: string) => ["tags", { categoryId }] as const,
};

// --- Catégories ---

export function useTagCategories() {
  return useQuery({
    queryKey: tagCategoriesKeys.all,
    queryFn: () => api.get<TagCategory[]>("/tag-categories"),
  });
}

export function useSaveTagCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id?: string; input: TagCategoryInput }) =>
      id ? api.put<TagCategory>(`/tag-categories/${id}`, input) : api.post<TagCategory>("/tag-categories", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagCategoriesKeys.all });
      // Le nom de la catégorie apparaît dans les étiquettes, elles-mêmes affichées sur les bouteilles
      queryClient.invalidateQueries({ queryKey: tagsKeys.all });
      queryClient.invalidateQueries({ queryKey: ["bottles"] });
    },
  });
}

export function useDeleteTagCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/tag-categories/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: tagCategoriesKeys.all }),
  });
}

// --- Étiquettes ---

export function useTags(categoryId?: string) {
  return useQuery({
    queryKey: tagsKeys.list(categoryId),
    queryFn: () => api.get<Tag[]>(`/tags${queryString({ category_id: categoryId })}`),
  });
}

export function useSaveTag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id?: string; input: TagInput }) =>
      id ? api.put<Tag>(`/tags/${id}`, input) : api.post<Tag>("/tags", input),
    // Promesse renvoyée : React Query l'attend avant les callbacks de mutate(), la liste des étiquettes est donc
    // déjà rechargée quand l'appelant utilise l'étiquette créée (ex : la cocher dans un TagSelect)
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: tagsKeys.all }),
        queryClient.invalidateQueries({ queryKey: ["bottles"] }),
      ]),
  });
}

export function useDeleteTag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/tags/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tagsKeys.all });
      queryClient.invalidateQueries({ queryKey: ["bottles"] });
    },
  });
}
