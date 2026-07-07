import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { attemptOpenFile, copyPathToClipboard } from "../../utils/fileOpen";
import "./ResultItem.css";

function ResultItem({ result }) {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const { doc_id, title, score, snippet, path } = result;

  const handleOpen = (e) => {
    e.stopPropagation();
    attemptOpenFile(path);
  };

  const handleCopy = async (e) => {
    e.stopPropagation();
    const success = await copyPathToClipboard(path);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  return (
    <div
      className="result-card"
      onClick={() => navigate(`/document/${doc_id}`)}
    >
      <h3 className="result-title">{title}</h3>
      <p className="result-score">Score: {score.toFixed(3)}</p>
      <p className="result-snippet">{snippet}</p>
      <p className="result-path">{path}</p>

      <div className="result-actions">
        <button className="result-action-button" onClick={handleOpen}>
          Open File
        </button>
        <button className="result-action-button" onClick={handleCopy}>
          {copied ? "Copied!" : "Copy Path"}
        </button>
      </div>
    </div>
  );
}

export default ResultItem;