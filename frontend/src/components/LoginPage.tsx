import { FormEvent, useState } from "react";
import { login } from "../api";

interface LoginPageProps {
  onSuccess: () => void;
}

export function LoginPage({ onSuccess }: LoginPageProps) {
  const [email, setEmail] = useState("admin@local");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email.trim(), password);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось войти");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-shell">
      <form className="login-card card" onSubmit={handleSubmit}>
        <h1 className="page-title">Python Refresh Trainer</h1>
        <p className="page-subtitle">Войдите, чтобы продолжить тренировку</p>

        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          className="text-input"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="login-password">Пароль</label>
        <input
          id="login-password"
          className="text-input"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        {error && <div className="error-box">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Вход..." : "Войти"}
        </button>
      </form>
    </div>
  );
}
