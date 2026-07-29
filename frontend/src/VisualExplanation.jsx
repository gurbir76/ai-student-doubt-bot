import { useMemo } from "react";

function NormalCurve({ showTail = false }) {
  const points = useMemo(() => {
    const values = [];
    for (let i = 0; i <= 80; i += 1) {
      const x = -4 + (i / 80) * 8;
      const y = Math.exp(-0.5 * x * x);
      const px = 20 + (i / 80) * 360;
      const py = 150 - y * 115;
      values.push(`${px},${py}`);
    }
    return values.join(" ");
  }, []);

  return (
    <svg
      className="visual-svg"
      viewBox="0 0 400 180"
      role="img"
      aria-label={
        showTail
          ? "Normal distribution with right tail shaded"
          : "Normal distribution bell curve"
      }
    >
      <line x1="20" y1="150" x2="380" y2="150" className="visual-axis" />
      <polyline points={points} className="visual-line" />

      {showTail && (
        <>
          <line x1="278" y1="150" x2="278" y2="85" className="visual-dashed" />
          <path
            d="M278 150 L278 85 C310 100, 345 130, 380 149 L380 150 Z"
            className="visual-tail"
          />
          <text x="302" y="128" className="visual-label">p-value</text>
        </>
      )}

      {!showTail && (
        <>
          <line x1="200" y1="150" x2="200" y2="35" className="visual-dashed" />
          <line x1="155" y1="150" x2="155" y2="65" className="visual-dotted" />
          <line x1="245" y1="150" x2="245" y2="65" className="visual-dotted" />
          <text x="186" y="166" className="visual-label">Mean</text>
          <text x="128" y="166" className="visual-label">-1 SD</text>
          <text x="231" y="166" className="visual-label">+1 SD</text>
        </>
      )}
    </svg>
  );
}

function RegressionVisual() {
  const points = [
    [65, 130],
    [125, 110],
    [185, 89],
    [245, 68],
    [305, 47],
  ];

  return (
    <svg className="visual-svg" viewBox="0 0 400 180" role="img" aria-label="Simple linear regression">
      <line x1="35" y1="150" x2="375" y2="150" className="visual-axis" />
      <line x1="35" y1="150" x2="35" y2="20" className="visual-axis" />
      <line x1="55" y1="138" x2="325" y2="42" className="visual-line" />

      {points.map(([x, y], index) => (
        <circle key={index} cx={x} cy={y} r="6" className="visual-point" />
      ))}

      <text x="278" y="35" className="visual-label">Y = a + bX</text>
      <text x="332" y="168" className="visual-label">X</text>
      <text x="15" y="28" className="visual-label">Y</text>
    </svg>
  );
}

function StandardDeviationVisual() {
  return (
    <svg className="visual-svg" viewBox="0 0 400 180" role="img" aria-label="Low versus high standard deviation">
      <line x1="35" y1="150" x2="375" y2="150" className="visual-axis" />

      <text x="25" y="62" className="visual-label">Low spread</text>
      <text x="25" y="122" className="visual-label">High spread</text>

      {[175, 188, 200, 212, 225].map((x) => (
        <circle key={`low-${x}`} cx={x} cy="58" r="6" className="visual-point" />
      ))}

      {[95, 145, 200, 255, 305].map((x) => (
        <circle key={`high-${x}`} cx={x} cy="118" r="6" className="visual-point secondary" />
      ))}
    </svg>
  );
}

function ProbabilityVisual() {
  return (
    <div className="probability-visual">
      <div className="probability-table">
        <div className="probability-row header">
          <span>Group</span>
          <span>Students</span>
        </div>
        <div className="probability-row">
          <span>Total students</span>
          <strong>100</strong>
        </div>
        <div className="probability-row">
          <span>Studied regularly</span>
          <strong>40</strong>
        </div>
        <div className="probability-row accent">
          <span>Studied & passed</span>
          <strong>30</strong>
        </div>
      </div>

      <div className="probability-formula">
        <span>P(Passed | Studied)</span>
        <strong>30 / 40 = 0.75</strong>
      </div>
    </div>
  );
}

function CentralTendencyVisual() {
  return (
    <svg className="visual-svg" viewBox="0 0 400 180" role="img" aria-label="Mean median and mode on a number line">
      <line x1="40" y1="120" x2="360" y2="120" className="visual-axis" />

      {[90, 130, 130, 170, 300].map((x, index) => (
        <circle key={index} cx={x} cy="120" r="6" className="visual-point" />
      ))}

      <line x1="165" y1="35" x2="165" y2="135" className="visual-dashed" />
      <line x1="130" y1="55" x2="130" y2="135" className="visual-dotted" />
      <line x1="130" y1="80" x2="130" y2="135" className="visual-mode-line" />

      <text x="145" y="28" className="visual-label">Mean</text>
      <text x="95" y="50" className="visual-label">Median</text>
      <text x="98" y="76" className="visual-label">Mode</text>
      <text x="72" y="143" className="visual-label">2</text>
      <text x="123" y="143" className="visual-label">3</text>
      <text x="163" y="143" className="visual-label">4</text>
      <text x="294" y="143" className="visual-label">8</text>
    </svg>
  );
}

const VISUALS = {
  regression: {
    title: "Simple Linear Regression",
    explanation:
      "The slope shows how much Y changes when X increases by one unit. A steeper line means a larger change in Y for each increase in X.",
    render: <RegressionVisual />,
  },
  p_value: {
    title: "p-value as Tail Area",
    explanation:
      "The shaded tail represents the p-value. A smaller shaded area means the observed result is less likely under the null hypothesis.",
    render: <NormalCurve showTail />,
  },
  normal_distribution: {
    title: "Normal Distribution",
    explanation:
      "Values are concentrated around the mean. The curve is symmetric, and standard deviation describes how widely values spread around the center.",
    render: <NormalCurve />,
  },
  standard_deviation: {
    title: "Low vs High Standard Deviation",
    explanation:
      "Closely packed values have a low standard deviation. Values spread farther from the mean have a higher standard deviation.",
    render: <StandardDeviationVisual />,
  },
  probability: {
    title: "Conditional Probability",
    explanation:
      "Conditional probability narrows attention to the group where the condition has already happened. Here, we look only at students who studied regularly.",
    render: <ProbabilityVisual />,
  },
  central_tendency: {
    title: "Mean, Median and Mode",
    explanation:
      "Mean is the average, median is the middle value, and mode is the value that occurs most often.",
    render: <CentralTendencyVisual />,
  },
};

function VisualExplanation({ visualType }) {
  const visual = VISUALS[visualType];

  if (!visual) {
    return null;
  }

  return (
    <details className="visual-explanation">
      <summary>
        <span className="visual-summary-icon">◫</span>
        <span>
          <strong>Show visual explanation</strong>
          <small>Optional topic visual</small>
        </span>
      </summary>

      <div className="visual-content">
        <div className="visual-content-header">
          <span className="eyebrow">Visual explanation</span>
          <h3>{visual.title}</h3>
        </div>

        <div className="visual-stage">
          {visual.render}
        </div>

        <div className="visual-insight">
          <span>✦</span>
          <p>{visual.explanation}</p>
        </div>
      </div>
    </details>
  );
}

export default VisualExplanation;
