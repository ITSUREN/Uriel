import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { getDocument, getRelatedDocuments } from "../services/api";
import { openFileBestEffort, copyPathToClipboard } from "../utils/fileOpen";
import ResultsList from "../components/Results/ResultsList";
import "./DocumentPage.css";

function DocumentPage() {
  const { docId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

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

  const handleBack = () => {
    // location.key === "default" means this is the first entry in the
    // session's history (e.g. a direct link or a refresh) — there's nothing
    // real to go back to, so fall back to the search page.
    if (location.key !== "default") {
      navigate(-1);
    } else {
      navigate("/");
    }
  };

  const handleOpen = async () => {
    const status = await openFileBestEffort(docId);
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
        onClick={handleBack}
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
            {openStatus === "failed" && (
              <p className="document-action-note document-action-note-error">
                Couldn't open this file.
              </p>
            )}
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