import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import VisualExplanation from "./VisualExplanation.jsx";
import "./App.css";
import "./VisualExplanation.css";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const QUICK_PROMPTS = [
  {
    icon: "x̄",
    title: "Mean, Median & Mode",
    description: "Central tendency made simple",
    prompt: "Explain the difference between mean, median and mode with a simple example.",
  },
  {
    icon: "σ",
    title: "Standard Deviation",
    description: "Understand spread and variability",
    prompt: "Explain variance and standard deviation with a simple example.",
  },
  {
    icon: "P",
    title: "Probability",
    description: "Events, rules and conditional probability",
    prompt: "What is conditional probability? Explain it with an easy example.",
  },
  {
    icon: "N",
    title: "Normal Distribution",
    description: "Z-scores and probability areas",
    prompt: "Explain normal distribution and z-scores in beginner-friendly language.",
  },
  {
    icon: "H₀",
    title: "Hypothesis Testing",
    description: "p-values and decision making",
    prompt: "Explain hypothesis testing and p-value in beginner-friendly language.",
  },
  {
    icon: "↗",
    title: "Correlation & Regression",
    description: "Relationships and prediction",
    prompt: "Compare correlation and simple linear regression and explain when each is used.",
  },
];

function App() {
  const [question, setQuestion] = useState("");
  const [activeQuestion, setActiveQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  const [learningMode, setLearningMode] = useState(null);
  const [studentAttempt, setStudentAttempt] = useState("");
  const [attemptSubmitted, setAttemptSubmitted] = useState(false);
  const [reflection, setReflection] = useState("");
  const [recentQuestions, setRecentQuestions] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);

  const resetResponseState = () => {
    setResult(null);
    setFeedbackStatus("");
    setLearningMode(null);
    setStudentAttempt("");
    setAttemptSubmitted(false);
    setReflection("");
    setError("");
  };

  const askQuestion = async (questionOverride = null) => {
    const cleanQuestion = (
      questionOverride ?? question
    ).trim();

    if (!cleanQuestion) {
      setError("Please enter a Business Statistics question.");
      return;
    }

    if (activeQuestion && result) {
      setConversationHistory((current) => [
        ...current,
        {
          question: activeQuestion,
          result,
          reflection,
        },
      ]);
    }

    setActiveQuestion(cleanQuestion);
    setQuestion("");
    setRecentQuestions((current) => {
      const deduplicated = current.filter(
        (item) => item.toLowerCase() !== cleanQuestion.toLowerCase()
      );
      return [cleanQuestion, ...deduplicated].slice(0, 5);
    });
    resetResponseState();
    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/learning/hint`,
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

      if (!response.ok) {
        throw new Error(
          `Learning hint request failed with status ${response.status}`
        );
      }

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
    setError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chat`,
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

      if (!response.ok) {
        throw new Error(
          `Chat request failed with status ${response.status}`
        );
      }

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

  const showFullSolution = async (attemptOverride = "") => {
    if (!learningMode?.question) {
      return;
    }

    const attemptToCompare =
      attemptOverride.trim() ||
      (attemptSubmitted ? studentAttempt.trim() : "");

    const data = await getFullSolution(
      learningMode.question
    );

    if (data && attemptToCompare) {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/learning/compare`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              question: learningMode.question,
              student_attempt: attemptToCompare,
              full_solution: data.answer,
            }),
          }
        );

        if (!response.ok) {
          throw new Error(
            `Comparison request failed with status ${response.status}`
          );
        }

        const compareData = await response.json();

        setReflection(
          compareData.reflection ?? ""
        );
      } catch (err) {
        console.error(err);
        setReflection(
          "### Reflection on Your Attempt\nI could not compare your attempt right now."
        );
      }
    }

    setLearningMode({
      ...learningMode,
      stage: "solution",
    });
  };

  const submitAttempt = async () => {
    const cleanAttempt = studentAttempt.trim();

    if (!cleanAttempt) {
      setError("Please enter your attempt before submitting.");
      return;
    }

    setError("");
    setAttemptSubmitted(true);

    await showFullSolution(cleanAttempt);
  };

  const submitFeedback = async (feedbackValue) => {
    if (!result?.feedback_id || feedbackStatus) {
      return;
    }

    setFeedbackLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/feedback`,
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
            question: activeQuestion,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Feedback request failed with status ${response.status}`
        );
      }

      const data = await response.json();

      if (data.status === "success") {
        setFeedbackStatus(
          feedbackValue === "helpful"
            ? "Helpful"
            : "Not helpful"
        );
      } else {
        setFeedbackStatus(
          "Feedback could not be recorded."
        );
      }
    } catch (err) {
      console.error(err);
      setFeedbackStatus(
        "Feedback could not be recorded."
      );
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

  const isConversationalQuestion = () => {
    const normalizedQuestion = activeQuestion
      .trim()
      .toLowerCase()
      .replace(/[?.!]+$/, "");

    const conversationalQuestions = [
      "who are you",
      "what are you",
      "what can you do",
      "hello",
      "hi",
      "hey",
    ];

    return conversationalQuestions.includes(normalizedQuestion);
  };

  const getAnswerTitle = () => {
    if (isConversationalQuestion()) {
      return "Answer";
    }

    if (learningMode) {
      return "Full solution";
    }

    return "Here’s the explanation";
  };

  const getConfidenceLabel = () => {
    const confidence = result?.confidence;

    if (
      !confidence ||
      confidence.toLowerCase() === "n/a" ||
      confidence.toLowerCase() === "not applicable"
    ) {
      return isConversationalQuestion()
        ? "General response"
        : "Confidence not applicable";
    }

    return `${confidence} confidence`;
  };

  const hasConversation =
    Boolean(activeQuestion) ||
    Boolean(learningMode) ||
    Boolean(result);

  return (
    <div className="student-app">
      <main className="student-shell">
        <section className="student-intro">
          <span className="eyebrow">Student learning workspace</span>
          <h1>Business Statistics, explained clearly.</h1>
          <p>
            Ask concepts, solve numerical problems, and learn through
            course-grounded explanations and guided practice.
          </p>
        </section>

        {!hasConversation && (
          <section className="learning-home">
            <div className="home-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">Popular topics</span>
                  <h2>What would you like to learn?</h2>
                </div>
                <span className="section-note">
                  Choose a topic to start a question
                </span>
              </div>

              <div className="topic-grid">
                {QUICK_PROMPTS.map((item) => (
                  <button
                    className="topic-card"
                    key={item.title}
                    onClick={() => {
                      setQuestion(item.prompt);
                      setError("");
                    }}
                  >
                    <span className="topic-icon">{item.icon}</span>
                    <span className="topic-copy">
                      <strong>{item.title}</strong>
                      <small>{item.description}</small>
                    </span>
                    <span className="topic-arrow">→</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="home-section recent-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">Recent questions</span>
                  <h2>Pick up where you left off</h2>
                </div>
                <span className="section-note">
                  Current browser session
                </span>
              </div>

              {recentQuestions.length === 0 ? (
                <div className="recent-empty">
                  <div className="recent-empty-icon">↺</div>
                  <div>
                    <strong>Your recent questions will appear here.</strong>
                    <p>
                      Ask a concept, numerical problem, interpretation,
                      or comparison question to build your learning history.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="recent-list">
                  {recentQuestions.map((item, index) => (
                    <button
                      className="recent-item"
                      key={`${item}-${index}`}
                      onClick={() => {
                        setQuestion(item);
                        setError("");
                      }}
                    >
                      <span className="recent-index">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span className="recent-question">{item}</span>
                      <span className="recent-arrow">→</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}

        <section className="conversation-panel">
          {conversationHistory.map((entry, index) => (
            <div className="history-exchange" key={`${entry.question}-${index}`}>
              <div className="message-row user-row">
                <div className="message-avatar user-avatar">You</div>
                <div className="message-bubble user-bubble">
                  <span className="message-label">Your question</span>
                  <p>{entry.question}</p>
                </div>
              </div>

              <div className="message-row assistant-row">
                <div className="message-avatar assistant-avatar">AI</div>

                <section className="answer-card previous-answer-card">
                  <div className="answer-header">
                    <div>
                      <span className="answer-kicker">Previous answer</span>
                      <h2>Here’s the explanation</h2>
                    </div>
                  </div>

                  <div className="markdown-answer">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {entry.result?.answer ?? ""}
                    </ReactMarkdown>
                  </div>

                  {entry.reflection && (
                    <div className="reflection-card">
                      <div className="reflection-heading">
                        <span>↺</span>
                        <strong>Reflection on your attempt</strong>
                      </div>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {entry.reflection}
                      </ReactMarkdown>
                    </div>
                  )}

                  {entry.result?.visual_type && (
                    <VisualExplanation
                      visualType={entry.result.visual_type}
                    />
                  )}

                  <details className="response-details">
                    <summary>
                      <span>Previous response details</span>
                      <small>Source, model and routing</small>
                    </summary>

                    <div className="details-grid">
                      <div>
                        <span>Source</span>
                        <strong>{entry.result?.source ?? "N/A"}</strong>
                      </div>

                      <div>
                        <span>Model</span>
                        <strong>{entry.result?.model_used ?? "N/A"}</strong>
                      </div>

                      <div>
                        <span>Route</span>
                        <strong>{entry.result?.routing_type ?? "N/A"}</strong>
                      </div>

                      <div>
                        <span>Latency</span>
                        <strong>{entry.result?.latency_ms ?? "N/A"} ms</strong>
                      </div>

                      <div>
                        <span>Assurance score</span>
                        <strong>
                          {entry.result?.assurance_score ?? "N/A"}/100
                        </strong>
                      </div>

                      <div>
                        <span>Hallucination risk</span>
                        <strong>
                          {entry.result?.hallucination_risk ?? "N/A"}
                        </strong>
                      </div>
                    </div>
                  </details>
                </section>
              </div>
            </div>
          ))}

          {activeQuestion && (
            <div className="message-row user-row">
              <div className="message-avatar user-avatar">You</div>
              <div className="message-bubble user-bubble">
                <span className="message-label">Your question</span>
                <p>{activeQuestion}</p>
              </div>
            </div>
          )}

          {error && (
            <div className="error-box">
              <strong>Something needs attention</strong>
              <span>{error}</span>
            </div>
          )}

          {learningMode && learningMode.stage !== "solution" && (
            <div className="message-row assistant-row">
              <div className="message-avatar assistant-avatar">AI</div>

              <section className="learning-card">
                <div className="learning-card-header">
                  <span className="learning-icon">✦</span>
                  <div>
                    <span className="learning-badge">
                      Learning-first mode
                    </span>
                    <h2>Pause and think first</h2>
                  </div>
                </div>

                <div className="hint-box">
                  <span>Hint</span>
                  <p>{learningMode.hint}</p>
                </div>

                {learningMode.stage === "choice" && (
                  <>
                    <p className="learning-prompt">
                      Would you like to work it out yourself first,
                      or see the complete solution now?
                    </p>

                    <div className="learning-actions">
                      <button
                        className="primary-action"
                        onClick={() =>
                          setLearningMode({
                            ...learningMode,
                            stage: "attempt",
                          })
                        }
                      >
                        ✎ I'll Try First
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
                    <label className="attempt-label" htmlFor="attempt">
                      Your working
                    </label>

                    <textarea
                      id="attempt"
                      className="attempt-box"
                      value={studentAttempt}
                      placeholder="Write your calculation, reasoning, or answer here..."
                      onChange={(event) =>
                        setStudentAttempt(event.target.value)
                      }
                    />

                    <div className="learning-actions">
                      <button
                        className="primary-action"
                        onClick={submitAttempt}
                      >
                        Submit & Compare
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
                      <span className="attempt-status">✓ Attempt recorded</span>
                      <strong>Your attempt</strong>
                      <p>{studentAttempt}</p>
                    </div>

                    <div className="learning-actions">
                      <button
                        className="primary-action"
                        onClick={showFullSolution}
                      >
                        Compare with Full Solution
                      </button>
                    </div>
                  </>
                )}
              </section>
            </div>
          )}

          {loading && (
            <div className="message-row assistant-row">
              <div className="message-avatar assistant-avatar">AI</div>
              <div className="thinking-card">
                <span className="thinking-dots">
                  <i />
                  <i />
                  <i />
                </span>
                <div>
                  <strong>Working on your question</strong>
                  <small>
                    Searching approved course material and selecting
                    the best response path...
                  </small>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div className="message-row assistant-row">
              <div className="message-avatar assistant-avatar">AI</div>

              <section className="answer-card">
                <div className="answer-header">
                  <div>
                    <span className="answer-kicker">Course-grounded answer</span>
                    <h2>{getAnswerTitle()}</h2>
                  </div>

                  <span
                    className={`confidence-badge ${getConfidenceClass()}`}
                  >
                    <span className="confidence-dot" />
                    {getConfidenceLabel()}
                  </span>
                </div>

                <div className="markdown-answer">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {result.answer}
                  </ReactMarkdown>
                </div>

                {reflection && (
                  <div className="reflection-card">
                    <div className="reflection-heading">
                      <span>↺</span>
                      <strong>Reflection on your attempt</strong>
                    </div>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {reflection}
                    </ReactMarkdown>
                  </div>
                )}

                {result.visual_type && (
                  <VisualExplanation
                    visualType={result.visual_type}
                  />
                )}

                <details className="response-details">
                  <summary>
                    <span>Response details</span>
                    <small>
                      Source, model, routing and performance
                    </small>
                  </summary>

                  <div className="details-grid">
                    <div>
                      <span>Source</span>
                      <strong>{result.source ?? "N/A"}</strong>
                    </div>

                    <div>
                      <span>Model</span>
                      <strong>{result.model_used ?? "N/A"}</strong>
                    </div>

                    <div>
                      <span>Route</span>
                      <strong>{result.routing_type ?? "N/A"}</strong>
                    </div>

                    <div>
                      <span>Latency</span>
                      <strong>{result.latency_ms ?? "N/A"} ms</strong>
                    </div>

                    <div>
                      <span>Input tokens</span>
                      <strong>{result.input_tokens ?? "N/A"}</strong>
                    </div>

                    <div>
                      <span>Output tokens</span>
                      <strong>{result.output_tokens ?? "N/A"}</strong>
                    </div>

                    <div>
                      <span>Assurance score</span>
                      <strong>{result.assurance_score ?? "N/A"}/100</strong>
                    </div>

                    <div>
                      <span>Hallucination risk</span>
                      <strong>{result.hallucination_risk ?? "N/A"}</strong>
                    </div>

                    <div>
                      <span>Question-source relevance</span>
                      <strong>{result.relevance_score ?? "N/A"}/35</strong>
                    </div>

                    <div>
                      <span>Answer grounding</span>
                      <strong>{result.grounding_score ?? "N/A"}/35</strong>
                    </div>

                    <div>
                      <span>Source availability</span>
                      <strong>{result.source_score ?? "N/A"}/15</strong>
                    </div>

                    <div>
                      <span>Guardrail compliance</span>
                      <strong>{result.guardrail_score ?? "N/A"}/15</strong>
                    </div>

                    <div>
                      <span>Question-source similarity</span>
                      <strong>
                        {result.question_source_similarity ?? "N/A"}
                      </strong>
                    </div>

                    <div>
                      <span>Answer grounding similarity</span>
                      <strong>
                        {result.grounding_similarity ?? "N/A"}
                      </strong>
                    </div>

                    <div className="detail-wide">
                      <span>Routing reason</span>
                      <strong>{result.routing_reason ?? "N/A"}</strong>
                    </div>

                    <div className="detail-wide">
                      <span>Confidence basis</span>
                      <strong>{result.confidence_reason ?? "N/A"}</strong>
                    </div>

                    <div className="detail-wide">
                      <span>Assurance basis</span>
                      <strong>
                        {result.assurance_reason ??
                          "This score is system-derived, not model self-confidence."}
                      </strong>
                    </div>
                  </div>
                </details>

                <div className="feedback-section">
                  {!feedbackStatus ? (
                    <>
                      <div className="feedback-copy">
                        <strong>Was this explanation useful?</strong>
                        <span>
                          Your feedback helps improve response quality.
                        </span>
                      </div>

                      <div className="feedback-actions">
                        <button
                          className="feedback-button helpful"
                          disabled={feedbackLoading}
                          onClick={() =>
                            submitFeedback("helpful")
                          }
                        >
                          👍 Helpful
                        </button>

                        <button
                          className="feedback-button not-helpful"
                          disabled={feedbackLoading}
                          onClick={() =>
                            submitFeedback("not_helpful")
                          }
                        >
                          👎 Not helpful
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="feedback-recorded">
                      <span>✓</span>
                      <div>
                        <strong>Feedback recorded</strong>
                        <small>{feedbackStatus}</small>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            </div>
          )}
        </section>
      </main>

      <div className="composer-dock">
        <div className="composer-shell">
          <div className="composer-icon">✦</div>

          <input
            value={question}
            placeholder="Ask a Business Statistics question..."
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter" && !loading) {
                askQuestion();
              }
            }}
            aria-label="Ask your Business Statistics question"
          />

          <button
            className="send-button"
            onClick={() => askQuestion()}
            disabled={loading}
            aria-label="Send question"
          >
            {loading ? "…" : "↑"}
          </button>
        </div>

        <p className="composer-note">
          Grounded in the approved Business Statistics knowledge base
        </p>
      </div>
    </div>
  );
}

export default App;
