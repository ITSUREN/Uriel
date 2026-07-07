import { IconSettings } from "../Icons";
import "./Header.css";

function Header({ onSettingsClick, settingsDisabled = false }) {
  return (
    <header className="header">
      <div className="header-brand">
        <h1 className="header-title">Local Document Retrieval</h1>
        <span className="header-status">
          <span className="header-status-dot" />
          Ready
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