import { useState } from "react";
import { addDirectory } from "../../services/api";
import "./DirectorySetupModal.css";

function DirectorySetupModal({ isOpen, onClose, onDirectoryAdded }) {
  const [step, setStep] = useState("confirm");
  const [path, setPath] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) {
    return null;
  }

  const handleDecline = () => {
    onClose();
  };

  const handleConfirm = () => {
    setStep("input");
  };

  const handleBack = () => {
    setStep("confirm");
    setError(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!path.trim()) {
      return;
    }

    setSubmitting(true);
    setError(null);

    addDirectory(path.trim())
      .then((response) => {
        onDirectoryAdded(response.data);
        setPath("");
        setStep("confirm");
        onClose();
      })
      .catch((err) => {
        const detail = err.response?.data?.detail;
        setError(typeof detail === "string" ? detail : err.message);
      })
      .finally(() => {
        setSubmitting(false);
      });
  };

  return (
    <div className="dir-setup-backdrop">
      <div className="dir-setup-modal">
        {step === "confirm" && (
          <>
            <h2>Add a Document Directory?</h2>
            <p>
              No watched directories are configured yet, so there's nothing
              to search. Would you like to add one now?
            </p>
            <div className="dir-setup-footer">
              <button
                className="dir-setup-secondary-button"
                type="button"
                onClick={handleDecline}
              >
                Not Now
              </button>
              <button
                className="dir-setup-primary-button"
                type="button"
                onClick={handleConfirm}
              >
                Yes, Add Directory
              </button>
            </div>
          </>
        )}

        {step === "input" && (
          <form onSubmit={handleSubmit}>
            <h2>Add Directory</h2>
            <p>Enter the full absolute path to the folder to index.</p>
            <input
              className="dir-setup-input"
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="e.g. C:\Users\you\Documents or /home/you/documents"
              autoFocus
            />
            {error && <p className="dir-setup-error">{error}</p>}
            <div className="dir-setup-footer">
              <button
                className="dir-setup-secondary-button"
                type="button"
                onClick={handleBack}
                disabled={submitting}
              >
                Back
              </button>
              <button
                className="dir-setup-primary-button"
                type="submit"
                disabled={submitting || !path.trim()}
              >
                {submitting ? "Adding..." : "Add Directory"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default DirectorySetupModal;