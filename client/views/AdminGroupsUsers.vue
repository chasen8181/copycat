<template>
  <div class="page-shell">
    <section class="app-surface app-hero">
      <div class="relative z-10 flex flex-col gap-6">
        <div class="max-w-3xl">
          <p class="app-kicker">Administration</p>
          <h1 class="app-title app-title-wide">Groups & Users</h1>
          <p class="app-subtitle">
            Create groups, assign users, and control who can work with
            each note space.
          </p>
        </div>
      </div>
    </section>

    <LoadingIndicator ref="loadingIndicator">
      <div v-if="!isAdmin" class="app-surface-muted rounded-[28px] px-6 py-10 text-center">
        <p class="section-heading">Access denied</p>
        <h2 class="section-title">Admin access required</h2>
        <p class="mx-auto mt-3 max-w-xl text-sm leading-7 text-theme-text-muted">
          This screen is only available to the bootstrap administrator.
        </p>
      </div>

      <div v-else class="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section class="app-surface-muted rounded-[28px] px-5 py-5 sm:px-6">
          <div class="flex items-end justify-between gap-4">
            <div>
              <p class="section-heading">Groups</p>
              <h2 class="section-title">Groups</h2>
            </div>
            <p class="section-meta">{{ groups.length }} groups</p>
          </div>

          <div class="mt-5 flex flex-col gap-3 sm:flex-row">
            <input
              v-model.trim="newGroupName"
              type="text"
              class="w-full rounded-[20px] border border-theme-border bg-theme-panel/80 px-4 py-3 text-theme-text shadow-[0_10px_30px_rgb(var(--theme-shadow)/0.06)] placeholder:text-theme-text-very-muted focus:border-theme-brand/40 focus:outline-none"
              placeholder="New group name"
              @keydown.enter.prevent="createGroupHandler"
            />
            <CustomButton
              label="Create Group"
              style="cta"
              class="shrink-0"
              @click="createGroupHandler"
            />
          </div>

          <div class="mt-6 space-y-3">
            <article
              v-for="group in groups"
              :key="group.id"
              class="rounded-[24px] border border-theme-border/70 bg-theme-panel/60 p-4"
            >
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="space-y-2">
                  <input
                    v-model.trim="groupDrafts[group.id]"
                    type="text"
                    class="w-full rounded-[18px] border border-theme-border/70 bg-theme-background/20 px-3 py-2 text-sm font-medium text-theme-text focus:border-theme-brand/40 focus:outline-none"
                  />
                  <div class="flex flex-wrap gap-2 text-xs text-theme-text-muted">
                    <span class="meta-pill">{{ group.noteCount }} notes</span>
                    <span class="meta-pill">{{ group.userCount }} users</span>
                    <span class="meta-pill">{{ group.slug }}</span>
                  </div>
                </div>

                <div class="flex flex-wrap items-center gap-2">
                  <CustomButton
                    label="Save"
                    size="sm"
                    style="success"
                    :disabled="!isGroupDirty(group)"
                    @click="saveGroupHandler(group)"
                  />
                  <CustomButton
                    label="Delete"
                    size="sm"
                    style="danger"
                    @click="deleteGroupHandler(group)"
                  />
                </div>
              </div>
            </article>
          </div>
        </section>

        <section class="app-surface-muted rounded-[28px] px-5 py-5 sm:px-6">
          <div class="flex items-end justify-between gap-4">
            <div>
              <p class="section-heading">Membership</p>
              <h2 class="section-title">Users</h2>
            </div>
            <p class="section-meta">{{ users.length }} users</p>
          </div>

          <div class="mt-5 rounded-[24px] border border-theme-border/70 bg-theme-panel/60 p-4">
            <div class="grid gap-3 sm:grid-cols-2">
              <input
                v-model.trim="newUser.username"
                type="text"
                class="w-full rounded-[20px] border border-theme-border bg-theme-panel/80 px-4 py-3 text-theme-text shadow-[0_10px_30px_rgb(var(--theme-shadow)/0.06)] placeholder:text-theme-text-very-muted focus:border-theme-brand/40 focus:outline-none"
                placeholder="Username"
              />
              <input
                v-model="newUser.password"
                type="password"
                class="w-full rounded-[20px] border border-theme-border bg-theme-panel/80 px-4 py-3 text-theme-text shadow-[0_10px_30px_rgb(var(--theme-shadow)/0.06)] placeholder:text-theme-text-very-muted focus:border-theme-brand/40 focus:outline-none"
                placeholder="Password"
              />
              <input
                v-model.trim="newUser.displayName"
                type="text"
                class="w-full rounded-[20px] border border-theme-border bg-theme-panel/80 px-4 py-3 text-theme-text shadow-[0_10px_30px_rgb(var(--theme-shadow)/0.06)] placeholder:text-theme-text-very-muted focus:border-theme-brand/40 focus:outline-none sm:col-span-2"
                placeholder="Display name"
              />
            </div>

            <div class="mt-4">
              <p class="mb-2 text-[11px] font-semibold uppercase tracking-[0.24em] text-theme-text-very-muted">
                Assign groups
              </p>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="group in groupOptions"
                  :key="`new-user-${group.id}`"
                  class="inline-flex items-center gap-2 rounded-full border border-theme-border/70 bg-theme-background/20 px-3 py-2 text-sm text-theme-text"
                >
                  <input
                    :checked="newUser.groupIds.includes(group.id)"
                    type="checkbox"
                    class="accent-[rgb(var(--theme-brand))]"
                    @change="toggleGroupSelection(newUser.groupIds, group.id)"
                  />
                  {{ group.name }}
                </label>
              </div>
            </div>

            <label class="mt-4 inline-flex items-center gap-3 text-sm text-theme-text-muted">
              <input
                v-model="newUser.isActive"
                type="checkbox"
                class="accent-[rgb(var(--theme-brand))]"
              />
              User is active
            </label>

            <div class="mt-4">
              <CustomButton label="Create User" style="cta" @click="createUserHandler" />
            </div>
          </div>

          <div class="mt-6 space-y-3">
            <article
              v-for="user in users"
              :key="user.username"
              class="rounded-[24px] border border-theme-border/70 bg-theme-panel/60 p-4"
            >
              <div class="grid gap-4">
                <div class="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p class="text-base font-semibold text-theme-text">
                      {{ user.username }}
                    </p>
                    <p class="mt-1 text-sm text-theme-text-muted">
                      {{ userDrafts[user.username]?.displayName || user.username }}
                    </p>
                  </div>
                  <label class="inline-flex items-center gap-2 text-sm text-theme-text-muted">
                    <input
                      v-model="userDrafts[user.username].isActive"
                      type="checkbox"
                      class="accent-[rgb(var(--theme-brand))]"
                    />
                    Active
                  </label>
                </div>

                <div class="grid gap-3 sm:grid-cols-2">
                  <input
                    v-model.trim="userDrafts[user.username].displayName"
                    type="text"
                    class="w-full rounded-[18px] border border-theme-border/70 bg-theme-background/20 px-3 py-2 text-sm text-theme-text focus:border-theme-brand/40 focus:outline-none"
                    placeholder="Display name"
                  />
                  <input
                    v-model="userDrafts[user.username].password"
                    type="password"
                    class="w-full rounded-[18px] border border-theme-border/70 bg-theme-background/20 px-3 py-2 text-sm text-theme-text focus:border-theme-brand/40 focus:outline-none"
                    placeholder="New password"
                  />
                </div>

                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="group in groupOptions"
                    :key="`${user.username}-${group.id}`"
                    class="inline-flex items-center gap-2 rounded-full border border-theme-border/70 bg-theme-background/20 px-3 py-2 text-sm text-theme-text"
                  >
                    <input
                      :checked="userDrafts[user.username].groupIds.includes(group.id)"
                      type="checkbox"
                      class="accent-[rgb(var(--theme-brand))]"
                      @change="toggleGroupSelection(userDrafts[user.username].groupIds, group.id)"
                    />
                    {{ group.name }}
                  </label>
                </div>

                <div class="flex flex-wrap items-center justify-end gap-2">
                  <CustomButton
                    label="Save"
                    size="sm"
                    style="success"
                    @click="saveUserHandler(user.username)"
                  />
                  <CustomButton
                    label="Delete"
                    size="sm"
                    style="danger"
                    @click="deleteUserHandler(user.username)"
                  />
                </div>
              </div>
            </article>
          </div>
        </section>
      </div>
    </LoadingIndicator>
  </div>
