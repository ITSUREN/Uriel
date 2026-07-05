import "./ResultItem.css";

function ResultItem({ result }) {
  const { title, score, snippet, path } = result;

  return (
    <div className="result-card">
      <h3 className="result-title">{title}</h3>
      <p className="result-score">Score: {score.toFixed(3)}</p>
      <p className="result-snippet">{snippet}</p>
      <p className="result-path">{path}</p>
    </div>
  );
}

export default ResultItem;