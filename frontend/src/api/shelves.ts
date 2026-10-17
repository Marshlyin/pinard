import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import type { Shelf, ShelfDetail, ShelfInput } from "./types";

export const shelvesKeys = {
  all: ["shelves"] as const,
  detail: (id: string) => ["shelves", id] as const,
};

export function useShelves() {
  return useQuery({ queryKey: shelvesKeys.all, queryFn: () => api.get<Shelf[]>("/shelves") });
}

export function useShelf(id: string | undefined) {
  return useQuery({
    queryKey: shelvesKeys.detail(id ?? ""),
    queryFn: () => api.get<ShelfDetail>(`/shelves/${id}`),
    enabled: id !== undefined,
  });
}

export function useSaveShelf() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id?: string; input: ShelfInput }) =>
      id ? api.put<Shelf>(`/shelves/${id}`, input) : api.post<Shelf>("/shelves", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: shelvesKeys.all });
      // Le nom de l'étagère apparaît dans les emplacements des bouteilles
      queryClient.invalidateQueries({ queryKey: ["bottles"] });
    },
  });
}

export function useDeleteShelf() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/shelves/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: shelvesKeys.all }),
  });
}
