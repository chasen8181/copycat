<template>
  <button
    type="button"
    class="inline-flex cursor-pointer items-center gap-2 rounded-full border border-theme-border bg-theme-panel/75 px-3 py-2 text-sm font-medium text-theme-text shadow-[0_10px_28px_rgb(var(--theme-shadow)/0.06)]"
  >
    <span v-if="label" class="text-theme-text-muted">{{ label }}</span>
    <SvgIcon
      type="mdi"
      :path="isOn ? mdiToggleSwitch : mdiToggleSwitchOff"
      :class="{ 'text-theme-brand': isOn, 'text-theme-text-very-muted': !isOn }"
      width="2em"
      height="1em"
      viewBox="2 7 20 10"
    ></SvgIcon>
  </button>
</template>

<script setup>
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiToggleSwitch, mdiToggleSwitchOff } from "@mdi/js";

defineProps({
  label: String,
  isOn: Boolean,
});
</script>
