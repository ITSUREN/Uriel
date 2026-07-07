import { useState, useRef } from "react";
import SearchBar from "../components/Search/SearchBar";
import ResultsList from "../components/Results/ResultsList";

function SearchPage({ config }) {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [correctedTerms, setCorrectedTerms] = useState(null);
  const searchBarRef = useRef(null);

  const hasCorrections =
    correctedTerms && Object.keys(correctedTerms).length > 0;

  const handleUseCorrection = () => {
    searchBarRef.current?.runSearchWithCorrections(correctedTerms);
  };

  return (
    <>
      <SearchBar
        ref={searchBarRef}
        config={config}
        onResults={setResults}
        onError={setError}
        onLoadingChange={setLoading}
        onCorrectedTerms={setCorrectedTerms}
      />

      {hasCorrections && (
        <p className="spelling-correction">
          Did you mean:{" "}
          {Object.entries(correctedTerms)
            .map(([original, corrected]) => `${original} → ${corrected}`)
            .join(", ")}
          {"  "}
          <button
            type="button"
            className="spelling-correction-link"
            onClick={handleUseCorrection}
          >
            Search with corrected spelling
          </button>
        </p>
      )}

      {loading && <p className="status-message">Searching...</p>}
      {error && <p className="error-message">{error}</p>}
      {!loading && !error && results && <ResultsList results={results} />}
    </>
  );
}

export default SearchPage;