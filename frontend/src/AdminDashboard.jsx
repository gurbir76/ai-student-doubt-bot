import { useEffect, useState } from "react";
import "./AdminDashboard.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";
const ADMIN_TOKEN_KEY = "statmentor_admin_token";

const ROOT_CAUSES = [
  "RETRIEVAL_ERROR",
  "KNOWLEDGE_GAP",
  "MODEL_ERROR",
  "PROMPT_ERROR",
  "ROUTING_ERROR",
  "GUARDRAIL_ERROR",
  "UI_OR_CONTEXT_ERROR",
];

function AdminDashboard() {
  const [token, setToken] = useState(
    () => sessionStorage.getItem(ADMIN_TOKEN_KEY) || ""
  );
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedRootCause, setSelectedRootCause] = useState({});
  const [activeFilter, setActiveFilter] = useState("All");

  const logout = (message = "") => {
    sessionStorage.removeItem(ADMIN_TOKEN_KEY);
    setToken("");
    setReviews([]);
    setSelectedRootCause({});
    setActiveFilter("All");
    setUsername("");
    setPassword("");
    setError("");
    setLoginError(message);
  };

  const authenticatedFetch = async (url, options = {}) => {
    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Bearer ${token}`);

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401 || response.status === 403) {
      logout(
        "Your admin session has expired or is no longer valid. Please sign in again."
      );
      throw new Error("ADMIN_AUTH_REQUIRED");
    }

    return response;
  };

  const login = async (event) => {
    event.preventDefault();

    const cleanUsername = username.trim();

    if (!cleanUsername || !password) {
      setLoginError("Enter both username and password.");
      return;
    }

    setLoginLoading(true);
    setLoginError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: cleanUsername,
            password,
          }),
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("INVALID_CREDENTIALS");
        }

        throw new Error("LOGIN_FAILED");
      }

      const data = await response.json();

      if (!data.access_token) {
        throw new Error("LOGIN_FAILED");
      }

      sessionStorage.setItem(
        ADMIN_TOKEN_KEY,
        data.access_token
      );
      setToken(data.access_token);
      setPassword("");
    } catch (err) {
      console.error(err);

      if (err.message === "INVALID_CREDENTIALS") {
        setLoginError("Invalid admin username or password.");
      } else {
        setLoginError(
          "Could not sign in to the governance workspace."
        );
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const loadReviews = async () => {
    if (!token) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/admin/reviews`
      );

      if (!response.ok) {
        throw new Error("Could not load governance reviews.");
      }

      const data = await response.json();
      setReviews(data.reviews ?? []);
    } catch (err) {
      if (err.message !== "ADMIN_AUTH_REQUIRED") {
        console.error(err);
        setError("Could not load governance reviews.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadReviews();
    }
    // loadReviews intentionally depends on the current token.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const classifyReview = async (reviewId) => {
    const rootCause = selectedRootCause[reviewId];

    if (!rootCause) {
      setError("Select a root cause before saving.");
      return;
    }

    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/admin/reviews/${reviewId}/root-cause`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            root_cause: rootCause,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Classification failed.");
      }

      await loadReviews();
    } catch (err) {
      if (err.message !== "ADMIN_AUTH_REQUIRED") {
        console.error(err);
        setError(
          "Could not save root cause classification."
        );
      }
    }
  };

  const resolveReview = async (reviewId) => {
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/admin/reviews/${reviewId}/resolve`,
        {
          method: "PATCH",
        }
      );

      if (!response.ok) {
        throw new Error("Resolution failed.");
      }

      await loadReviews();
    } catch (err) {
      if (err.message !== "ADMIN_AUTH_REQUIRED") {
        console.error(err);
        setError("Could not resolve governance review.");
      }
    }
  };

  const pendingCount = reviews.filter(
    (review) => review.review_status === "Pending Review"
  ).length;

  const underReviewCount = reviews.filter(
    (review) => review.review_status === "Under Review"
  ).length;

  const resolvedCount = reviews.filter(
    (review) => review.review_status === "Resolved"
  ).length;

  const filteredReviews = reviews.filter((review) => {
    if (activeFilter === "All") {
      return true;
    }

    return review.review_status === activeFilter;
  });

  const rootCauseCounts = reviews.reduce(
    (accumulator, review) => {
      const rootCause = review.root_cause;

      if (
        rootCause &&
        rootCause !== "Pending Classification"
      ) {
        accumulator[rootCause] =
          (accumulator[rootCause] || 0) + 1;
      }

      return accumulator;
    },
    {}
  );

  const rootCauseEntries = Object.entries(rootCauseCounts);

  const maxRootCauseCount = Math.max(
    ...rootCauseEntries.map(([, count]) => count),
    1
  );

  if (!token) {
    return (
      <main className="admin-login-shell">
        <section className="admin-login-card">
          <div className="admin-login-brand">
            <span className="admin-login-mark">AI</span>

            <div>
              <span className="admin-eyebrow">
                Governance Workspace
              </span>
              <h1>Admin sign in</h1>
            </div>
          </div>

          <p className="admin-login-copy">
            Sign in to review student feedback, classify
            root causes and close governance cases.
          </p>

          <form
            className="admin-login-form"
            onSubmit={login}
          >
            <label>
              <span>Username</span>
              <input
                type="text"
                value={username}
                autoComplete="username"
                placeholder="Admin username"
                onChange={(event) =>
                  setUsername(event.target.value)
                }
              />
            </label>

            <label>
              <span>Password</span>
              <input
                type="password"
                value={password}
                autoComplete="current-password"
                placeholder="Admin password"
                onChange={(event) =>
                  setPassword(event.target.value)
                }
              />
            </label>

            {loginError && (
              <div className="admin-login-error">
                {loginError}
              </div>
            )}

            <button
              className="admin-login-button"
              type="submit"
              disabled={loginLoading}
            >
              {loginLoading
                ? "Signing in..."
                : "Sign in to Governance"}
            </button>
          </form>

          <a
            className="admin-login-student-link"
            href="/"
          >
            ← Back to Student Workspace
          </a>
        </section>
      </main>
    );
  }

  return (
    <main className="admin-shell">
      <header className="admin-header">
        <div>
          <span className="admin-eyebrow">
            Governance Workspace
          </span>

          <h1>AI Response Review Dashboard</h1>

          <p>
            Review student feedback, classify root causes and
            close the governance loop.
          </p>
        </div>

        <div className="admin-header-actions">
          <span className="admin-session-badge">
            <span className="admin-session-dot" />
            Authenticated Admin
          </span>

          <a className="student-link" href="/">
            ← Student View
          </a>

          <button
            className="logout-button"
            onClick={() => logout()}
          >
            Sign out
          </button>
        </div>
      </header>

      <section className="metric-grid">
        <div className="metric-card">
          <span>Pending Review</span>
          <strong>{pendingCount}</strong>
        </div>

        <div className="metric-card">
          <span>Under Review</span>
          <strong>{underReviewCount}</strong>
        </div>

        <div className="metric-card">
          <span>Resolved</span>
          <strong>{resolvedCount}</strong>
        </div>

        <div className="metric-card">
          <span>Total Feedback Cases</span>
          <strong>{reviews.length}</strong>
        </div>
      </section>

      <section className="insight-panel">
        <div className="insight-heading">
          <div>
            <span className="section-eyebrow">
              Governance Insight
            </span>

            <h2>Root Cause Distribution</h2>

            <p>
              Shows the recurring causes behind reviewed AI responses.
            </p>
          </div>
        </div>

        {rootCauseEntries.length === 0 ? (
          <div className="chart-empty">
            Root-cause data will appear after reviews are classified.
          </div>
        ) : (
          <div className="root-cause-chart">
            {rootCauseEntries.map(([rootCause, count]) => {
              const percentage =
                (count / maxRootCauseCount) * 100;

              return (
                <div
                  className="root-cause-row"
                  key={rootCause}
                >
                  <div className="root-cause-label">
                    <span>
                      {rootCause.replaceAll("_", " ")}
                    </span>

                    <strong>{count}</strong>
                  </div>

                  <div className="root-cause-track">
                    <div
                      className="root-cause-bar"
                      style={{
                        width: `${percentage}%`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      <section className="review-section">
        <div className="review-heading">
          <div>
            <h2>Governance Review Queue</h2>
            <p>
              Negative student feedback automatically appears here.
            </p>

            <div className="review-filters">
              {[
                "All",
                "Pending Review",
                "Under Review",
                "Resolved",
              ].map((filter) => (
                <button
                  key={filter}
                  className={
                    activeFilter === filter
                      ? "filter-button active"
                      : "filter-button"
                  }
                  onClick={() =>
                    setActiveFilter(filter)
                  }
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          <button onClick={loadReviews}>
            Refresh
          </button>
        </div>

        {error && (
          <div className="admin-error">
            {error}
          </div>
        )}

        {loading ? (
          <div className="empty-state">
            Loading governance reviews...
          </div>
        ) : filteredReviews.length === 0 ? (
          <div className="empty-state">
            No governance reviews match the selected filter.
          </div>
        ) : (
          <div className="review-list">
            {filteredReviews.map((review) => (
              <article
                className="review-card"
                key={review.id}
              >
                <div className="review-card-top">
                  <div>
                    <span className="case-id">
                      Case #{review.id}
                    </span>

                    <h3>
                      {review.question ||
                        "Question not captured"}
                    </h3>
                  </div>

                  <div className="status-group">
                    <span
                      className={`priority priority-${review.review_priority.toLowerCase()}`}
                    >
                      {review.review_priority}
                    </span>

                    <span
                      className={`status status-${review.review_status
                        .toLowerCase()
                        .replaceAll(" ", "-")}`}
                    >
                      {review.review_status}
                    </span>
                  </div>
                </div>

                <div className="review-meta">
                  <div>
                    <span>Feedback</span>
                    <strong>
                      {review.feedback_value}
                    </strong>
                  </div>

                  <div>
                    <span>Root Cause</span>
                    <strong>
                      {review.root_cause}
                    </strong>
                  </div>

                  <div>
                    <span>Trace ID</span>
                    <code>{review.trace_id}</code>
                  </div>

                  <div>
                    <span>Created</span>
                    <strong>
                      {new Date(
                        review.created_at
                      ).toLocaleString()}
                    </strong>
                  </div>
                </div>

                {review.review_status !== "Resolved" && (
                  <div className="review-actions">
                    <select
                      value={
                        selectedRootCause[review.id] ?? ""
                      }
                      onChange={(event) =>
                        setSelectedRootCause({
                          ...selectedRootCause,
                          [review.id]:
                            event.target.value,
                        })
                      }
                    >
                      <option value="">
                        Select root cause
                      </option>

                      {ROOT_CAUSES.map((rootCause) => (
                        <option
                          key={rootCause}
                          value={rootCause}
                        >
                          {rootCause}
                        </option>
                      ))}
                    </select>

                    <button
                      onClick={() =>
                        classifyReview(review.id)
                      }
                    >
                      Save Classification
                    </button>

                    {review.review_status ===
                      "Under Review" && (
                      <button
                        className="resolve-button"
                        onClick={() =>
                          resolveReview(review.id)
                        }
                      >
                        Resolve Review
                      </button>
                    )}
                  </div>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default AdminDashboard;
