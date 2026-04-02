import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const location = useLocation();
  const [email, setEmail] = useState("admin@gov.in");
  const [password, setPassword] = useState("ChangeMe!12345");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) {
    const destination = location.state?.from?.pathname || "/dashboard";
    return <Navigate to={destination} replace />;
  }

  const onSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await login(email, password);
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page-shell">
      <section className="auth-panel">
        <h1>Government Cyber Defense</h1>
        <p>Authorized personnel access only. All access attempts are monitored.</p>

        <form onSubmit={onSubmit} className="auth-form">
          <label>
            Government Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="username"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              autoComplete="current-password"
            />
          </label>

          {error ? <div className="error-box">{error}</div> : null}

          <button type="submit" disabled={submitting}>
            {submitting ? "Authenticating..." : "Secure Login"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default LoginPage;
