import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { fetchCurrentUser, loginUser, logoutUser } from "../api/authApi";

const ACCESS_TOKEN_KEY = "cyber_access_token";
const USER_KEY = "cyber_user";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(ACCESS_TOKEN_KEY));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      if (!token) {
        setUser(null);
        localStorage.removeItem(USER_KEY);
        setLoading(false);
        return;
      }

      try {
        const me = await fetchCurrentUser(token);
        setUser(me);
        localStorage.setItem(USER_KEY, JSON.stringify(me));
      } catch {
        setUser(null);
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        setToken(null);
        localStorage.removeItem(USER_KEY);
      } finally {
        setLoading(false);
      }
    };

    restoreSession();
  }, [token]);

  const login = async (email, password) => {
    const payload = await loginUser(email, password);

    // Cookie is preferred (httpOnly set by backend). Token fallback supports legacy clients.
    if (payload.access_token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, payload.access_token);
      setToken(payload.access_token);
    }

    const me = await fetchCurrentUser(payload.access_token || null);
    setUser(me);
    localStorage.setItem(USER_KEY, JSON.stringify(me));
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch {
      // Keep local cleanup even if network logout fails.
    }
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
    }),
    [user, token, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
