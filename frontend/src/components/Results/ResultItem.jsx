import { useNavigate } from "react-router-dom";
import "./ResultItem.css";

function ResultItem({ result }) {
  const navigate = useNavigate();
  const { doc_id, title, score, snippet, path } = result;

  return (
    <div
      className="result-card"
      onClick={() => navigate(`/document/${doc_id}`)}
    >
      <h3 className="result-title">{title}</h3>
      <p className="result-score">Score: {score.toFixed(3)}</p>
      <p className="result-snippet">{snippet}</p>
      <p className="result-path">{path}</p>
    </div>
  );
}

export default ResultItem;