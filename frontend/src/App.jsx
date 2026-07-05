import { useState } from "react";
import SearchBar from "./components/Search/SearchBar";
import ResultsList from "./components/Results/ResultsList";

function App() {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div>
      <SearchBar
        onResults={setResults}
        onError={setError}
        onLoadingChange={setLoading}
      />

      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {results && <ResultsList results={results} />}
    </div>
  );
}

export default App;