</template>

<script setup>
import { useToast } from "primevue/usetoast";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { onBeforeRouteLeave } from "vue-router";

import {
  apiErrorHandler,
  createGroup,
  createUser,
  deleteGroup,
  deleteUser,
  getAdminGroups,
  getAdminUsers,
  updateGroup,
  updateUser,
} from "../api.js";
import CustomButton from "../components/CustomButton.vue";
import LoadingIndicator from "../components/LoadingIndicator.vue";
import { useGlobalStore } from "../globalStore.js";
import { getToastOptions } from "../helpers.js";

const globalStore = useGlobalStore();
const groups = ref([]);
const groupDrafts = ref({});
const loadingIndicator = ref();
const newGroupName = ref("");
const newUser = ref({
  username: "",
  password: "",
  displayName: "",
  groupIds: [],
  isActive: true,
});
const toast = useToast();
const userDrafts = ref({});
const users = ref([]);

const groupOptions = computed(() =>
  groups.value.map((group) => ({ id: group.id, name: group.name })),
);
const isAdmin = computed(() => globalStore.principal?.isAdmin === true);
const hasUnsavedGroupChanges = computed(() =>
  groups.value.some((group) => isGroupDirty(group)),
);

function syncGroupDrafts() {
  groupDrafts.value = Object.fromEntries(
    groups.value.map((group) => [group.id, group.name]),
  );
}

