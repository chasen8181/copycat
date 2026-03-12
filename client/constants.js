// Params
export const params = {
  searchTerm: "term",
  redirect: "redirect",
  sort: "sort",
  order: "order",
  tagIds: "tags",
  favoriteOnly: "favoriteOnly",
  group: "group",
};

export const searchSortOptions = {
  score: "score",
  title: "title",
  lastModified: "lastModified",
  createdAt: "createdAt",
};

export const searchOrderOptions = {
  asc: "asc",
  desc: "desc",
};

export const noteSortOptions = [
  {
    key: "title-asc",
    label: "A-Z",
    sort: searchSortOptions.title,
    order: searchOrderOptions.asc,
  },
  {
    key: "title-desc",
    label: "Z-A",
    sort: searchSortOptions.title,
    order: searchOrderOptions.desc,
  },
  {
    key: "last-modified-desc",
    label: "Last Modified",
    sort: searchSortOptions.lastModified,
    order: searchOrderOptions.desc,
  },
  {
    key: "created-at-desc",
    label: "Created Date",
    sort: searchSortOptions.createdAt,
    order: searchOrderOptions.desc,
  },
];

export const authTypes = {
  none: "none",
  readOnly: "read_only",
  password: "password",
  totp: "totp",
};

export const tagColorPalette = [
  "#3B82F6",
  "#10B981",
  "#EAB308",
  "#F97316",
  "#EF4444",
  "#EC4899",
  "#8B5CF6",
  "#6B7280",
];

export const maxNoteTags = 10;
