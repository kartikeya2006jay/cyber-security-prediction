const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const mergedHeaders = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: mergedHeaders,
  });

  if (response.status === 204) {
    return null;
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    let errorMessage = "Request failed";

    if (typeof payload?.detail === "string") {
      errorMessage = payload.detail;
    } else if (Array.isArray(payload?.detail) && payload.detail.length > 0) {
      errorMessage = payload.detail
        .map((entry) => entry.msg || JSON.stringify(entry))
        .join("; ");
    }

    throw new Error(errorMessage);
  }

  return payload;
}

export async function loginUser(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function fetchCurrentUser(token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return request("/auth/me", { method: "GET", headers });
}

export async function fetchUsers(token) {
  return request("/auth/users", {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function createUser(token, userPayload) {
  return request("/auth/create-user", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(userPayload),
  });
}

export async function updateUserRole(token, userId, role) {
  return request(`/auth/users/${userId}/role`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ role }),
  });
}

export async function deleteUser(token, userId) {
  return request(`/auth/users/${userId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function logoutUser() {
  return request("/auth/logout", { method: "POST" });
}

export { API_BASE_URL };
