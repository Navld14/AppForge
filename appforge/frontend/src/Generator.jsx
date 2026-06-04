import { useState } from "react";

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const EXAMPLE_PROMPTS = [
  "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
  "Create an e-commerce platform with product listings, shopping cart, Stripe checkout, and seller dashboard.",
  "Build a project management tool with boards, cards, teams, deadlines, and notifications.",
];

const STAGE_LABELS = {
  intent: { label: "Stage 1: Intent Extraction", icon: "🧠" },
  architecture: { label: "Stage 2: System Design", icon: "🏗" },
  schemas: { label: "Stage 3: Schema Generation", icon: "📐" },
  refined_output: { label: "Stage 4: Refined Output", icon: "✅" },
};

export default function Generator({ apiKey }) {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeStage, setActiveStage] = useState("refined_output");
  const [loadingStage, setLoadingStage] = useState(0);

  const stages = ["Extracting intent...", "Designing architecture...", "Generating schemas...", "Refining & validating..."];

  async function handleGenerate() {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setLoadingStage(0);

    const interval = setInterval(() => {
      setLoadingStage((s) => Math.min(s + 1, 3));
    }, 4000);

    try {
      const res = await fetch(`${BACKEND}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, api_key: apiKey }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Generation failed");
      setResult(data);
      setActiveStage("refined_output");
    } catch (e) {
      setError(e.message);
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  }

  return (
    <div className="generator">
      <div className="prompt-section">
        <h2 className="section-title">Describe your application</h2>
        <div className="examples-row">
          {EXAMPLE_PROMPTS.map((p, i) => (
            <button key={i} className="example-chip" onClick={() => setPrompt(p)}>
              {p.slice(0, 45)}...
            </button>
          ))}
        </div>
        <textarea
          className="prompt-textarea"
          placeholder="e.g. Build a CRM with login, contacts, role-based access, and payment plans..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
        />
        <div className="prompt-footer">
          <span className="char-count">{prompt.length} chars</span>
          <button className="btn-generate" onClick={handleGenerate} disabled={loading || !prompt.trim()}>
            {loading ? "Compiling..." : "⚡ Compile App →"}
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading-section">
          <div className="pipeline-stages">
            {stages.map((s, i) => (
              <div key={i} className={`pipeline-step ${i <= loadingStage ? "active" : ""} ${i < loadingStage ? "done" : ""}`}>
                <div className="step-dot">{i < loadingStage ? "✓" : i + 1}</div>
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <div className="error-box">❌ {error}</div>}

      {result && (
        <div className="result-section">
          <div className="result-meta">
            <div className="meta-card">
              <span className="meta-label">Latency</span>
              <span className="meta-val">{result.latency_seconds}s</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">Retries</span>
              <span className="meta-val">{result.retries_used}</span>
            </div>
            <div className={`meta-card ${result.validation?.is_valid ? "valid" : "warn"}`}>
              <span className="meta-label">Validation</span>
              <span className="meta-val">{result.validation?.is_valid ? "✅ Passed" : "⚠ Issues"}</span>
            </div>
          </div>

          {result.validation?.issues?.length > 0 && (
            <div className="validation-issues">
              <strong>Validation issues:</strong>
              <ul>{result.validation.issues.map((i, idx) => <li key={idx}>{i}</li>)}</ul>
            </div>
          )}

          {result.validation?.passed?.length > 0 && (
            <div className="validation-passed">
              {result.validation.passed.map((p, idx) => <span key={idx} className="pass-tag">✓ {p}</span>)}
            </div>
          )}

          <div className="stage-tabs">
            {Object.entries(STAGE_LABELS).map(([key, val]) => (
              <button
                key={key}
                className={activeStage === key ? "stage-tab active" : "stage-tab"}
                onClick={() => setActiveStage(key)}
              >
                {val.icon} {val.label}
              </button>
            ))}
          </div>

          <div className="json-output">
            <div className="json-header">
              <span>{STAGE_LABELS[activeStage]?.label}</span>
              <button className="btn-copy" onClick={() => navigator.clipboard.writeText(JSON.stringify(result.stages?.[activeStage] || result.final_output, null, 2))}>
                Copy JSON
              </button>
            </div>
            <pre className="json-pre">
              {JSON.stringify(
                activeStage === "refined_output" ? result.final_output : result.stages?.[activeStage],
                null, 2
              )}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
