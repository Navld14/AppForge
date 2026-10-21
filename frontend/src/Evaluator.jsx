import { useState } from "react";

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export default function Evaluator({ apiKey }) {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  async function runEval() {
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const res = await fetch(`${BACKEND}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Evaluation failed");
      setResults(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const typeColors = {
    real: "#4ade80",
    edge_vague: "#facc15",
    edge_conflicting: "#f87171",
    edge_incomplete: "#fb923c",
  };

  return (
    <div className="evaluator">
      <div className="eval-header">
        <h2>Evaluation Framework</h2>
        <p>Tests 5 prompts (mix of real + edge cases) and reports metrics. Full 20-prompt dataset in code.</p>
        <button className="btn-generate" onClick={runEval} disabled={loading}>
          {loading ? "Running evaluation... (~2 min)" : "▶ Run Evaluation"}
        </button>
      </div>

      {loading && (
        <div className="eval-loading">
          <div className="spinner" />
          <p>Running pipeline on test prompts... this takes ~2 minutes</p>
        </div>
      )}

      {error && <div className="error-box">❌ {error}</div>}

      {results && (
        <div className="eval-results">
          <div className="summary-grid">
            <div className="summary-card">
              <div className="summary-num">{results.summary.success_rate}</div>
              <div className="summary-label">Success Rate</div>
            </div>
            <div className="summary-card">
              <div className="summary-num">{results.summary.avg_latency_seconds}s</div>
              <div className="summary-label">Avg Latency</div>
            </div>
            <div className="summary-card">
              <div className="summary-num">{results.summary.avg_retries_per_request}</div>
              <div className="summary-label">Avg Retries</div>
            </div>
            <div className="summary-card">
              <div className="summary-num">{results.summary.total_tested}</div>
              <div className="summary-label">Prompts Tested</div>
            </div>
          </div>

          <div className="results-table">
            <div className="table-header">
              <span>#</span>
              <span>Type</span>
              <span>Prompt</span>
              <span>Status</span>
              <span>Retries</span>
              <span>Latency</span>
            </div>
            {results.per_prompt_results.map((r) => (
              <div key={r.id} className="table-row">
                <span>{r.id}</span>
                <span>
                  <span className="type-badge" style={{ background: typeColors[r.type] + "33", color: typeColors[r.type] }}>
                    {r.type.replace("edge_", "")}
                  </span>
                </span>
                <span className="prompt-cell" title={r.prompt_preview}>{r.prompt_preview}</span>
                <span>{r.success ? "✅" : "❌"}</span>
                <span>{r.retries}</span>
                <span>{r.latency_seconds}s</span>
              </div>
            ))}
          </div>

          {Object.keys(results.summary.failure_types).length > 0 && (
            <div className="failure-types">
              <strong>Failure types:</strong>
              {Object.entries(results.summary.failure_types).map(([k, v]) => (
                <span key={k} className="failure-badge">{k}: {v}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
