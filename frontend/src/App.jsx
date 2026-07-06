import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import SettingsModal from "./components/Settings/SettingsModal";
import SearchPage from "./pages/SearchPage";
import DocumentPage from "./pages/DocumentPage";
import "./App.css";

function App() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="app">
        <Header onSettingsClick={() => setIsSettingsOpen(true)} />

        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/document/:docId" element={<DocumentPage />} />
        </Routes>

        <SettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
        />
      </div>
    </BrowserRouter>
  );
}

export default App;