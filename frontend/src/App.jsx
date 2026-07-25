import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  const [learningMode, setLearningMode] = useState(null);
  const [studentAttempt, setStudentAttempt] = useState("");
  const [attemptSubmitted, setAttemptSubmitted] = useState(false);
  const [reflection, setReflection] = useState("");

  const askQuestion = async () => {
    const cleanQuestion = question.trim();

    if (!cleanQuestion) {
      setError("Please enter a Business Statistics question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setFeedbackStatus("");
    setLearningMode(null);
    setStudentAttempt("");
    setAttemptSubmitted(false);
    setReflection("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/learning/hint",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: cleanQuestion,
          }),
        }
      );

      const data = await response.json();

      if (data.problem_solving) {
        setLearningMode({
          question: cleanQuestion,
          hint: data.hint,
          stage: "choice",
        });
      } else {
        await getFullSolution(cleanQuestion);
      }
    } catch (err) {
      console.error(err);
      setError("Could not connect to the FastAPI backend.");
    } finally {
      setLoading(false);
    }
  };

  const getFullSolution = async (questionText) => {
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: questionText,
          }),
        }
      );

      const data = await response.json();
      setResult(data);

      return data;
    } catch (err) {
      console.error(err);
      setError("Could not retrieve the full solution.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const showFullSolution = async () => {
    const data = await getFullSolution(
      learningMode.question
    );

    if (
      data &&
      attemptSubmitted &&
      studentAttempt.trim()
    ) {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/learning/compare",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              question: learningMode.question,
              student_attempt: studentAttempt.trim(),
              full_solution: data.answer,
            }),
          }
        );

        const compareData = await response.json();

        setReflection(
          compareData.reflection ?? ""
        );
      } catch (err) {
        console.error(err);
      }
    }

    setLearningMode({
      ...learningMode,
      stage: "solution",
    });
  };

  const submitAttempt = () => {
    if (!studentAttempt.trim()) {
      setError("Please enter your attempt before submitting.");
      return;
    }

    setError("");
    setAttemptSubmitted(true);

    setLearningMode({
      ...learningMode,
      stage: "attempt-recorded",
    });
  };

  const submitFeedback = async (feedbackValue) => {
    if (!result?.feedback_id) {
      return;
    }

    setFeedbackLoading(true);

    try {
      await fetch(
        "http://127.0.0.1:8000/api/feedback",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            trace_id: result.feedback_id,
            feedback_value: feedbackValue,
            comment:
              feedbackValue === "helpful"
                ? "User marked answer as helpful"
                : "User marked answer as not helpful",
          }),
        }
      );

      setFeedbackStatus(
        feedbackValue === "helpful"
          ? "Helpful"
          : "Not helpful"
      );
    } catch (err) {
      console.error(err);
    } finally {
      setFeedbackLoading(false);
    }
  };

  const getConfidenceClass = () => {
    const value = result?.confidence?.toLowerCase();

    if (value === "high") return "confidence-high";
    if (value === "medium") return "confidence-medium";
    if (value === "low") return "confidence-low";

    return "confidence-neutral";
  };

  return (
    <main className="app-shell">
      <section className="hero">
        <h1>AI Student Doubt Resolution Bot</h1>

        <p>
          Business Statistics support for first-year MBA /
          undergraduate management students
        </p>
      </section>

      <section className="ask-panel">
        <input
          value={question}
          placeholder="Ask your Business Statistics doubt..."
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              askQuestion();
            }
          }}
        />

        <button
          onClick={askQuestion}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </section>

      {error && (
        <div className="error-box">
          {error}
        </div>
      )}

      {learningMode && (
        <section className="learning-card">
          <span className="learning-badge">
            Learning-first mode
          </span>

          <h2>💡 Learning Hint</h2>

          <p>{learningMode.hint}</p>

          {learningMode.stage === "choice" && (
            <>
              <p>
                Would you like to try solving this yourself first,
                or would you prefer to see the full solution?
              </p>

              <div className="learning-actions">
                <button
                  onClick={() =>
                    setLearningMode({
                      ...learningMode,
                      stage: "attempt",
                    })
                  }
                >
                  I'll Try First
                </button>

                <button
                  className="secondary-button"
                  onClick={showFullSolution}
                >
                  Show Full Solution
                </button>
              </div>
            </>
          )}

          {learningMode.stage === "attempt" && (
            <>
              <textarea
                className="attempt-box"
                value={studentAttempt}
                placeholder="Write your calculation or reasoning..."
                onChange={(event) =>
                  setStudentAttempt(event.target.value)
                }
              />

              <div className="learning-actions">
                <button onClick={submitAttempt}>
                  Submit Attempt
                </button>

                <button
                  className="secondary-button"
                  onClick={showFullSolution}
                >
                  Show Full Solution Instead
                </button>
              </div>
            </>
          )}

          {learningMode.stage === "attempt-recorded" && (
            <>
              <div className="attempt-recorded">
                <strong>My attempt</strong>
                <p>{studentAttempt}</p>
              </div>

              <div className="learning-actions">
                <button onClick={showFullSolution}>
                  Show Full Solution
                </button>
              </div>
            </>
          )}
        </section>
      )}

      {result && (
        <section className="answer-card">
          <div className="answer-header">
            <h2>Answer</h2>

            <span
              className={`confidence-badge ${getConfidenceClass()}`}
            >
              Response confidence:{" "}
              {result.confidence ?? "N/A"}
            </span>
          </div>

          <div className="markdown-answer">
            <ReactMarkdown>
              {result.answer}
            </ReactMarkdown>
          </div>

          {reflection && (
            <div className="reflection-card">
              <ReactMarkdown>
                {reflection}
              </ReactMarkdown>
            </div>
          )}

          <details className="response-details">
            <summary>View response details</summary>

            <div className="details-grid">
              <div>
                <strong>Source</strong>
                <span>{result.source}</span>
              </div>

              <div>
                <strong>Model</strong>
                <span>{result.model_used}</span>
              </div>

              <div>
                <strong>Route</strong>
                <span>{result.routing_type}</span>
              </div>

              <div>
                <strong>Routing reason</strong>
                <span>{result.routing_reason}</span>
              </div>

              <div>
                <strong>Confidence basis</strong>
                <span>{result.confidence_reason}</span>
              </div>

              <div>
                <strong>Latency</strong>
                <span>{result.latency_ms} ms</span>
              </div>
            </div>
          </details>

          <div className="feedback-section">
            {!feedbackStatus ? (
              <>
                <span className="feedback-label">
                  Was this answer helpful?
                </span>

                <button
                  className="feedback-button"
                  disabled={feedbackLoading}
                  onClick={() =>
                    submitFeedback("helpful")
                  }
                >
                  👍 Helpful
                </button>

                <button
                  className="feedback-button"
                  disabled={feedbackLoading}
                  onClick={() =>
                    submitFeedback("not_helpful")
                  }
                >
                  👎 Not helpful
                </button>
              </>
            ) : (
              <span className="feedback-recorded">
                Feedback recorded: {feedbackStatus}
              </span>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;