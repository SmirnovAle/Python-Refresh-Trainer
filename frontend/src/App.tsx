import { useEffect, useState, type KeyboardEvent } from "react";
import { Link, Route, Routes, useNavigate, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import {
  explainError,
  getAiStatus,
  getCurrentUser,
  getExercise,
  getHint,
  getProgressSummary,
  getSolution,
  getTopic,
  getTopics,
  logout,
  submitExercise,
  updateUserLevel,
} from "./api";
import { LoginPage } from "./components/LoginPage";
import { Sidebar } from "./components/Sidebar";
import { clearDraft, resolveInitialCode, writeDraft } from "./draftStorage";
import type {
  ExerciseDetail,
  ProgressSummary,
  SubmitCodeResponse,
  TopicDetail,
  TopicSummary,
  User,
  UserLevel,
} from "./types";
import { DIFFICULTY_LABELS } from "./types";

function HomePage({ topics }: { topics: TopicSummary[] }) {
  const available = topics.filter((topic) => topic.available && topic.exercise_count > 0);
  const first = available[0];

  return (
    <div>
      <h1 className="page-title">Python Refresh Trainer</h1>
      <p className="page-subtitle">
        Тренажёр для повторения встроенных возможностей Python. Выберите тему слева или начните с первой
        доступной.
      </p>
      {first ? (
        <div className="card">
          <Link to={`/topics/${first.slug}`} style={{ color: "var(--accent)" }}>
            Начать с темы «{first.title}»
          </Link>
        </div>
      ) : (
        <div className="empty-state">Нет доступных тем для текущего уровня.</div>
      )}
    </div>
  );
}

function TopicPage({ slug, onProgressChange }: { slug: string; onProgressChange: () => void }) {
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    getTopic(slug)
      .then((data) => {
        if (!cancelled) setTopic(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    onProgressChange();
    return () => {
      cancelled = true;
    };
  }, [slug, onProgressChange]);

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  if (!topic) {
    return <div className="empty-state">Загрузка темы...</div>;
  }

  return (
    <div>
      <h1 className="page-title">{topic.title}</h1>
      <div className="card markdown-body">
        <ReactMarkdown>{topic.theory_md}</ReactMarkdown>
      </div>

      <div className="card">
        <h2>Задания</h2>
        {topic.exercises.length === 0 ? (
          <div className="empty-state">Задания для этой темы скоро появятся.</div>
        ) : (
          <ul className="exercise-list">
            {topic.exercises.map((exercise) => (
              <li key={exercise.id} className="exercise-item">
                <div>
                  <Link to={`/exercises/${exercise.id}`} style={{ color: "var(--accent)" }}>
                    {exercise.title}
                  </Link>
                  <div className="topic-meta">
                    {DIFFICULTY_LABELS[exercise.difficulty]}
                    {exercise.solved ? " · решено" : ""}
                  </div>
                </div>
                {exercise.solved && <span className="badge success">✓</span>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function ExercisePage({
  exerciseId,
  onProgressChange,
}: {
  exerciseId: number;
  onProgressChange: () => void;
}) {
  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [code, setCode] = useState("");
  const [result, setResult] = useState<SubmitCodeResponse | null>(null);
  const [hint, setHint] = useState<string | null>(null);
  const [hintSignature, setHintSignature] = useState<string | null>(null);
  const [solutionVisible, setSolutionVisible] = useState(false);
  const [solutionCode, setSolutionCode] = useState<string | null>(null);
  const [solutionExplanation, setSolutionExplanation] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAvailable, setAiAvailable] = useState(false);
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    setResult(null);
    setHint(null);
    setHintSignature(null);
    setSolutionVisible(false);
    setSolutionCode(null);
    setSolutionExplanation(null);
    setAiExplanation(null);

    getExercise(exerciseId)
      .then((data) => {
        if (!cancelled) {
          setExercise(data);
          setCode(resolveInitialCode(exerciseId, data.last_code, data.starter_code));
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });

    getAiStatus()
      .then((status) => {
        if (!cancelled) setAiAvailable(status.configured);
      })
      .catch(() => {
        if (!cancelled) setAiAvailable(false);
      });

    return () => {
      cancelled = true;
    };
  }, [exerciseId]);

  useEffect(() => {
    if (!exercise) return;
    const timer = window.setTimeout(() => writeDraft(exercise.id, code), 400);
    return () => window.clearTimeout(timer);
  }, [code, exercise]);

  async function handleSubmit() {
    if (!exercise) return;
    setLoading(true);
    setError(null);
    setAiExplanation(null);
    try {
      const response = await submitExercise(exercise.id, code);
      setResult(response);
      if (response.success) {
        clearDraft(exercise.id);
        onProgressChange();
        setExercise({ ...exercise, solved: true });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка проверки");
    } finally {
      setLoading(false);
    }
  }

  async function handleHint() {
    if (!exercise) return;
    try {
      const response = await getHint(exercise.id);
      setHint(response.hint);
      setHintSignature(response.hint_signature || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось получить подсказку");
    }
  }

  async function handleExplain() {
    if (!exercise || !result || result.success) return;
    setAiLoading(true);
    setError(null);
    try {
      const response = await explainError({
        exercise_id: exercise.id,
        code,
        error: result.error,
        stderr: result.stderr || null,
        failed_tests: result.tests.filter((test) => !test.passed).map((test) => test.message),
      });
      setAiExplanation(response.explanation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось получить AI-разбор");
    } finally {
      setAiLoading(false);
    }
  }

  function handleEditorKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      void handleSubmit();
    }
  }

  async function handleSolution() {
    if (!exercise) return;
    try {
      const response = await getSolution(exercise.id);
      setSolutionCode(response.solution);
      setSolutionExplanation(response.explanation);
      setSolutionVisible(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось получить решение");
    }
  }

  if (error && !exercise) {
    return <div className="error-box">{error}</div>;
  }

  if (!exercise) {
    return <div className="empty-state">Загрузка задания...</div>;
  }

  return (
    <div>
      <Link to={`/topics/${exercise.topic_slug}`} className="back-link">
        ← {exercise.topic_title}
      </Link>
      <h1 className="page-title">{exercise.title}</h1>
      <p>{exercise.description}</p>
      <p className="muted">
        Функция: <code>{exercise.function_name}</code> · {DIFFICULTY_LABELS[exercise.difficulty]}
        {exercise.solved ? " · решено" : ""}
      </p>

      <div className={`editors-grid ${solutionVisible ? "with-solution" : ""}`}>
        <div className="editor-pane">
          <div className="editor-label">Ваш код</div>
          <textarea
            className="code-editor"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            onKeyDown={handleEditorKeyDown}
            spellCheck={false}
          />
        </div>

        {solutionVisible && solutionCode && (
          <div className="editor-pane solution-pane">
            <div className="editor-label">Эталонное решение</div>
            <pre className="code-readonly">{solutionCode}</pre>
            {solutionExplanation && (
              <div className="solution-explanation markdown-body">
                <h3>Разбор инструментов</h3>
                <ReactMarkdown>{solutionExplanation}</ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="actions">
        <button type="button" onClick={handleSubmit} disabled={loading}>
          {loading ? "Проверка..." : "Проверить"}
        </button>
        <button type="button" className="secondary" onClick={handleHint}>
          Подсказка
        </button>
        <button type="button" className="secondary" onClick={handleSolution}>
          {solutionVisible ? "Обновить решение" : "Показать решение"}
        </button>
        {solutionVisible && (
          <button
            type="button"
            className="secondary"
            onClick={() => setSolutionVisible(false)}
          >
            Скрыть решение
          </button>
        )}
      </div>

      {hint && (
        <div className="hint-box">
          {hintSignature && (
            <div className="hint-signature">
              <span className="muted">Ключевая конструкция:</span>
              <code>{hintSignature}</code>
            </div>
          )}
          <div>{hint}</div>
        </div>
      )}
      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="card">
          <h2>{result.success ? "Все проверки пройдены" : "Есть ошибки"}</h2>
          <p className="muted">
            Автопроверки вызывают вашу функцию с разными входными данными и сравнивают результат с
            ожидаемым.
          </p>
          {result.error && <div className="error-box">{result.error}</div>}
          {result.stderr && <div className="muted">stderr: {result.stderr}</div>}
          {!result.success && aiAvailable && (
            <div className="actions" style={{ marginTop: "1rem" }}>
              <button type="button" className="secondary" onClick={handleExplain} disabled={aiLoading}>
                {aiLoading ? "AI думает..." : "Объяснить ошибку"}
              </button>
            </div>
          )}
          {aiExplanation && (
            <div className="ai-box markdown-body">
              <h3>AI-разбор</h3>
              <ReactMarkdown>{aiExplanation}</ReactMarkdown>
            </div>
          )}
          <div className="test-results">
            {result.tests.map((test) => (
              <div key={test.index} className={`test-result ${test.passed ? "pass" : "fail"}`}>
                <strong>Проверка {test.index + 1}:</strong>{" "}
                {test.passed ? `пройдена — ${test.message}` : test.message}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const navigate = useNavigate();
  const [topics, setTopics] = useState<TopicSummary[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [progress, setProgress] = useState<ProgressSummary | null>(null);
  const [menuOpen, setMenuOpen] = useState(true);
  const [loadingLevel, setLoadingLevel] = useState(false);
  const [bootError, setBootError] = useState<string | null>(null);
  const [authState, setAuthState] = useState<"loading" | "guest" | "authenticated">("loading");

  async function refreshDashboard() {
    const [topicsData, userData, progressData] = await Promise.all([
      getTopics(),
      getCurrentUser(),
      getProgressSummary(),
    ]);
    setTopics(topicsData);
    setUser(userData);
    setProgress(progressData);
    setAuthState("authenticated");
    setBootError(null);
  }

  useEffect(() => {
    refreshDashboard().catch((err: Error) => {
      if (err.message.includes("Требуется вход") || err.message.includes("Сессия истекла")) {
        setAuthState("guest");
        return;
      }
      setBootError(err.message);
      setAuthState("guest");
    });
  }, []);

  async function handleLogout() {
    try {
      await logout();
    } catch {
      // cookie may already be cleared
    }
    setTopics([]);
    setUser(null);
    setProgress(null);
    setBootError(null);
    setAuthState("guest");
    navigate("/");
  }

  async function handleLevelChange(level: UserLevel) {
    setLoadingLevel(true);
    try {
      const updated = await updateUserLevel(level);
      setUser(updated);
      await refreshDashboard();
      navigate("/");
    } catch (err) {
      setBootError(err instanceof Error ? err.message : "Не удалось сменить уровень");
    } finally {
      setLoadingLevel(false);
    }
  }

  if (authState === "loading") {
    return <div className="empty-state">Загрузка...</div>;
  }

  if (authState === "guest") {
    return <LoginPage onSuccess={() => refreshDashboard().catch((err: Error) => setBootError(err.message))} />;
  }

  if (bootError) {
    return <div className="error-box">{bootError}</div>;
  }

  return (
    <div className="app-shell">
      <Sidebar
        topics={topics}
        progress={progress}
        user={user}
        menuOpen={menuOpen}
        onToggleMenu={() => setMenuOpen((value) => !value)}
        onLevelChange={handleLevelChange}
        loadingLevel={loadingLevel}
        onLogout={handleLogout}
      />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage topics={topics} />} />
          <Route
            path="/topics/:slug"
            element={
              <TopicRoute onProgressChange={() => refreshDashboard().catch(() => undefined)} />
            }
          />
          <Route
            path="/exercises/:id"
            element={
              <ExerciseRoute onProgressChange={() => refreshDashboard().catch(() => undefined)} />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

function TopicRoute({ onProgressChange }: { onProgressChange: () => void }) {
  const { slug = "" } = useParams();
  return <TopicPage slug={slug} onProgressChange={onProgressChange} />;
}

function ExerciseRoute({ onProgressChange }: { onProgressChange: () => void }) {
  const { id = "0" } = useParams();
  return <ExercisePage exerciseId={Number(id)} onProgressChange={onProgressChange} />;
}
