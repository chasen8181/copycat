<template>
  <nav class="-mx-1 mb-6 sm:-mx-2 md:mb-10 lg:-mx-3 print:hidden">
    <div class="app-surface rounded-[28px] px-5 py-3 sm:px-6 lg:px-7">
      <div
        class="topbar-layout"
        :class="{ 'topbar-layout-simple': !showMetrics }"
      >
        <div class="topbar-left">
          <RouterLink :to="{ name: 'home' }" v-if="!hideLogo" class="shrink-0">
            <Logo responsive></Logo>
          </RouterLink>
          <div v-if="showMetrics" class="topbar-metrics">
            <span v-for="badge in metricBadges" :key="badge.label" class="topbar-badge">
              <span class="topbar-badge-label">{{ badge.label }}</span>
              <span class="topbar-badge-value">{{ badge.value }}</span>
            </span>
          </div>
        </div>
        <div v-if="showMetrics" class="topbar-search-shell">
          <div class="topbar-search">
            <SearchInput
              :initialSearchTerm="currentSearchTerm"
              placeholder="Search notes..."
            />
          </div>
        </div>
        <div class="topbar-actions">
          <CustomButton
            v-if="showSearchButton"
            :iconPath="mdilMagnify"
            label="Search"
            @click="emit('toggleSearchModal')"
          />
          <RouterLink v-if="showNewButton" :to="newNoteRoute">
            <CustomButton
              :iconPath="mdilPlusCircle"
              label="New Note"
              style="cta"
            />
          </RouterLink>
          <CustomButton :iconPath="mdilMenu" label="Menu" @click="toggleMenu" />
          <PrimeMenu ref="menu" :model="menuItems" :popup="true" />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import {
  mdilLogout,
  mdilMenu,
  mdilMonitor,
  mdilNoteMultiple,
  mdilPlusCircle,
  mdilMagnify,
} from "@mdi/light-js";
import { mdiStarOutline, mdiTagOutline } from "@mdi/js";
import { computed, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import CustomButton from "../components/CustomButton.vue";
import Logo from "../components/Logo.vue";
import PrimeMenu from "../components/PrimeMenu.vue";
import SearchInput from "./SearchInput.vue";
import {
  authTypes,
  params,
  searchOrderOptions,
  searchSortOptions,
} from "../constants.js";
import { useGlobalStore } from "../globalStore.js";
import { toggleTheme } from "../helpers.js";
import { clearStoredToken } from "../tokenStorage.js";
import { logout } from "../api.js";

const globalStore = useGlobalStore();
const menu = ref();
const route = useRoute();
const router = useRouter();

defineProps({
  hideLogo: Boolean,
});

const emit = defineEmits(["toggleSearchModal"]);

const currentAuthType = computed(() => globalStore.config?.authType);
const activeGroup = computed(() => {
  return (
    globalStore.currentGroup ||
    globalStore.config?.defaultGroupId ||
    (globalStore.principal?.isAdmin ? "legacy" : undefined)
  );
});
const isAdmin = computed(() => globalStore.principal?.isAdmin === true);
const canAccessAdminUi = computed(
  () => isAdmin.value && currentAuthType.value !== authTypes.readOnly,
);
const isHomeRoute = computed(() => String(route.path || "") === "/" || route.name === "home");
const isLoginRoute = computed(
  () => String(route.path || "").startsWith("/login") || route.name === "login",
);
const showMetrics = computed(() =>
  isHomeRoute.value,
);
const showSearchButton = computed(() => !showMetrics.value && !isLoginRoute.value);
const currentSearchTerm = computed(() => {
  const term = route.query[params.searchTerm];
  return term && term !== "*" ? term : "";
});
const metricBadges = computed(() => [
  {
    label: "Notes",
    value: globalStore.topBarCounts.notes ?? 0,
  },
  {
    label: "Favorites",
    value: globalStore.topBarCounts.favorites ?? 0,
  },
  {
    label: "Tags",
    value: globalStore.topBarCounts.customTags ?? 0,
  },
]);
const allNotesQuery = computed(() => {
  const query = {
    [params.searchTerm]: "*",
    [params.sort]: searchSortOptions.lastModified,
    [params.order]: searchOrderOptions.desc,
  };
  if (activeGroup.value) {
    query[params.group] = activeGroup.value;
  }
  return query;
});
const favoritesQuery = computed(() => {
  const query = {
    ...allNotesQuery.value,
    [params.favoriteOnly]: "true",
  };
  return query;
});
const tagsRoute = computed(() => ({
  name: "tags",
  query: activeGroup.value ? { [params.group]: activeGroup.value } : {},
}));
const menuItems = computed(() => [
  {
    label: "All Notes",
    icon: mdilNoteMultiple,
    command: () =>
      router.push({
        name: "home",
        query: allNotesQuery.value,
      }),
  },
  {
    label: "Favorites",
    icon: mdiStarOutline,
    command: () =>
      router.push({
        name: "home",
        query: favoritesQuery.value,
      }),
  },
  {
    label: "Tags",
    icon: mdiTagOutline,
    visible: showNewButton.value,
    command: () => router.push(tagsRoute.value),
  },
  {
    label: "Groups & Users",
    icon: mdilPlusCircle,
    visible: canAccessAdminUi.value,
    command: () => router.push({ name: "admin-groups-users" }),
  },
  {
    label: "Toggle Theme",
    icon: mdilMonitor,
    command: toggleTheme,
  },
  {
    separator: true,
    visible: showLogOutButton(),
  },
  {
    label: "Log Out",
    icon: mdilLogout,
    command: logOut,
    visible: showLogOutButton(),
  },
]);

const showNewButton = computed(() => {
  return Boolean(currentAuthType.value) && currentAuthType.value !== authTypes.readOnly;
});
const newNoteRoute = computed(() => ({
  name: "new",
  query:
    activeGroup.value && activeGroup.value !== "all"
      ? { [params.group]: activeGroup.value }
      : {},
}));

function logOut() {
  logout()
    .catch(() => {})
    .finally(() => {
      clearStoredToken();
      localStorage.clear();
      globalStore.principal = null;
      globalStore.config = {
        ...(globalStore.config || {}),
        role: "guest",
        availableGroups: [],
        defaultGroupId: null,
        showLegacyLibrary: false,
        httpOnlyAuthCookie: false,
      };
      globalStore.currentGroup = null;
      globalStore.topBarCounts = {
        notes: 0,
        favorites: 0,
        customTags: 0,
      };
      router.push({ name: "login" });
    });
}

function toggleMenu(event) {
  menu.value.toggle(event);
}

function showLogOutButton() {
  return Boolean(currentAuthType.value) && ![authTypes.none, authTypes.readOnly].includes(currentAuthType.value);
}
</script>
