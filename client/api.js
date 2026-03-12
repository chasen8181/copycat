import * as constants from "./constants.js";

import { Note, SearchResult, Tag } from "./classes.js";

import axios from "axios";
import { getStoredToken } from "./tokenStorage.js";
import { buildAppUrl } from "./helpers.js";
import { getToastOptions } from "./helpers.js";
import router from "./router.js";

const api = axios.create({
  paramsSerializer: {
    indexes: null,
  },
});

api.interceptors.request.use(
  // If the request is not for the token endpoint, add the token to the headers.
  function (config) {
    if (config.url !== "api/token") {
      const token = getStoredToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  },
);

export function apiErrorHandler(error, toast) {
  if (error.response?.status === 401) {
    const redirectPath = router.currentRoute.value.fullPath;
    router.push({
      name: "login",
      query: { [constants.params.redirect]: redirectPath },
    });
  } else {
    console.error(error);
    const detail =
      error.response?.data?.detail ||
      "Unknown error communicating with the server. Please try again.";
    toast.add(
      getToastOptions(
        detail,
        "Unknown Error",
        "error",
      ),
    );
  }
}

export async function getConfig() {
  try {
    const response = await api.get("api/config");
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function getToken(username, password, totp) {
  try {
    const response = await api.post("api/token", {
      username: username,
      password: totp ? password + totp : password,
    });
    return response.data.access_token;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function authCheck() {
  try {
    const response = await api.get("api/auth-check");
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function logout() {
  try {
    await api.post("api/logout");
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function getNotes(term, sort, order, limit, group) {
  try {
    const response = await api.get("api/search", {
      params: {
        term,
        sort,
        order,
        limit,
        group,
      },
    });
    return response.data.map((note) => new SearchResult(note));
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function searchNotes({
  term,
  sort,
  order,
  limit,
  tagIds = [],
  favoriteOnly = false,
  favoritesFirst = true,
  group,
}) {
  try {
    const response = await api.get("api/search", {
      params: {
        term,
        sort,
        order,
        limit,
        tagIds,
        favoriteOnly,
        favoritesFirst,
        group,
      },
    });
    return response.data.map((note) => new SearchResult(note));
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function createNote(title, content, tagIds = [], group = null) {
  try {
    const response = await api.post(
      "api/notes",
      {
        title,
        content,
        tagIds,
      },
      {
        params: { group },
      },
    );
    return new Note(response.data);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function getNote(title, group = null) {
  try {
    const response = await api.get(`api/notes/${encodeURIComponent(title)}`, {
      params: { group },
    });
    return new Note(response.data);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function updateNote(title, data, group = null) {
  try {
    const response = await api.patch(
      `api/notes/${encodeURIComponent(title)}`,
      data,
      {
        params: { group },
      },
    );
    return new Note(response.data);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function deleteNote(title, group = null) {
  try {
    await api.delete(`api/notes/${encodeURIComponent(title)}`, {
      params: { group },
    });
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function getTags(group = null) {
  try {
    const response = await api.get("api/tags", { params: { group } });
    return response.data.map((tag) => new Tag(tag));
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function createTag(label, color, group = null) {
  try {
    const response = await api.post(
      "api/tags",
      { label, color },
      { params: { group } },
    );
    return new Tag(response.data);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function updateTag(tagId, data, group = null) {
  try {
    const response = await api.patch(
      `api/tags/${encodeURIComponent(tagId)}`,
      data,
      { params: { group } },
    );
    return new Tag(response.data);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function deleteTag(tagId, group = null) {
  try {
    await api.delete(`api/tags/${encodeURIComponent(tagId)}`, {
      params: { group },
    });
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function duplicateNote(title, group = null) {
  try {
    const response = await api.post(
      `api/notes/${encodeURIComponent(title)}/duplicate`,
      null,
      {
        params: { group },
      },
    );
    return new Note(response.data);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function createAttachment(file, group = null) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("api/attachments", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      params: { group },
    });
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export function getNoteExportUrl(title, group = null) {
  const params = new URLSearchParams();
  if (group) {
    params.set("group", group);
  }
  const query = params.toString();
  return buildAppUrl(
    `api/notes/${encodeURIComponent(title)}/export${query ? `?${query}` : ""}`,
  );
}

export async function getAdminGroups() {
  try {
    const response = await api.get("api/admin/groups");
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function createGroup(name) {
  try {
    const response = await api.post("api/admin/groups", { name });
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function updateGroup(groupId, data) {
  try {
    const response = await api.patch(
      `api/admin/groups/${encodeURIComponent(groupId)}`,
      data,
    );
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function deleteGroup(groupId) {
  try {
    await api.delete(`api/admin/groups/${encodeURIComponent(groupId)}`);
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function getAdminUsers() {
  try {
    const response = await api.get("api/admin/users");
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function createUser(data) {
  try {
    const response = await api.post("api/admin/users", data);
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function updateUser(username, data) {
  try {
    const response = await api.patch(
      `api/admin/users/${encodeURIComponent(username)}`,
      data,
    );
    return response.data;
  } catch (response) {
    return Promise.reject(response);
  }
}

export async function deleteUser(username) {
  try {
    await api.delete(`api/admin/users/${encodeURIComponent(username)}`);
  } catch (response) {
    return Promise.reject(response);
  }
}
