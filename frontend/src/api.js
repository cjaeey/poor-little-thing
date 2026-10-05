// In development this is your local FastAPI server.
// In production, Vercel sets VITE_API_URL to your Render URL.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json();
}

export function getRecommendation(quiz) {
  return request("/recommend", { method: "POST", body: JSON.stringify(quiz) });
}

export function searchProducts(query) {
  return request(`/products?q=${encodeURIComponent(query)}&limit=8`);
}

export function checkConflicts(productIds) {
  return request("/check-conflicts", {
    method: "POST",
    body: JSON.stringify({ product_ids: productIds }),
  });
}