<template>
  <input
    type="text"
    class="w-full rounded-[20px] border border-theme-border bg-theme-panel/80 px-4 py-3 text-theme-text shadow-[0_10px_30px_rgb(var(--theme-shadow)/0.06)] placeholder:text-theme-text-very-muted focus:border-theme-brand/40 focus:outline-none"
    v-model="model"
    ref="input"
  />
</template>

<script setup>
import { ref } from "vue";

const model = defineModel();
const input = ref();
</script>
