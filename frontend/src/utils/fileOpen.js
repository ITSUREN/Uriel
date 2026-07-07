// Browsers cannot ask the OS to open an arbitrary local file, and there is
// no backend endpoint for it either (confirmed against the Swagger route
// list). A file:// link from an http(s) page is actively blocked by modern
// browsers with a thrown SecurityError (confirmed in testing) rather than
// just silently failing, so this must be caught. When it's blocked, we fall
// back to copying the path to the clipboard, which always works.

export function buildFileUrl(path) {
  const normalized = path.replace(/\\/g, "/");
  const encoded = normalized
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
  const withLeadingSlash = encoded.startsWith("/") ? encoded : `/${encoded}`;
  return `file://${withLeadingSlash}`;
}

export async function copyPathToClipboard(path) {
  try {
    await navigator.clipboard.writeText(path);
    return true;
  } catch {
    return false;
  }
}

// Returns "opened" | "copied" | "failed" so the caller can show the right message.
export async function openFileBestEffort(path) {
  try {
    const win = window.open(buildFileUrl(path), "_blank");
    if (!win) {
      throw new Error("popup blocked");
    }
    return "opened";
  } catch {
    const copied = await copyPathToClipboard(path);
    return copied ? "copied" : "failed";
  }
}