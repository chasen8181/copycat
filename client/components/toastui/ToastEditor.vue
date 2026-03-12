<template>
  <div ref="editorElement" class="toast-editor-root"></div>
</template>

<script setup>
import Editor from "@toast-ui/editor";
import { onMounted, ref } from "vue";

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
