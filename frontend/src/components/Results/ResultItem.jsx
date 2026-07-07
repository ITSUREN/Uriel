import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { openFileBestEffort, copyPathToClipboard } from "../../utils/fileOpen";
import "./ResultItem.css";

function ResultItem({ result }) {
  const navigate = useNavigate();
  const [openStatus, setOpenStatus] = useState(null);
  const [copied, setCopied] = useState(false);
  const { doc_id, title, score, snippet, path } = result;

  const handleOpen = async (e) => {
    e.stopPropagation();
    const status = await openFileBestEffort(path);
    setOpenStatus(status);
    setTimeout(() => setOpenStatus(null), 2500);
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
      <span className="result-score-badge">{score.toFixed(3)}</span>
      <p
        className="result-snippet"
        dangerouslySetInnerHTML={{ __html: snippet }}
      />
      <p className="result-path">{path}</p>

      <div className="result-actions">
        <button className="result-action-button" onClick={handleOpen}>
          Open File
        </button>
        <button className="result-action-button" onClick={handleCopy}>
          {copied ? "Copied!" : "Copy Path"}
        </button>
        {openStatus === "copied" && (
          <span className="result-action-note">
            Browser blocked direct opening — path copied instead.
          </span>
        )}
        {openStatus === "failed" && (
          <span className="result-action-note result-action-note-error">
            Couldn't open or copy the path.
          </span>
        )}
      </div>
    </div>
  );
}

export default ResultItem;