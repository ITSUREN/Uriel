import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import { searchDocuments } from "../../services/api";
import "./SearchBar.css";

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const SearchBar = forwardRef(function SearchBar(
  { config, onResults, onError, onLoadingChange, onCorrectedTerms },
  ref
) {
  const [query, setQuery] = useState("");
  const [algorithm, setAlgorithm] = useState(config.ranking.default_algorithm);
  const [topK, setTopK] = useState(config.ranking.default_top_k);
  const [expandQuery, setExpandQuery] = useState(false);

  useEffect(() => {
    setAlgorithm(config.ranking.default_algorithm);
    setTopK(config.ranking.default_top_k);
  }, [config.ranking.default_algorithm, config.ranking.default_top_k]);

  const runSearch = (queryText) => {
    const finalQuery = queryText !== undefined ? queryText : query;

    if (queryText !== undefined) {
      setQuery(queryText);
    }

    onLoadingChange(true);
    onError(null);
    onCorrectedTerms(null);

    searchDocuments({
      query: finalQuery,
      algorithm,
      top_k: topK,
      expand_query: expandQuery,
    })
      .then((response) => {
        onResults(response.data.results);
        onCorrectedTerms(response.data.corrected_terms || null);
      })
      .catch((err) => {
        onError(err.message);
      })
      .finally(() => {
        onLoadingChange(false);
      });
  };

  // Exposed so SearchPage can re-run the search with corrected spelling
  // applied, without the frontend silently overriding what the user typed.
  useImperativeHandle(ref, () => ({
    runSearchWithCorrections: (correctedTerms) => {
      let corrected = query;
      Object.entries(correctedTerms).forEach(([original, replacement]) => {
        const pattern = new RegExp(`\\b${escapeRegExp(original)}\\b`, "gi");
        corrected = corrected.replace(pattern, replacement);
      });
      runSearch(corrected);
    },
  }));

  const handleSubmit = (e) => {
    e.preventDefault();
    runSearch();
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <input
        className="search-input"
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter search query"
      />

      <select
        className="search-algorithm"
        value={algorithm}
        onChange={(e) => setAlgorithm(e.target.value)}
      >
        <option value="bm25">bm25</option>
        <option value="tfidf">tfidf</option>
      </select>

      <input
        className="search-topk"
        type="number"
        value={topK}
        onChange={(e) => setTopK(Number(e.target.value))}
      />

      <label className="search-checkbox-label">
        <input
          type="checkbox"
          checked={expandQuery}
          onChange={(e) => setExpandQuery(e.target.checked)}
        />
        Expand Query
      </label>

      <button className="search-button" type="submit">
        Search
      </button>
    </form>
  );
});

export default SearchBar;