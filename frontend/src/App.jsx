import { useState } from "react";
import Generator from "./Generator";
import Evaluator from "./Evaluator";
import "./index.css";

export default function App() {
  const [tab, setTab] = useState("generate");
  const [apiKey, setApiKey] = useState("");
  const [keySet, setKeySet] = useState(false);

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">⚙</span>
            <span className="logo-text">AppForge</span>
            <span className="logo-tag">AI App Compiler</span>
          </div>
          {!keySet ? (
            <div className="key-input-row">
              <input
                className="key-input"
                type="password"
                placeholder="Enter Gemini API key..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
              <button className="btn-set-key" onClick={() => setKeySet(true)} disabled={!apiKey}>
                Connect
              </button>
            </div>
          ) : (
            <div className="key-connected">
              <span className="dot-green" /> API Connected
              <button className="btn-reset" onClick={() => { setKeySet(false); setApiKey(""); }}>Change</button>
            </div>
          )}
        </div>
        <nav className="tabs">
          <button className={tab === "generate" ? "tab active" : "tab"} onClick={() => setTab("generate")}>
            ⚡ Generate
          </button>
          <button className={tab === "evaluate" ? "tab active" : "tab"} onClick={() => setTab("evaluate")}>
            📊 Evaluate
          </button>
        </nav>
      </header>

      <main className="main">
        {!keySet ? (
          <div className="no-key-msg">
            <div className="no-key-icon">🔑</div>
            <h2>Enter your Gemini API key above to get started</h2>
            <p>Your key is never stored — it's only used for this session.</p>
          </div>
        ) : tab === "generate" ? (
          <Generator apiKey={apiKey} />
        ) : (
          <Evaluator apiKey={apiKey} />
        )}
      </main>
    </div>
  );
}
