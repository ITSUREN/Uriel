import { useState } from "react";
import { searchDocuments } from "../../services/api";

function SearchBar({ onResults, onError, onLoadingChange }) {
  const [query, setQuery] = useState("");
  const [algorithm, setAlgorithm] = useState("bm25");
  const [topK, setTopK] = useState(10);
  const [expandQuery, setExpandQuery] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();

    onLoadingChange(true);
    onError(null);

    searchDocuments({
      query,
      algorithm,
      top_k: topK,
      expand_query: expandQuery,
    })
      .then((response) => {
        onResults(response.data);
      })
      .catch((err) => {
        onError(err.message);
      })
      .finally(() => {
        onLoadingChange(false);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter search query"
      />

      <select
        value={algorithm}
        onChange={(e) => setAlgorithm(e.target.value)}
      >
        <option value="bm25">bm25</option>
      </select>

      <input
        type="number"
        value={topK}
        onChange={(e) => setTopK(Number(e.target.value))}
      />

      <label>
        <input
          type="checkbox"
          checked={expandQuery}
          onChange={(e) => setExpandQuery(e.target.checked)}
        />
        Expand Query
      </label>

      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;