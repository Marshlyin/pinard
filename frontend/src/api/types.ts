// Types des ressources de l'API backend (voir http://127.0.0.1:9090/docs)

export interface Shelf {
  id: string;
  name: string;
  rows: number;
  columns: number;
  capacity: number;
}

export interface BottleSummary {
  id: string;
  cuvee: string;
  domain: string;
  vintage: number | null;
}

export interface ShelfPlacement {
  id: string;
  row: number;
  column: number;
  bottle: BottleSummary;
}

export interface ShelfDetail extends Shelf {
  placements: ShelfPlacement[];
}

export interface ShelfInput {
  name: string;
  rows: number;
  columns: number;
}

export interface TagCategory {
  id: string;
  name: string;
}

export interface TagCategoryInput {
  name: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  category: TagCategory;
}

export interface TagInput {
  name: string;
  category_id: string;
  color: string;
}

export interface Bottle extends BottleSummary {
  quantity: number;
  tags: Tag[];
}

export interface BottleLocation {
  id: string;
  shelf: { id: string; name: string };
  row: number;
  column: number;
}

export interface BottleDetail extends Bottle {
  placements: BottleLocation[];
}

export interface BottleInput {
  cuvee: string;
  domain: string;
  vintage: number | null;
  tag_ids: string[];
}

export interface PlacementInput {
  shelf_id: string;
  row: number;
  column: number;
}
