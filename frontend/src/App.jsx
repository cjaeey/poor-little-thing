import { useState } from "react";
import Quiz from "./components/Quiz.jsx";
import Routine from "./components/Routine.jsx";
import ShelfChecker from "./components/ShelfChecker.jsx";
import { getRecommendation } from "./api.js";

export default function App() {
  const [tab, setTab] = useState("routine");
  const [routine, setRoutine] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleQuizSubmit(quiz) {
    setLoading(true);
    setError("");
    try {
      setRoutine(await getRecommendation(quiz));
    } catch {
      setError("Couldn't reach the server. It may be waking up, so try again in 30 seconds.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="header">
        <h1>Poor Little Thing</h1>
        <p>A skincare routine picked by people with your skin type.</p>
      </header>

      <nav className="tabs">
        <button className={tab === "routine" ? "active" : ""} onClick={() => setTab("routine")}>
          Build my routine
        </button>
        <button className={tab === "shelf" ? "active" : ""} onClick={() => setTab("shelf")}>
          Check my shelf
        </button>
      </nav>

      {tab === "routine" && (
        <>
          {!routine && <Quiz onSubmit={handleQuizSubmit} loading={loading} />}
          {error && <p className="error">{error}</p>}
          {routine && <Routine routine={routine} onRestart={() => setRoutine(null)} />}
        </>
      )}
      {tab === "shelf" && <ShelfChecker />}
    </main>
  );
}