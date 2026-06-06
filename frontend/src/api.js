const BASE = import.meta.env.VITE_API_URL || "/api";

export const getExpenses = (filters = {}) => {
  const params = new URLSearchParams(filters);
  return fetch(`${BASE}/expenses?${params}`).then(r => r.json());
};

export const addExpense = (body) => 
  fetch(`${BASE}/expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  }).then(r => r.json());

export const deleteExpense = (id) => 
  fetch(`${BASE}/expenses/${id}`, { method: "DELETE" }).then(r => r.json());

export const undoLast = () => 
  fetch(`${BASE}/expenses/undo`, { method: "POST" }).then(r => r.json());

export const getBreakdown = (f = {}) => 
  fetch(`${BASE}/summary/breakdown?${new URLSearchParams(f)}`).then(r => r.json());

export const getMonthly = (f = {}) => 
  fetch(`${BASE}/summary/monthly?${new URLSearchParams(f)}`).then(r => r.json());

export const getCategories = () => 
  fetch(`${BASE}/categories`).then(r => r.json());
