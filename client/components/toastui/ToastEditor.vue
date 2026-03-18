<template>
  <div ref="editorElement" class="toast-editor-root"></div>
</template>

<script setup>
import Editor from "@toast-ui/editor";
import { onBeforeUnmount, onMounted, ref } from "vue";

import baseOptions from "./baseOptions.js";

const props = defineProps({
  initialValue: String,
  initialEditType: {
    type: String,
    default: "markdown",
  },
  height: {
    type: String,
    default: "",
  },
  addImageBlobHook: Function,
});

const emit = defineEmits(["change", "keydown"]);

const editorElement = ref();
let toastEditor;
let removePasteListener = null;

onMounted(() => {
  const editorHeight =
    props.height ||
    (window.matchMedia("(max-width: 767px)").matches ? "420px" : "620px");

  toastEditor = new Editor({
    ...baseOptions,
    el: editorElement.value,
    height: editorHeight,
    initialValue: props.initialValue,
    initialEditType: props.initialEditType,
    events: {
      change: () => {
        emit("change");
      },
      keydown: (_, event) => {
        emit("keydown", event);
      },
    },
    hooks: props.addImageBlobHook
      ? { addImageBlobHook: props.addImageBlobHook }
      : {},
  });

  bindPasteScrollGuard();
});

onBeforeUnmount(() => {
  removePasteListener?.();
  removePasteListener = null;
  toastEditor?.destroy?.();
});

function getMarkdown() {
  return toastEditor.getMarkdown();
}

function setMarkdown(markdown) {
  toastEditor.setMarkdown(markdown ?? "");
}

function isWysiwygMode() {
  return toastEditor.isWysiwygMode();
}

function bindPasteScrollGuard() {
  if (!editorElement.value) {
    return;
  }

  const handlePaste = (event) => {
    const target =
      event.target instanceof HTMLElement ? event.target : editorElement.value;
    const scrollStates = captureScrollStates(target);
    if (scrollStates.length === 0) {
      return;
    }

    // TOAST UI mutates the editor DOM asynchronously during paste, so restore
    // the scroll position after the browser and editor finish their updates.
    requestAnimationFrame(() => {
      restoreScrollStates(scrollStates);
      requestAnimationFrame(() => {
        restoreScrollStates(scrollStates);
      });
    });
  };

  editorElement.value.addEventListener("paste", handlePaste, true);
  removePasteListener = () => {
    editorElement.value?.removeEventListener("paste", handlePaste, true);
  };
}

function captureScrollStates(startElement) {
  const scrollStates = [];
  const seen = new Set();
  let current = startElement;

  while (current instanceof HTMLElement) {
    if (seen.has(current)) {
      current = current.parentElement;
      continue;
    }

    seen.add(current);
    if (isScrollable(current)) {
      scrollStates.push({
        type: "element",
        element: current,
        top: current.scrollTop,
        left: current.scrollLeft,
      });
    }
    current = current.parentElement;
  }

  scrollStates.push({
    type: "window",
    top: window.scrollY,
    left: window.scrollX,
  });

  return scrollStates;
}

function restoreScrollStates(scrollStates) {
  for (const state of scrollStates) {
    if (state.type === "window") {
      window.scrollTo(state.left, state.top);
      continue;
    }

    if (!state.element?.isConnected) {
      continue;
    }

    state.element.scrollTop = state.top;
    state.element.scrollLeft = state.left;
  }
}

function isScrollable(element) {
  const style = window.getComputedStyle(element);
  const overflowY = style.overflowY;
  const overflowX = style.overflowX;
  const canScrollY =
    ["auto", "scroll", "overlay"].includes(overflowY) &&
    element.scrollHeight > element.clientHeight;
  const canScrollX =
    ["auto", "scroll", "overlay"].includes(overflowX) &&
    element.scrollWidth > element.clientWidth;

  return canScrollY || canScrollX;
}

defineExpose({ getMarkdown, setMarkdown, isWysiwygMode });
</script>

<style>
@import "@toast-ui/editor/dist/toastui-editor.css";
@import "prismjs/themes/prism.css";
@import "@toast-ui/editor-plugin-code-syntax-highlight/dist/toastui-editor-plugin-code-syntax-highlight.css";
@import "./toastui-editor-overrides.scss";

.toast-editor-root {
  min-height: 420px;
}

@media (min-width: 768px) {
  .toast-editor-root {
    min-height: 620px;
  }
}
</style>
