import ResultItem from "./ResultItem";

function ResultsList({ results }) {
  if (!results || results.length === 0) {
    return null;
  }

  return (
    <div>
      {results.map((result) => (
        <ResultItem key={result.doc_id} result={result} />
      ))}
    </div>
  );
}

export default ResultsList;