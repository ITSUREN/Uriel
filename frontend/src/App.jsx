import { useState } from "react";
import Header from "./components/Header/Header";
import SearchBar from "./components/Search/SearchBar";
import ResultsList from "./components/Results/ResultsList";
import SettingsModal from "./components/Settings/SettingsModal";
import "./App.css";

function App() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <div className="app">
      <Header onSettingsClick={() => setIsSettingsOpen(true)} />
      <SearchBar
        onResults={setResults}
        onError={setError}
        onLoadingChange={setLoading}
      />

      {loading && <p className="status-message">Searching...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && results && <ResultsList results={results} />}

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}

export default App;