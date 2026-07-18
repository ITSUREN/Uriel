import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from "react";
import { useSearchParams } from "react-router-dom";
import { searchDocuments } from "../../services/api";
import { IconSearch } from "../icons.jsx";
import "./SearchBar.css";

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const SearchBar = forwardRef(function SearchBar(
  { config, onResults, onError, onLoadingChange, onCorrectedTerms },
  ref
) {
  const [searchParams, setSearchParams] = useSearchParams();

  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [algorithm, setAlgorithm] = useState(
    searchParams.get("algorithm") || config.ranking.default_algorithm
  );
  const [topK, setTopK] = useState(
    searchParams.get("top_k")
      ? Number(searchParams.get("top_k"))
      : config.ranking.default_top_k
  );
  const [expandQuery, setExpandQuery] = useState(
    searchParams.get("expand") === "true"
  );

  const isFirstConfigSync = useRef(true);
  useEffect(() => {
    if (isFirstConfigSync.current) {
      isFirstConfigSync.current = false;
      return;
    }
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

    setSearchParams({
      q: finalQuery,
      algorithm,
      top_k: String(topK),
      expand: String(expandQuery),
    });

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

  // Auto-run the search once on mount if the URL already has a query —
  // this is what makes "back to search" actually restore results, since
  // SearchPage/SearchBar remount fresh each time.
  useEffect(() => {
    if (searchParams.get("q")) {
      runSearch(searchParams.get("q"));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
      <div className="search-input-wrap">
        <IconSearch size={16} className="search-input-icon" />
        <input
          className="search-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search your documents"
        />
      </div>

      <div className="search-segmented" role="group" aria-label="Ranking algorithm">
        <button
          type="button"
          className={`search-segment ${algorithm === "bm25" ? "is-active" : ""}`}
          onClick={() => setAlgorithm("bm25")}
        >
          BM25
        </button>
        <button
          type="button"
          className={`search-segment ${algorithm === "tfidf" ? "is-active" : ""}`}
          onClick={() => setAlgorithm("tfidf")}
        >
          TF-IDF
        </button>
      </div>

      <input
        className="search-topk"
        type="number"
        value={topK}
        onChange={(e) => setTopK(Number(e.target.value))}
        title="Number of results"
        aria-label="Number of results"
      />

      <label className="search-toggle">
        <span className="toggle-switch">
          <input
            type="checkbox"
            checked={expandQuery}
            onChange={(e) => setExpandQuery(e.target.checked)}
          />
          <span className="toggle-slider" />
        </span>
        Expand query
      </label>

      <button className="search-button" type="submit">
        Search
      </button>
    </form>
  );
});

export default SearchBar;