import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const searchDocuments = (searchRequest) => {
  return apiClient.post("/search", searchRequest);
};

export const getConfig = () => {
  return apiClient.get("/config");
};

export const getDocuments = () => {
  return apiClient.get("/documents");
};

export const getDocument = (docId) => {
  return apiClient.get(`/documents/${docId}`);
};

export const buildDocumentFileUrl = (docId) => {
  return `${apiClient.defaults.baseURL}/documents/${docId}/file`;
};

export const getIndexStats = () => {
  return apiClient.get("/index/stats");
};

export const getRelatedDocuments = (docId) => {
  return apiClient.get(`/documents/${docId}/related`);
};

export const updatePreprocessingConfig = (data) => {
  return apiClient.put("/config/preprocessing", data);
};

export const updateRankingConfig = (data) => {
  return apiClient.put("/config/ranking", data);
};

export const updateQueryExpansionConfig = (data) => {
  return apiClient.put("/config/query-expansion", data);
};

export const rebuildIndex = () => {
  return apiClient.post("/index/rebuild");
};

export const getDirectories = () => {
  return apiClient.get("/config/directories");
};

export const addDirectory = (path) => {
  return apiClient.post("/config/directories", { path });
};

export const removeDirectory = (dirId) => {
  return apiClient.delete(`/config/directories/${dirId}`);
};

export default apiClient;