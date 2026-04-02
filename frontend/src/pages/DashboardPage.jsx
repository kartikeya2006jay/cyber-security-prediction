import { useEffect, useState } from "react";
import { createUser, deleteUser, fetchUsers, updateUserRole } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

const ROLE_SECTIONS = {
  SUPER_ADMIN: "Admin: full system and user management",
  SECURITY_ANALYST: "Threat telemetry and monitoring",
  INCIDENT_RESPONDER: "Active response actions and containment",
  AUDITOR: "Read-only compliance and incident reports",
};

function validatePasswordPolicy(password) {
  if (password.length < 12) {
    return "Password must be at least 12 characters";
  }
  if (password.length > 72) {
    return "Password cannot exceed 72 characters";
  }

  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);

  if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) {
    return "Password must include uppercase, lowercase, number, and special character";
  }

  return null;
}

function DashboardPage() {
  const { user, token, logout } = useAuth();
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    password: "",
    role: "SECURITY_ANALYST",
  });
  const [status, setStatus] = useState("");
  const [statusType, setStatusType] = useState("success");

  useEffect(() => {
    if (user?.role === "SUPER_ADMIN" && token) {
      fetchUsers(token)
        .then(setUsers)
        .catch(() => setUsers([]));
    }
  }, [user, token]);

  const createUserHandler = async (event) => {
    event.preventDefault();
    setStatus("");
    setStatusType("success");

    const passwordError = validatePasswordPolicy(newUser.password);
    if (passwordError) {
      setStatusType("error");
      setStatus(passwordError);
      return;
    }

    try {
      await createUser(token, newUser);
      const refreshed = await fetchUsers(token);
      setUsers(refreshed);
      setNewUser({ name: "", email: "", password: "", role: "SECURITY_ANALYST" });
      setStatusType("success");
      setStatus("User created successfully");
    } catch (err) {
      setStatusType("error");
      setStatus(err.message || "Failed to create user");
    }
  };

  const onRoleChange = async (userId, role) => {
    setStatus("");
    setStatusType("success");
    try {
      await updateUserRole(token, userId, role);
      const refreshed = await fetchUsers(token);
      setUsers(refreshed);
      setStatusType("success");
      setStatus("Role updated successfully");
    } catch (err) {
      setStatusType("error");
      setStatus(err.message || "Failed to update role");
    }
  };

  const onDeleteUser = async (userId) => {
    setStatus("");
    setStatusType("success");
    try {
      await deleteUser(token, userId);
      const refreshed = await fetchUsers(token);
      setUsers(refreshed);
      setStatusType("success");
      setStatus("User deleted successfully");
    } catch (err) {
      setStatusType("error");
      setStatus(err.message || "Failed to delete user");
    }
  };

  return (
    <main className="page-shell dashboard-shell">
      <header className="top-bar">
        <div>
          <h1>Cyber Threat Operations Dashboard</h1>
          <p>{ROLE_SECTIONS[user.role]}</p>
        </div>
        <button onClick={logout}>Logout</button>
      </header>

      <section className="grid-panel">
        {(user.role === "SUPER_ADMIN" || user.role === "SECURITY_ANALYST") && (
          <article className="panel-card">
            <h2>Threat Monitoring</h2>
            <p>Live anomaly feed, actor scoring, and active detections.</p>
          </article>
        )}

        {(user.role === "SUPER_ADMIN" || user.role === "INCIDENT_RESPONDER") && (
          <article className="panel-card">
            <h2>Response Controls</h2>
            <p>Block IP, isolate workloads, and trigger containment workflows.</p>
          </article>
        )}

        {(user.role === "SUPER_ADMIN" || user.role === "AUDITOR") && (
          <article className="panel-card">
            <h2>Audit Reports</h2>
            <p>Immutable login audits, incident timelines, and compliance exports.</p>
          </article>
        )}
      </section>

      {user.role === "SUPER_ADMIN" && (
        <section className="admin-panel">
          <h2>User Management</h2>
          <form onSubmit={createUserHandler} className="admin-form">
            <input
              placeholder="Full name"
              value={newUser.name}
              onChange={(event) => setNewUser({ ...newUser, name: event.target.value })}
              required
            />
            <input
              placeholder="user@gov.in"
              type="email"
              value={newUser.email}
              onChange={(event) => setNewUser({ ...newUser, email: event.target.value })}
              required
            />
            <input
              placeholder="Strong password"
              type="password"
              minLength={12}
              maxLength={72}
              value={newUser.password}
              onChange={(event) =>
                setNewUser({ ...newUser, password: event.target.value })
              }
              required
            />
            <select
              value={newUser.role}
              onChange={(event) => setNewUser({ ...newUser, role: event.target.value })}
            >
              <option value="SECURITY_ANALYST">SECURITY_ANALYST</option>
              <option value="INCIDENT_RESPONDER">INCIDENT_RESPONDER</option>
              <option value="AUDITOR">AUDITOR</option>
              <option value="SUPER_ADMIN">SUPER_ADMIN</option>
            </select>
            <button type="submit">Create User</button>
          </form>

          {status ? (
            <p className={`status-line ${statusType === "error" ? "status-error" : "status-success"}`}>
              {status}
            </p>
          ) : null}

          <div className="user-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Last Login</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((row) => (
                  <tr key={row.id}>
                    <td>{row.name}</td>
                    <td>{row.email}</td>
                    <td>
                      <select
                        value={row.role}
                        onChange={(event) => onRoleChange(row.id, event.target.value)}
                      >
                        <option value="SECURITY_ANALYST">SECURITY_ANALYST</option>
                        <option value="INCIDENT_RESPONDER">INCIDENT_RESPONDER</option>
                        <option value="AUDITOR">AUDITOR</option>
                        <option value="SUPER_ADMIN">SUPER_ADMIN</option>
                      </select>
                    </td>
                    <td>{row.last_login ? new Date(row.last_login).toLocaleString() : "Never"}</td>
                    <td>
                      <button type="button" onClick={() => onDeleteUser(row.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}

export default DashboardPage;
