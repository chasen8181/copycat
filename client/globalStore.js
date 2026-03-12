import { defineStore } from "pinia";
import { ref } from "vue";

export const useGlobalStore = defineStore("global", () => {
  const config = ref(null);
  const principal = ref(null);
  const topBarCounts = ref({
    notes: 0,
    favorites: 0,
    customTags: 0,
  });
  const currentGroup = ref(null);

  return { config, principal, topBarCounts, currentGroup };
});
