import { IconSettings } from "../Icons";
import "./Header.css";

function Header({ onSettingsClick }) {
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
        title="Settings"
        aria-label="Settings"
      >
        <IconSettings size={18} />
      </button>
    </header>
  );
}

export default Header;