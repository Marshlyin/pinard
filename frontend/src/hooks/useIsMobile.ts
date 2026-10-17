import { Grid } from "antd";

/** Écran étroit (téléphone, < 768 px) : tables compactes, actions regroupées dans un menu. */
export function useIsMobile(): boolean {
  const screens = Grid.useBreakpoint();
  // `=== false` : tant que la taille n'est pas connue (undefined), on garde l'affichage ordinateur
  return screens.md === false;
}
