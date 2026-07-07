import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getDocument, getRelatedDocuments } from "../services/api";
import { openFileBestEffort, copyPathToClipboard } from "../utils/fileOpen";
import ResultsList from "../components/Results/ResultsList";
import "./DocumentPage.css";

function DocumentPage() {
  const { docId } = useParams();
  const navigate = useNavigate();

  const [docData, setDocData] = useState(null);
  const [relatedDocuments, setRelatedDocuments] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [openStatus, setOpenStatus] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setDocData(null);
    setRelatedDocuments(null);

    Promise.all([getDocument(docId), getRelatedDocuments(docId)])
      .then(([docResponse, relatedResponse]) => {
        setDocData(docResponse.data);
        setRelatedDocuments(relatedResponse.data.results ?? relatedResponse.data);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [docId]);

  const handleOpen = async () => {
    const status = await openFileBestEffort(docData.path);
    setOpenStatus(status);
    setTimeout(() => setOpenStatus(null), 2500);
  };

  const handleCopy = async () => {
    const success = await copyPathToClipboard(docData.path);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  };

  return (
    <div className="document-page">
      <button
        className="back-button"
        type="button"
        onClick={() => navigate("/")}
      >
        ← Back to Search
      </button>

      {loading && <p className="status-message">Loading document...</p>}
      {error && <p className="error-message">{error}</p>}

      {!loading && !error && docData && (
        <>
          <div className="document-meta">
            <h2>{docData.title}</h2>
            <p className="document-path">{docData.path}</p>
            <p className="document-detail">
              Last Modified: {docData.last_modified}
            </p>
            <p className="document-detail">Length: {docData.length}</p>
            <div className="document-actions">
              <button className="document-action-button" onClick={handleOpen}>
                Open File
              </button>
              <button className="document-action-button" onClick={handleCopy}>
                {copied ? "Copied!" : "Copy Path"}
              </button>
            </div>
            {openStatus === "copied" && (
              <p className="document-action-note">
                Browser blocked direct opening — path copied instead.
              </p>
            )}
            {openStatus === "failed" && (
              <p className="document-action-note document-action-note-error">
                Couldn't open or copy the path.
              </p>
            )}
          </div>

          <div className="document-content-placeholder">
            <h3>Document Content</h3>
            <p>
              Displaying the full text of this document requires backend
              support that does not currently exist. The API only exposes
              document metadata (title, path, length, last modified) — there
              is no endpoint that returns file contents.
            </p>
          </div>

          <div className="related-documents-section">
            <h3>Related Documents</h3>
            <ResultsList results={relatedDocuments} />
          </div>
        </>
      )}
    </div>
  );
}

export default DocumentPage;