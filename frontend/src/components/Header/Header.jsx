import { IconSettings } from "../Icons";
import { useIndexProgress } from "../../hooks/useIndexProgress"
import "./Header.css";

function Header({ onSettingsClick, settingsDisabled = false }) {
  const progress = useIndexProgress();
  const isRunning = progress?.state === "running";

  const statusText = isRunning
    ? progress.total_files > 0
      ? `Indexing ${progress.processed_files}/${progress.total_files}...`
      : "Indexing..."
    : "Ready";

  return (
    <header className="header">
      <div className="header-brand">
        <h1 className="header-title">Local Document Retrieval</h1>
        <span className="header-status">
          <span className="header-status-dot" />
          {statusText}
        </span>
      </div>
      <button
        className="settings-button"
        type="button"
        onClick={onSettingsClick}
        disabled={settingsDisabled}
        title={settingsDisabled ? "Complete setup first" : "Settings"}
        aria-label="Settings"
      >
        <IconSettings size={18} />
      </button>
    </header>
  );
}

export default Header;