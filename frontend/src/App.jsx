import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import SettingsModal from "./components/Settings/SettingsModal";
import SearchPage from "./pages/SearchPage";
import DocumentPage from "./pages/DocumentPage";
import { getConfig } from "./services/api";
import "./App.css";

function App() {
  const [config, setConfig] = useState(null);
  const [configLoading, setConfigLoading] = useState(true);
  const [configError, setConfigError] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  useEffect(() => {
    getConfig()
      .then((response) => {
        setConfig(response.data);
      })
      .catch((err) => {
        setConfigError(err.message);
      })
      .finally(() => {
        setConfigLoading(false);
      });
  }, []);

  const handleConfigUpdate = (updatedConfig) => {
    setConfig(updatedConfig);
  };

  return (
    <BrowserRouter>
      <div className="app">
        <Header onSettingsClick={() => setIsSettingsOpen(true)} />

        {configLoading && (
          <p className="status-message">Loading configuration...</p>
        )}
        {configError && <p className="error-message">{configError}</p>}

        {!configLoading && !configError && config && (
          <>
            <Routes>
              <Route path="/" element={<SearchPage config={config} />} />
              <Route path="/document/:docId" element={<DocumentPage />} />
            </Routes>

            <SettingsModal
              isOpen={isSettingsOpen}
              onClose={() => setIsSettingsOpen(false)}
              config={config}
              onConfigUpdate={handleConfigUpdate}
            />
          </>
        )}
      </div>
    </BrowserRouter>
  );
}

export default App;