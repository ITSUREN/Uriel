import { useState } from "react";
import SearchBar from "../components/Search/SearchBar";
import ResultsList from "../components/Results/ResultsList";

function SearchPage({ config }) {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [correctedTerms, setCorrectedTerms] = useState(null);

  const hasCorrections =
    correctedTerms && Object.keys(correctedTerms).length > 0;

  return (
    <>
      <SearchBar
        config={config}
        onResults={setResults}
        onError={setError}
        onLoadingChange={setLoading}
        onCorrectedTerms={setCorrectedTerms}
      />

      {hasCorrections && (
        <p className="spelling-correction">
          Showing results for:{" "}
          {Object.entries(correctedTerms)
            .map(([original, corrected]) => `${original} → ${corrected}`)
            .join(", ")}
        </p>
      )}

      {loading && <p className="status-message">Searching...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && results && <ResultsList results={results} />}
    </>
  );
}

export default SearchPage;