const noteImportExtensions = [".md", ".markdown", ".txt"];
const noteImportInvalidTitleCharacters = /[<>:"/\\|?*]+/g;

export const noteImportAccept =
  ".md,.markdown,.txt,text/markdown,text/plain";
export const noteImportMaxBytes = 2 * 1024 * 1024;

export function isSupportedNoteImportFile(file) {
  const lowerName = String(file?.name || "").toLowerCase();
  return noteImportExtensions.some((extension) => lowerName.endsWith(extension));
}

export function getImportedNoteTitle(filename) {
  const strippedTitle = String(filename || "").replace(
    /\.(md|markdown|txt)$/i,
    "",
  );
  const normalizedTitle = strippedTitle
    .replace(noteImportInvalidTitleCharacters, "-")
    .replace(/\s+/g, " ")
    .trim();

  return normalizedTitle || "Imported note";
}
