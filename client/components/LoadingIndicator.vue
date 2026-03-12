<template>
  <div
    class="w-full"
    :class="{ 'flex min-h-[220px] items-center justify-center': loadSuccessful !== true }"
  >
    <!-- Loading -->
    <div
      v-if="gracePeriodExpired && loadSuccessful === null && !props.hideLoader"
      class="app-surface-muted flex min-w-[220px] flex-col items-center gap-4 rounded-[28px] px-8 py-8"
    >
      <div class="loader-orbit">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <span class="text-[11px] font-semibold uppercase tracking-[0.28em] text-theme-text-very-muted">
        Loading
      </span>
    </div>

    <!-- Failed -->
    <div
      v-else-if="loadSuccessful === false"
      class="app-surface-muted flex max-w-[28rem] flex-col items-center rounded-[32px] px-8 py-10 text-center"
    >
      <SvgIcon
        type="mdi"
        :path="failedIconPath"
        size="4em"
        class="mb-4 text-theme-brand"
      />
      <span class="max-w-80 text-lg text-theme-text-muted">{{ failedMessage }}</span>
    </div>

    <!-- Loaded -->
    <slot v-else-if="loadSuccessful"></slot>
  </div>
</template>

<script setup>
import SvgIcon from "@jamescoyle/vue-icon";
import { mdiTrafficCone } from "@mdi/js";
import { ref, onMounted } from "vue";

const props = defineProps({ hideLoader: Boolean });

const loadSuccessful = ref(null);
const failedIconPath = ref("");
const failedMessage = ref("");
const gracePeriodExpired = ref(false);

// Don't show loading animation within the first 400ms.
onMounted(() => {
  startGracePeriodTimer();
});

function startGracePeriodTimer() {
  gracePeriodExpired.value = false;
  setTimeout(() => {
    gracePeriodExpired.value = true;
  }, 400);
}

function setLoading() {
  loadSuccessful.value = null;
  startGracePeriodTimer();
}

function setFailed(message, iconPath) {
  failedMessage.value = message || "Loading Failed";
  failedIconPath.value = iconPath || mdiTrafficCone;
  loadSuccessful.value = false;
}

function setLoaded() {
  loadSuccessful.value = true;
}

defineExpose({ setLoading, setFailed, setLoaded });
</script>

<style scoped>
.loader-orbit {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.loader-orbit span {
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 9999px;
  background: rgb(var(--theme-brand));
  box-shadow: 0 0 20px rgb(var(--theme-brand) / 0.35);
  animation: loaderPulse 1s infinite ease-in-out;
}

.loader-orbit span:nth-child(2) {
  animation-delay: 0.15s;
}

.loader-orbit span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes loaderPulse {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  50% {
    transform: translateY(-5px);
    opacity: 1;
  }
}
</style>