function syncUserDrafts() {
  userDrafts.value = Object.fromEntries(
    users.value.map((user) => [
      user.username,
      {
        displayName: user.displayName || user.username,
        password: "",
        groupIds: [...user.groupIds],
        isActive: user.isActive,
      },
    ]),
  );
}

function normalizeGroupName(value) {
  return (value || "").trim();
}

function isGroupDirty(group) {
  return normalizeGroupName(groupDrafts.value[group.id]) !== group.name;
}

function confirmDiscardGroupChanges() {
  return window.confirm(
    "You have unsaved group changes. Are you sure you want to leave without saving them?",
  );
}

function handleBeforeUnload(event) {
  if (!hasUnsavedGroupChanges.value) {
    return;
  }

  event.preventDefault();
  event.returnValue = "";
}

function loadData() {
  if (!isAdmin.value) {
    loadingIndicator.value?.setLoaded();
    return;
  }

  loadingIndicator.value.setLoading();
  Promise.all([getAdminGroups(), getAdminUsers()])
    .then(([groupsData, usersData]) => {
      groups.value = groupsData;
      users.value = usersData;
      globalStore.config = {
        ...globalStore.config,
        availableGroups: groupsData.map((group) => ({
          id: group.id,
          name: group.name,
        })),
      };
      syncGroupDrafts();
      syncUserDrafts();
      loadingIndicator.value.setLoaded();
    })
    .catch((error) => {
      loadingIndicator.value.setFailed();
      apiErrorHandler(error, toast);
    });
}

function toggleGroupSelection(groupIds, groupId) {
  const index = groupIds.indexOf(groupId);
  if (index >= 0) {
    groupIds.splice(index, 1);
  } else {
    groupIds.push(groupId);
  }
}

function createGroupHandler() {
  if (!newGroupName.value) {
    return;
  }
  createGroup(newGroupName.value)
    .then(() => {
      newGroupName.value = "";
      toast.add(getToastOptions("Group created.", "Success", "success"));
      loadData();
    })
    .catch((error) => {
      apiErrorHandler(error, toast);
    });
}

function saveGroupHandler(group) {
  if (!isGroupDirty(group)) {
    return;
  }

  updateGroup(group.id, { name: groupDrafts.value[group.id] })
    .then(() => {
      toast.add(getToastOptions("Group updated.", "Success", "success"));
      loadData();
    })
    .catch((error) => {
      apiErrorHandler(error, toast);
    });
}

function deleteGroupHandler(group) {
  deleteGroup(group.id)
    .then(() => {
      toast.add(getToastOptions("Group deleted.", "Success", "success"));
      loadData();
    })
    .catch((error) => {
      apiErrorHandler(error, toast);
    });
}

function createUserHandler() {
  createUser({
    username: newUser.value.username,
    password: newUser.value.password,
    displayName: newUser.value.displayName || newUser.value.username,
    groupIds: newUser.value.groupIds,
    isActive: newUser.value.isActive,
  })
    .then(() => {
      newUser.value = {
        username: "",
        password: "",
        displayName: "",
        groupIds: [],
        isActive: true,
      };
      toast.add(getToastOptions("User created.", "Success", "success"));
      loadData();
    })
    .catch((error) => {
      apiErrorHandler(error, toast);
    });
}

function saveUserHandler(username) {
  const draft = userDrafts.value[username];
  const payload = {
    displayName: draft.displayName || username,
    groupIds: draft.groupIds,
    isActive: draft.isActive,
  };
  if (draft.password) {
    payload.password = draft.password;
  }
  updateUser(username, payload)
    .then(() => {
      toast.add(getToastOptions("User updated.", "Success", "success"));
      loadData();
    })
    .catch((error) => {
      apiErrorHandler(error, toast);
    });
}

function deleteUserHandler(username) {
  deleteUser(username)
    .then(() => {
      toast.add(getToastOptions("User deleted.", "Success", "success"));
      loadData();
    })
    .catch((error) => {
      apiErrorHandler(error, toast);
    });
}

watch(
  () => newUser.value.username,
  (username, previousUsername) => {
    const normalizedUsername = username.trim();
    if (
      !newUser.value.displayName ||
      newUser.value.displayName === previousUsername
    ) {
      newUser.value.displayName = normalizedUsername;
    }
  },
);

watch(isAdmin, (nextValue) => {
  if (nextValue) {
    loadData();
  }
});

onBeforeRouteLeave(() => {
  if (!hasUnsavedGroupChanges.value) {
    return true;
  }

  return confirmDiscardGroupChanges();
});

onMounted(() => {
  window.addEventListener("beforeunload", handleBeforeUnload);
  loadData();
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeunload", handleBeforeUnload);
});
</script>
