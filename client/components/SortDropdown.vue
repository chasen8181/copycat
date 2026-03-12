<template>
  <Popover ref="popover" panelClass="toolbar-popover">
    <template #trigger>
      <CustomButton :iconPath="mdiSort" :label="buttonLabel" />
    </template>

    <template #default="{ close }">
      <div class="mb-2 px-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-theme-text-very-muted">
        Sort notes
      </div>
      <button
        v-for="option in options"
        :key="option.key"
        type="button"
        class="flex w-full rounded-[18px] px-3 py-3 text-left text-sm text-theme-text hover:bg-theme-background/45"
        :class="{
          'bg-theme-brand/10 text-theme-text': isSelected(option),
        }"
        @click="selectOption(option, close)"
      >
        {{ option.label }}
      </button>
    </template>
  </Popover>
</template>

<script setup>
import { mdiSort } from "@mdi/js";
import { computed } from "vue";

import { noteSortOptions } from "../constants.js";
import CustomButton from "./CustomButton.vue";
import Popover from "./Popover.vue";

const props = defineProps({
  sort: String,
  order: String,
});

const emit = defineEmits(["select"]);

const options = noteSortOptions;

const buttonLabel = computed(() => {
  const option = options.find((item) => isSelected(item));
  return option ? `Sort: ${option.label}` : "Sort";
});

function isSelected(option) {
  return option.sort === props.sort && option.order === props.order;
}

function selectOption(option, close) {
  emit("select", option);
  close();
}
</script>
