import { Link, useLocation } from "react-router-dom";
import type { ProgressSummary, TopicSummary, User, UserLevel } from "../types";
import { USER_LEVEL_LABELS } from "../types";

interface SidebarProps {
  topics: TopicSummary[];
  progress: ProgressSummary | null;
  user: User | null;
  menuOpen: boolean;
  onToggleMenu: () => void;
  onLevelChange: (level: UserLevel) => void;
  loadingLevel: boolean;
  onLogout: () => void;
}

export function Sidebar({
  topics,
  progress,
  user,
  menuOpen,
  onToggleMenu,
  onLevelChange,
  loadingLevel,
  onLogout,
}: SidebarProps) {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand">Python Refresh</div>
        <button type="button" className="menu-toggle secondary" onClick={onToggleMenu}>
          {menuOpen ? "Скрыть" : "Темы"}
        </button>
      </div>

      <label htmlFor="level-select">Уровень</label>
      <select
        id="level-select"
        className="level-select"
        value={user?.level ?? "beginner"}
        disabled={loadingLevel || !user}
        onChange={(event) => onLevelChange(event.target.value as UserLevel)}
      >
        {(Object.keys(USER_LEVEL_LABELS) as UserLevel[]).map((level) => (
          <option key={level} value={level}>
            {USER_LEVEL_LABELS[level]}
          </option>
        ))}
      </select>

      <button type="button" className="secondary logout-button" onClick={onLogout}>
        Выйти
      </button>

      {progress && (
        <div className="progress-card">
          <div>Общий прогресс: {progress.percent}%</div>
          <div className="muted">
            {progress.solved_count} / {progress.total_available} заданий по всем темам
          </div>
          <div className="progress-bar">
            <span style={{ width: `${progress.percent}%` }} />
          </div>
        </div>
      )}

      <ul className={`topic-list ${menuOpen ? "" : "collapsed"}`}>
        {topics.map((topic) => {
          const active = location.pathname.startsWith(`/topics/${topic.slug}`);
          return (
            <li key={topic.id}>
              <Link
                to={topic.available ? `/topics/${topic.slug}` : "#"}
                className={`topic-link ${active ? "active" : ""} ${topic.available ? "" : "disabled"}`}
              >
                <div>{topic.title}</div>
                <div className="topic-meta">
                  {!topic.available
                    ? "Недоступно на вашем уровне"
                    : topic.exercise_count === 0
                      ? "Заданий пока нет"
                      : `${topic.solved_count}/${topic.exercise_count} решено`}
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
