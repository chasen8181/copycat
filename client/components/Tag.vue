<template>
  <span
    class="inline-flex min-w-0 max-w-full items-center rounded-full border border-theme-border bg-theme-background/35 px-3 py-1.5 text-[12px] font-medium text-theme-text shadow-[0_8px_24px_rgb(var(--theme-shadow)/0.06)]"
    :class="{
      'cursor-pointer hover:border-theme-brand/40 hover:bg-theme-panel/80':
        clickable,
      'border-theme-brand/45 bg-theme-brand/10': selected,
      'pr-1.5': removable || deletable,
    }"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? 0 : undefined"
    @click="clickHandler"
    @keydown.enter.prevent="clickHandler"
    @keydown.space.prevent="clickHandler"
  >
    <span
      class="mr-2 h-2.5 w-2.5 rounded-full"
      :style="{ backgroundColor: resolvedColor }"
    ></span>
    <span class="min-w-0 truncate">{{ resolvedLabel }}</span>
    <button
      v-if="removable"
      type="button"
      class="ml-1 rounded-full px-1.5 py-0.5 text-theme-text-muted hover:bg-theme-background/70 hover:text-theme-text"
      @click.stop="$emit('remove')"
    >
      x
    </button>
    <button
      v-if="deletable"
      type="button"
      class="ml-1 rounded-full px-1.5 py-0.5 text-theme-text-muted hover:bg-theme-background/70 hover:text-theme-danger"
      @click.stop="$emit('delete')"
    >
      x
    </button>
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  tag: {
    type: Object,
    default: null,
  },
  label: {
    type: String,
    default: "",
  },
  color: {
    type: String,
    default: "",
  },
  clickable: Boolean,
  deletable: Boolean,
  removable: Boolean,
  selected: Boolean,
});

const emit = defineEmits(["click", "remove", "delete"]);

const resolvedLabel = computed(() => {
  return props.tag?.label || props.label || props.tag?.id || "";
});

const resolvedColor = computed(() => {
  return props.tag?.color || props.color || "#6B7280";
});

function clickHandler() {
  if (props.clickable) {
    emit("click");
  }
}
</script>
