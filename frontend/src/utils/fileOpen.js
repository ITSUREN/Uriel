import { buildDocumentFileUrl } from "../services/api";

// Returns "opened" | "failed". Fetches the file as a GET (no HEAD probe —
// some backends don't support HEAD on GET-only routes), converts it to a
// blob, and opens an object URL for that blob. This still triggers the
// browser's native PDF/text viewer, and lets us actually confirm success
// instead of guessing from window.open's return value.
export async function openFileBestEffort(docId) {
  const url = buildDocumentFileUrl(docId);

  try {
    const res = await fetch(url);
    if (!res.ok) {
      return "failed";
    }

    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);
    window.open(objectUrl, "_blank");

    // Revoke after a delay so the new tab has time to load it first.
    setTimeout(() => URL.revokeObjectURL(objectUrl), 10000);

    return "opened";
  } catch {
    return "failed";
  }
}

export async function copyPathToClipboard(path) {
  try {
    await navigator.clipboard.writeText(path);
    return true;
  } catch {
    return false;
  }
}