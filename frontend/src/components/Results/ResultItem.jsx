import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { openFileBestEffort, copyPathToClipboard } from "../../utils/fileOpen";
import { IconExternal, IconCopy } from "../icons.jsx";
import "./ResultItem.css";

function ResultItem({ result }) {
  const navigate = useNavigate();
  const [openStatus, setOpenStatus] = useState(null);
  const [copied, setCopied] = useState(false);
  const { doc_id, title, score, snippet, path } = result;

  const handleOpen = async (e) => {
    e.stopPropagation();
    const status = await openFileBestEffort(doc_id);
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
    <div className="result-card" onClick={() => navigate(`/document/${doc_id}`)}>
      <div className="result-card-header">
        <h3 className="result-title">{title}</h3>
        <span className="result-score-badge">{score.toFixed(3)}</span>
      </div>

      <p
        className="result-snippet"
        dangerouslySetInnerHTML={{ __html: snippet }}
      />
      <p className="result-path">{path}</p>

      <div className="result-actions">
        <button
          className="icon-button"
          onClick={handleOpen}
          title="Open file"
          aria-label="Open file"
        >
          <IconExternal size={15} />
        </button>
        <button
          className="icon-button"
          onClick={handleCopy}
          title="Copy path"
          aria-label="Copy path"
        >
          <IconCopy size={15} />
        </button>
        {copied && <span className="result-action-note">Copied</span>}
        {openStatus === "failed" && (
          <span className="result-action-note result-action-note-error">
            Couldn't open this file.
          </span>
)}
      </div>
    </div>
  );
}

export default ResultItem;