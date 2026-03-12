<template>
  <Popover panelClass="toolbar-popover">
    <template #trigger>
      <CustomButton :iconPath="mdiViewGridOutline" :label="buttonLabel" />
    </template>

    <template #default="{ close }">
      <div class="mb-2 px-1 text-[11px] font-semibold uppercase tracking-[0.24em] text-theme-text-very-muted">
        Notes scope
      </div>
      <button
        v-for="option in options"
        :key="option.id"
        type="button"
        class="flex w-full rounded-[18px] px-3 py-3 text-left text-sm text-theme-text hover:bg-theme-background/45"
        :class="{ 'bg-theme-brand/10 text-theme-text': option.id === modelValue }"
        @click="selectOption(option.id, close)"
      >
        {{ option.name }}
      </button>
    </template>
  </Popover>
</template>

<script setup>
import { mdiViewGridOutline } from "@mdi/js";
import { computed } from "vue";

import CustomButton from "./CustomButton.vue";
import Popover from "./Popover.vue";

const props = defineProps({
  modelValue: {
    type: String,
    default: undefined,
  },
  options: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);

const buttonLabel = computed(() => {
  const selected = props.options.find((option) => option.id === props.modelValue);
  return selected ? `Scope: ${selected.name}` : "Scope";
});

function selectOption(value, close) {
  emit("update:modelValue", value);
  close();
}
</script>
