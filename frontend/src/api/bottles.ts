import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, queryString } from "./client";
import { shelvesKeys } from "./shelves";
import type { Bottle, BottleDetail, BottleInput, BottleLocation, PlacementInput } from "./types";

export const bottlesKeys = {
  all: ["bottles"] as const,
  list: (tagIds: string[]) => ["bottles", "list", { tagIds }] as const,
  detail: (id: string) => ["bottles", "detail", id] as const,
};

/** Filtre par étiquettes : OU dans une même catégorie, ET entre catégories (règle appliquée par le backend). */
export function useBottles(tagIds: string[]) {
  return useQuery({
    queryKey: bottlesKeys.list(tagIds),
    queryFn: () => api.get<Bottle[]>(`/bottles${queryString({ tag_id: tagIds })}`),
  });
}

export function useBottle(id: string | undefined) {
  return useQuery({
    queryKey: bottlesKeys.detail(id ?? ""),
    queryFn: () => api.get<BottleDetail>(`/bottles/${id}`),
    enabled: id !== undefined,
  });
}

export function useSaveBottle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id?: string; input: BottleInput }) =>
      id ? api.put<Bottle>(`/bottles/${id}`, input) : api.post<Bottle>("/bottles", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: bottlesKeys.all });
      // La cuvée et le domaine apparaissent dans le détail des étagères
      queryClient.invalidateQueries({ queryKey: shelvesKeys.all });
    },
  });
}

export function useDeleteBottle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`/bottles/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: bottlesKeys.all });
      queryClient.invalidateQueries({ queryKey: shelvesKeys.all });
    },
  });
}

/** Ranger, déplacer et retirer les bouteilles physiques : impacte bouteilles (quantité) et étagères (cases). */
function useInvalidatePlacements() {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: bottlesKeys.all });
    queryClient.invalidateQueries({ queryKey: shelvesKeys.all });
  };
}

export function useAddPlacement() {
  const invalidate = useInvalidatePlacements();
  return useMutation({
    mutationFn: ({ bottleId, input }: { bottleId: string; input: PlacementInput }) =>
      api.post<BottleLocation>(`/bottles/${bottleId}/placements`, input),
    onSuccess: invalidate,
  });
}

export function useMovePlacement() {
  const invalidate = useInvalidatePlacements();
  return useMutation({
    mutationFn: ({ bottleId, placementId, input }: { bottleId: string; placementId: string; input: PlacementInput }) =>
      api.put<BottleLocation>(`/bottles/${bottleId}/placements/${placementId}`, input),
    onSuccess: invalidate,
  });
}

export function useRemovePlacement() {
  const invalidate = useInvalidatePlacements();
  return useMutation({
    mutationFn: ({ bottleId, placementId }: { bottleId: string; placementId: string }) =>
      api.delete(`/bottles/${bottleId}/placements/${placementId}`),
    onSuccess: invalidate,
  });
}
