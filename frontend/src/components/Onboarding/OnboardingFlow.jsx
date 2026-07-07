import { useState } from "react";
import {
  testBackendConnection,
  setApiBaseUrl,
  getApiBaseUrl,
  addDirectory,
  rebuildIndex,
  completeOnboarding,
} from "../../services/api";
import "./OnboardingFlow.css";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";

function OnboardingFlow({ startStep = 1, onComplete }) {
  const [step, setStep] = useState(startStep);

  const [backendUrl, setBackendUrl] = useState(getApiBaseUrl() || DEFAULT_BACKEND_URL);
  const [testing, setTesting] = useState(false);
  const [backendError, setBackendError] = useState(null);

  const [dirPath, setDirPath] = useState("");
  const [addingDir, setAddingDir] = useState(false);
  const [addDirError, setAddDirError] = useState(null);
  const [addedDirectories, setAddedDirectories] = useState([]);
  const [rebuilding, setRebuilding] = useState(false);
  const [rebuildError, setRebuildError] = useState(null);
  const [rebuildSuccess, setRebuildSuccess] = useState(null);
  const [finishing, setFinishing] = useState(false);
  const [finishError, setFinishError] = useState(null);

  const handleTestAndContinue = async () => {
    setTesting(true);
    setBackendError(null);

    try {
      await testBackendConnection(backendUrl);
      setApiBaseUrl(backendUrl);
      setStep(3);
    } catch {
      setBackendError(
        "Couldn't reach a valid backend at that address. Check the URL and that the server is running."
      );
    } finally {
      setTesting(false);
    }
  };

  const handleAddDirectory = (e) => {
    e.preventDefault();
    if (!dirPath.trim()) return;

    setAddingDir(true);
    setAddDirError(null);

    addDirectory(dirPath.trim())
      .then((response) => {
        setAddedDirectories((prev) => [...prev, response.data]);
        setDirPath("");
      })
      .catch((err) => {
        const detail = err.response?.data?.detail;
        setAddDirError(typeof detail === "string" ? detail : err.message);
      })
      .finally(() => {
        setAddingDir(false);
      });
  };

  const handleRebuild = () => {
    setRebuilding(true);
    setRebuildError(null);
    setRebuildSuccess(null);

    rebuildIndex()
      .then((response) => {
        setRebuildSuccess(
          `Index built successfully. ${response.data.reindexed} documents were indexed.`
        );
      })
      .catch((err) => {
        setRebuildError(err.message);
      })
      .finally(() => {
        setRebuilding(false);
      });
  };

  const handleFinish = () => {
    setFinishing(true);
    setFinishError(null);

    completeOnboarding()
      .then(() => {
        onComplete();
      })
      .catch((err) => {
        setFinishError(err.message);
      })
      .finally(() => {
        setFinishing(false);
      });
  };

  return (
    <div className="onboarding-backdrop">
      <div className="onboarding-card">
        {step === 1 && (
          <>
            <h2>Welcome to Local Document Retrieval</h2>
            <p>
              This tool searches across your local documents using BM25 or
              TF-IDF ranking, with optional query expansion. Point it at a
              running backend and a folder of documents to get started.
            </p>
            <div className="onboarding-footer">
              <button
                className="onboarding-primary-button"
                type="button"
                onClick={() => setStep(2)}
              >
                Get Started
              </button>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2>Connect to Backend</h2>
            <p>Enter the address where the search backend is running.</p>
            <input
              className="onboarding-input"
              type="text"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              placeholder={DEFAULT_BACKEND_URL}
            />
            {backendError && <p className="onboarding-error">{backendError}</p>}
            <div className="onboarding-footer">
              <button
                className="onboarding-primary-button"
                type="button"
                onClick={handleTestAndContinue}
                disabled={testing || !backendUrl.trim()}
              >
                {testing ? "Connecting..." : "Connect"}
              </button>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h2>Add a Document Directory</h2>
            <p>Enter the full absolute path to a folder to index.</p>
            <form onSubmit={handleAddDirectory}>
              <input
                className="onboarding-input"
                type="text"
                value={dirPath}
                onChange={(e) => setDirPath(e.target.value)}
                placeholder="e.g. C:\Users\you\Documents or /home/you/documents"
              />
              {addDirError && <p className="onboarding-error">{addDirError}</p>}
              <div className="onboarding-footer">
                <button
                  className="onboarding-secondary-button"
                  type="submit"
                  disabled={addingDir || !dirPath.trim()}
                >
                  {addingDir ? "Adding..." : "Add Directory"}
                </button>
              </div>
            </form>

            {addedDirectories.length > 0 && (
              <ul className="onboarding-directory-list">
                {addedDirectories.map((dir) => (
                  <li key={dir.id}>{dir.path}</li>
                ))}
              </ul>
            )}

            {addedDirectories.length > 0 && (
              <div className="onboarding-reindex">
                <p>Rebuild the index so these directories become searchable.</p>
                <button
                  className="onboarding-secondary-button"
                  type="button"
                  onClick={handleRebuild}
                  disabled={rebuilding}
                >
                  {rebuilding ? "Rebuilding..." : "Rebuild Index"}
                </button>
                {rebuildSuccess && <p className="onboarding-success">{rebuildSuccess}</p>}
                {rebuildError && <p className="onboarding-error">{rebuildError}</p>}
              </div>
            )}

            {finishError && <p className="onboarding-error">{finishError}</p>}

            <div className="onboarding-footer">
              <button
                className="onboarding-primary-button"
                type="button"
                onClick={handleFinish}
                disabled={finishing}
              >
                {finishing ? "Finishing..." : "Finish Setup"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default OnboardingFlow;