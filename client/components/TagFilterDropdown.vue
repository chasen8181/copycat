<template>
  <Popover ref="popover" panelClass="toolbar-popover">
    <template #trigger>
      <CustomButton :iconPath="mdiFilterVariant" :label="buttonLabel" />
    </template>

    <template #default="{ close }">
      <div class="mb-3 flex items-center justify-between px-1">
        <span class="text-[11px] font-semibold uppercase tracking-[0.24em] text-theme-text-very-muted">
          Filter by tags
        </span>
        <button
          type="button"
          class="rounded-full px-2 py-1 text-xs text-theme-text-muted hover:bg-theme-background/45 hover:text-theme-text"
          @click="clearTags(close)"
        >
          Clear
        </button>
      </div>

      <div
        v-if="tags.length === 0"
        class="px-1 py-2 text-sm text-theme-text-muted"
      >
        No custom tags yet.
      </div>

      <label
        v-for="tag in tags"
        :key="tag.id"
        class="flex cursor-pointer items-center rounded-[18px] px-2 py-2 hover:bg-theme-background/45"
      >
        <input
          :checked="model.includes(tag.id)"
          type="checkbox"
          class="mr-3 accent-[rgb(var(--theme-brand))]"
          @change="toggleTag(tag.id)"
        />
        <Tag :tag="tag" />
      </label>
    </template>
  </Popover>
</template>

<script setup>
import { mdiFilterVariant } from "@mdi/js";
import { computed } from "vue";

import CustomButton from "./CustomButton.vue";
import Popover from "./Popover.vue";
import Tag from "./Tag.vue";

const model = defineModel({
  type: Array,
  default: [],
});

defineProps({
  tags: {
    type: Array,
    default: () => [],
  },
});

const buttonLabel = computed(() => {
  if (model.value.length === 0) {
    return "Tags";
  }
  return `Tags (${model.value.length})`;
});

function toggleTag(tagId) {
  if (model.value.includes(tagId)) {
    model.value = model.value.filter(
      (selectedTagId) => selectedTagId !== tagId,
    );
  } else {
    model.value = [...model.value, tagId];
  }
}

function clearTags(close) {
  model.value = [];
  close();
}
</script>
