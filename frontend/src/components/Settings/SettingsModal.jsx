import { useState, useEffect } from "react";
import {
  getConfig,
  getIndexStats,
  updatePreprocessingConfig,
  updateRankingConfig,
  updateQueryExpansionConfig,
} from "../../services/api";
import "./SettingsModal.css";

function SettingsModal({ isOpen, onClose }) {
  const [config, setConfig] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const [preprocessingForm, setPreprocessingForm] = useState(null);
  const [rankingForm, setRankingForm] = useState(null);
  const [queryExpansionForm, setQueryExpansionForm] = useState(null);

  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [reindexMessage, setReindexMessage] = useState(null);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setLoading(true);
    setError(null);
    setSaveError(null);
    setReindexMessage(null);

    Promise.all([getConfig(), getIndexStats()])
      .then(([configResponse, statsResponse]) => {
        setConfig(configResponse.data);
        setStats(statsResponse.data);
        setPreprocessingForm(configResponse.data.preprocessing);
        setRankingForm(configResponse.data.ranking);
        setQueryExpansionForm(configResponse.data.query_expansion);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  const handlePreprocessingChange = (field, value) => {
    setPreprocessingForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleLemmaToggle = (value) => {
    setPreprocessingForm((prev) => ({
      ...prev,
      use_lemma: value,
      use_stemming: value ? false : prev.use_stemming,
    }));
  };

  const handleStemmingToggle = (value) => {
    setPreprocessingForm((prev) => ({
      ...prev,
      use_stemming: value,
      use_lemma: value ? false : prev.use_lemma,
    }));
  };

  const handleRankingChange = (field, value) => {
    setRankingForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleBm25Change = (field, value) => {
    setRankingForm((prev) => ({
      ...prev,
      bm25: { ...prev.bm25, [field]: value },
    }));
  };

  const handleQueryExpansionChange = (field, value) => {
    setQueryExpansionForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleRocchioChange = (field, value) => {
    setQueryExpansionForm((prev) => ({
      ...prev,
      rocchio: { ...prev.rocchio, [field]: value },
    }));
  };

  const handleCancel = () => {
    onClose();
  };

  const handleSave = () => {
    setSaving(true);
    setSaveError(null);
    setReindexMessage(null);

    Promise.all([
      updatePreprocessingConfig(preprocessingForm),
      updateRankingConfig(rankingForm),
      updateQueryExpansionConfig(queryExpansionForm),
    ])
      .then(([preprocessingRes, rankingRes, queryExpansionRes]) => {
        setPreprocessingForm(preprocessingRes.data.config);
        setRankingForm(rankingRes.data.config);
        setQueryExpansionForm(queryExpansionRes.data.config);

        if (preprocessingRes.data.reindex_required) {
          setReindexMessage(preprocessingRes.data.message);
        }
      })
      .catch((err) => {
        setSaveError(err.message);
      })
      .finally(() => {
        setSaving(false);
      });
  };

  return (
    <div className="settings-backdrop" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="settings-close" type="button" onClick={onClose}>
            ×
          </button>
        </div>

        {loading && <p className="settings-status">Loading settings...</p>}
        {error && <p className="settings-error">{error}</p>}

        {!loading &&
          !error &&
          config &&
          stats &&
          preprocessingForm &&
          rankingForm &&
          queryExpansionForm && (
            <>
              <div className="settings-content">
                <section className="settings-section">
                  <h3>Preprocessing</h3>

                  <div className="settings-row">
                    <label>Engine</label>
                    <select
                      className="settings-select"
                      value={preprocessingForm.engine}
                      onChange={(e) =>
                        handlePreprocessingChange("engine", e.target.value)
                      }
                    >
                      <option value="spacy">spacy</option>
                      <option value="traditional">traditional</option>
                    </select>
                  </div>

                  <div className="settings-row">
                    <label>Spacy Model</label>
                    <select
                      className="settings-select"
                      value={preprocessingForm.spacy_model}
                      onChange={(e) =>
                        handlePreprocessingChange(
                          "spacy_model",
                          e.target.value
                        )
                      }
                    >
                      <option value="en_core_web_sm">en_core_web_sm</option>
                    </select>
                  </div>

                  <div className="settings-row">
                    <label>Lowercase</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={preprocessingForm.lowercase}
                        onChange={(e) =>
                          handlePreprocessingChange(
                            "lowercase",
                            e.target.checked
                          )
                        }
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="settings-row">
                    <label>Remove Stopwords</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={preprocessingForm.remove_stopwords}
                        onChange={(e) =>
                          handlePreprocessingChange(
                            "remove_stopwords",
                            e.target.checked
                          )
                        }
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="settings-row">
                    <label>Use Lemma</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={preprocessingForm.use_lemma}
                        onChange={(e) => handleLemmaToggle(e.target.checked)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="settings-row">
                    <label>Use Stemming</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={preprocessingForm.use_stemming}
                        onChange={(e) =>
                          handleStemmingToggle(e.target.checked)
                        }
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="settings-row">
                    <label>Keep POS Tags</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={preprocessingForm.keep_pos_tags}
                        onChange={(e) =>
                          handlePreprocessingChange(
                            "keep_pos_tags",
                            e.target.checked
                          )
                        }
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="settings-row">
                    <label>Keep Noun Chunks</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={preprocessingForm.keep_noun_chunks}
                        onChange={(e) =>
                          handlePreprocessingChange(
                            "keep_noun_chunks",
                            e.target.checked
                          )
                        }
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>
                </section>

                <section className="settings-section">
                  <h3>Ranking</h3>

                  <div className="settings-row">
                    <label>Default Algorithm</label>
                    <select
                      className="settings-select"
                      value={rankingForm.default_algorithm}
                      onChange={(e) =>
                        handleRankingChange(
                          "default_algorithm",
                          e.target.value
                        )
                      }
                    >
                      <option value="bm25">bm25</option>
                      <option value="tfidf">tfidf</option>
                    </select>
                  </div>

                  <div className="settings-row">
                    <label>Default Top K</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      value={rankingForm.default_top_k}
                      onChange={(e) =>
                        handleRankingChange(
                          "default_top_k",
                          Number(e.target.value)
                        )
                      }
                    />
                  </div>

                  <div className="settings-row">
                    <label>BM25 k1</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      step="0.01"
                      value={rankingForm.bm25.k1}
                      onChange={(e) =>
                        handleBm25Change("k1", Number(e.target.value))
                      }
                    />
                  </div>

                  <div className="settings-row">
                    <label>BM25 b</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      step="0.01"
                      value={rankingForm.bm25.b}
                      onChange={(e) =>
                        handleBm25Change("b", Number(e.target.value))
                      }
                    />
                  </div>
                </section>

                <section className="settings-section">
                  <h3>Query Expansion</h3>

                  <div className="settings-row">
                    <label>WordNet Enabled</label>
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={queryExpansionForm.wordnet_enabled}
                        onChange={(e) =>
                          handleQueryExpansionChange(
                            "wordnet_enabled",
                            e.target.checked
                          )
                        }
                      />
                      <span className="toggle-slider"></span>
                    </label>
                  </div>

                  <div className="settings-row">
                    <label>Max Synonyms Per Term</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      value={queryExpansionForm.wordnet_max_synonyms_per_term}
                      onChange={(e) =>
                        handleQueryExpansionChange(
                          "wordnet_max_synonyms_per_term",
                          Number(e.target.value)
                        )
                      }
                    />
                  </div>

                  <div className="settings-row">
                    <label>Synonym Weight</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      step="0.01"
                      value={queryExpansionForm.wordnet_synonym_weight}
                      onChange={(e) =>
                        handleQueryExpansionChange(
                          "wordnet_synonym_weight",
                          Number(e.target.value)
                        )
                      }
                    />
                  </div>

                  <div className="settings-row">
                    <label>Rocchio Alpha</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      step="0.01"
                      value={queryExpansionForm.rocchio.alpha}
                      onChange={(e) =>
                        handleRocchioChange("alpha", Number(e.target.value))
                      }
                    />
                  </div>

                  <div className="settings-row">
                    <label>Rocchio Beta</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      step="0.01"
                      value={queryExpansionForm.rocchio.beta}
                      onChange={(e) =>
                        handleRocchioChange("beta", Number(e.target.value))
                      }
                    />
                  </div>

                  <div className="settings-row">
                    <label>Rocchio Gamma</label>
                    <input
                      className="settings-input-number"
                      type="number"
                      step="0.01"
                      value={queryExpansionForm.rocchio.gamma}
                      onChange={(e) =>
                        handleRocchioChange("gamma", Number(e.target.value))
                      }
                    />
                  </div>
                </section>

                <section className="settings-section">
                  <h3>Index</h3>

                  <div className="settings-row">
                    <label>Indexed Documents</label>
                    <span className="settings-static-value">
                      {stats.documents}
                    </span>
                  </div>

                  <div className="settings-row">
                    <label>Vocabulary Size</label>
                    <span className="settings-static-value">
                      {stats.vocabulary_size}
                    </span>
                  </div>
                </section>

                <section className="settings-section">
                  <h3>Watched Directories</h3>
                  {config.directories.length === 0 ? (
                    <p>No directories configured.</p>
                  ) : (
                    <ul className="settings-directory-list">
                      {config.directories.map((dir) => (
                        <li key={dir.id}>
                          {dir.path} {dir.is_default && "(default)"}
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              </div>

              {reindexMessage && (
                <p className="settings-reindex-message">{reindexMessage}</p>
              )}
              {saveError && <p className="settings-error">{saveError}</p>}

              <div className="settings-footer">
                <button
                  className="settings-cancel-button"
                  type="button"
                  onClick={handleCancel}
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  className="settings-save-button"
                  type="button"
                  onClick={handleSave}
                  disabled={saving}
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </>
          )}
      </div>
    </div>
  );
}

export default SettingsModal;