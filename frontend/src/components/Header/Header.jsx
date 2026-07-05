import "./Header.css";

function Header({ onSettingsClick }) {
  return (
    <header className="header">
      <h1 className="header-title">Local Document Retrieval System</h1>
      <button
        className="settings-button"
        type="button"
        onClick={onSettingsClick}
      >
        Settings
      </button>
    </header>
  );
}

export default Header;