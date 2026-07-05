import { useState } from "react";
import Header from "./components/Header/Header";
import SearchBar from "./components/Search/SearchBar";
import ResultsList from "./components/Results/ResultsList";
import "./App.css";

function App() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <Header />
      <SearchBar
        onResults={setResults}
        onError={setError}
        onLoadingChange={setLoading}
      />

      {loading && <p className="status-message">Searching...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && results && <ResultsList results={results} />}
    </div>
  );
}

export default App;