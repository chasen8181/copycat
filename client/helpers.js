export function getToastOptions(description, title, severity) {
  return {
    summary: title,
    detail: description,
    severity: severity,
    closable: false,
    life: 5000,
  };
}

export function setDarkThemeOn(save = true) {
  document.body.classList.add("dark");
  if (save) localStorage.setItem("darkTheme", "true");
}

export function setDarkThemeOff(save = true) {
  document.body.classList.remove("dark");
  if (save) localStorage.setItem("darkTheme", "false");
}

export function toggleTheme() {
  document.body.classList.contains("dark")
    ? setDarkThemeOff()
    : setDarkThemeOn();
}

export function loadTheme() {
  const storedTheme = localStorage.getItem("darkTheme");
  if (storedTheme === "true") {
    setDarkThemeOn();
  } else if (
    storedTheme === null &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    setDarkThemeOn(false);
  }
}

export function buildAppUrl(path) {
  const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
  return new URL(normalizedPath, document.baseURI).toString();
}

export async function copyTextToClipboard(text) {
  await navigator.clipboard.writeText(text);
}

export function formatMonthYear(unixTimestamp) {
  if (!unixTimestamp) {
    return "Undated";
  }

  return new Intl.DateTimeFormat(undefined, {
    month: "long",
    year: "numeric",
  }).format(new Date(unixTimestamp * 1000));
}

export function groupNotesByMonth(notes, dateField = "lastModified") {
  const groups = [];
  const groupsByKey = new Map();

  notes.forEach((note) => {
    const timestamp = Number(note?.[dateField] || 0);
    const date = timestamp ? new Date(timestamp * 1000) : null;
    const key = date
      ? `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`
      : "undated";
    const label = date ? formatMonthYear(timestamp) : "Undated";

    if (!groupsByKey.has(key)) {
      const group = {
        key,
        label,
        items: [],
      };
      groupsByKey.set(key, group);
      groups.push(group);
    }

    groupsByKey.get(key).items.push(note);
  });

  return groups;
}
