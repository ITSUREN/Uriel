// Browsers cannot ask the OS to open an arbitrary local file — there is no
// backend endpoint for this either (confirmed against the Swagger route
// list). This is a best-effort attempt via a file:// link, which many
// browsers block when the page itself isn't served from file://. The
// clipboard copy is the reliable fallback: it always works and lets the
// user paste the path into their file manager.

export function buildFileUrl(path) {
  const normalized = path.replace(/\\/g, "/");
  const encoded = normalized
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
  const withLeadingSlash = encoded.startsWith("/") ? encoded : `/${encoded}`;
  return `file://${withLeadingSlash}`;
}

export function attemptOpenFile(path) {
  window.open(buildFileUrl(path), "_blank");
}

export async function copyPathToClipboard(path) {
  try {
    await navigator.clipboard.writeText(path);
    return true;
  } catch {
    return false;
  }
}