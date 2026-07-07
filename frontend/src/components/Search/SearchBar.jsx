import { useState, useEffect } from "react";
import { searchDocuments } from "../../services/api";
import "./SearchBar.css";

function SearchBar({
  config,
  onResults,
  onError,
  onLoadingChange,
  onCorrectedTerms,
}) {
  const [query, setQuery] = useState("");
  const [algorithm, setAlgorithm] = useState(config.ranking.default_algorithm);
  const [topK, setTopK] = useState(config.ranking.default_top_k);
  const [expandQuery, setExpandQuery] = useState(false);

  useEffect(() => {
    setAlgorithm(config.ranking.default_algorithm);
    setTopK(config.ranking.default_top_k);
  }, [config.ranking.default_algorithm, config.ranking.default_top_k]);

  const handleSubmit = (e) => {
    e.preventDefault();

    onLoadingChange(true);
    onError(null);
    onCorrectedTerms(null);

    searchDocuments({
      query,
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
}

export default SearchBar;