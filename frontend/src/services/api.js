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

export const getIndexStats = () => {
  return apiClient.get("/index/stats");
};

export const getRelatedDocuments = (docId) => {
  return apiClient.get(`/documents/${docId}/related`);
};

export default apiClient;