const BASE = "http://localhost:8000";

const api = {
  async req(method, path, body, token) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Request failed");
    }
    return res.json();
  },
  get:    (path, token)       => api.req("GET",    path, null, token),
  post:   (path, body, token) => api.req("POST",   path, body, token),
  put:    (path, body, token) => api.req("PUT",    path, body, token),
  delete: (path, token)       => api.req("DELETE", path, null, token),
};

export { BASE };
export default api;
