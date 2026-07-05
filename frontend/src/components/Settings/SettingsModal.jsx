import { useState, useEffect } from "react";
import { getConfig, getIndexStats } from "../../services/api";
import "./SettingsModal.css";

function SettingsModal({ isOpen, onClose }) {
  const [config, setConfig] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setLoading(true);
    setError(null);

    Promise.all([getConfig(), getIndexStats()])
      .then(([configResponse, statsResponse]) => {
        setConfig(configResponse.data);
        setStats(statsResponse.data);
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

        {!loading && !error && config && stats && (
          <div className="settings-content">
            <section className="settings-section">
              <h3>Preprocessing</h3>
              <dl>
                <dt>Engine</dt>
                <dd>{config.preprocessing.engine}</dd>

                <dt>Spacy Model</dt>
                <dd>{config.preprocessing.spacy_model}</dd>

                <dt>Lowercase</dt>
                <dd>{String(config.preprocessing.lowercase)}</dd>

                <dt>Remove Stopwords</dt>
                <dd>{String(config.preprocessing.remove_stopwords)}</dd>

                <dt>Use Lemma</dt>
                <dd>{String(config.preprocessing.use_lemma)}</dd>

                <dt>Use Stemming</dt>
                <dd>{String(config.preprocessing.use_stemming)}</dd>

                <dt>Keep POS Tags</dt>
                <dd>{String(config.preprocessing.keep_pos_tags)}</dd>

                <dt>Keep Noun Chunks</dt>
                <dd>{String(config.preprocessing.keep_noun_chunks)}</dd>
              </dl>
            </section>

            <section className="settings-section">
              <h3>Ranking</h3>
              <dl>
                <dt>Default Algorithm</dt>
                <dd>{config.ranking.default_algorithm}</dd>

                <dt>Default Top K</dt>
                <dd>{config.ranking.default_top_k}</dd>

                <dt>BM25 k1</dt>
                <dd>{config.ranking.bm25.k1}</dd>

                <dt>BM25 b</dt>
                <dd>{config.ranking.bm25.b}</dd>
              </dl>
            </section>

            <section className="settings-section">
              <h3>Query Expansion</h3>
              <dl>
                <dt>WordNet Enabled</dt>
                <dd>{String(config.query_expansion.wordnet_enabled)}</dd>

                <dt>Max Synonyms Per Term</dt>
                <dd>{config.query_expansion.wordnet_max_synonyms_per_term}</dd>

                <dt>Synonym Weight</dt>
                <dd>{config.query_expansion.wordnet_synonym_weight}</dd>

                <dt>Rocchio Alpha</dt>
                <dd>{config.query_expansion.rocchio.alpha}</dd>

                <dt>Rocchio Beta</dt>
                <dd>{config.query_expansion.rocchio.beta}</dd>

                <dt>Rocchio Gamma</dt>
                <dd>{config.query_expansion.rocchio.gamma}</dd>
              </dl>
            </section>

            <section className="settings-section">
              <h3>Index</h3>
              <dl>
                <dt>Indexed Documents</dt>
                <dd>{stats.documents}</dd>

                <dt>Vocabulary Size</dt>
                <dd>{stats.vocabulary_size}</dd>
              </dl>
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
        )}
      </div>
    </div>
  );
}

export default SettingsModal;