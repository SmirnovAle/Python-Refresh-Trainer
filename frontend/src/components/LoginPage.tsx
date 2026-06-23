import { FormEvent, useEffect, useState } from "react";
import { getAuthConfig, login, register } from "../api";

interface LoginPageProps {
  onSuccess: () => void;
}

type AuthMode = "login" | "register";

export function LoginPage({ onSuccess }: LoginPageProps) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [registrationEnabled, setRegistrationEnabled] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAuthConfig()
      .then((config) => setRegistrationEnabled(config.registration_enabled))
      .catch(() => setRegistrationEnabled(false));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "register") {
        await register(name.trim(), email.trim(), password);
      } else {
        await login(email.trim(), password);
      }
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось выполнить запрос");
    } finally {
      setLoading(false);
    }
  }

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode);
    setError(null);
  }

  const isRegister = mode === "register";

  return (
    <div className="login-shell">
      <form className="login-card card" onSubmit={handleSubmit}>
        <h1 className="page-title">Python Refresh Trainer</h1>
        <p className="page-subtitle">
          {isRegister ? "Создайте аккаунт для тренировки" : "Войдите, чтобы продолжить тренировку"}
        </p>

        {isRegister && (
          <>
            <label htmlFor="register-name">Имя</label>
            <input
              id="register-name"
              className="text-input"
              type="text"
              autoComplete="name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              minLength={2}
              required
            />
          </>
        )}

        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          className="text-input"
          type="email"
          autoComplete={isRegister ? "email" : "username"}
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="login-password">Пароль</label>
        <input
          id="login-password"
          className="text-input"
          type="password"
          autoComplete={isRegister ? "new-password" : "current-password"}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          minLength={isRegister ? 8 : 1}
          required
        />
        {isRegister && <p className="muted login-hint">Минимум 8 символов</p>}

        {error && <div className="error-box">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? (isRegister ? "Регистрация..." : "Вход...") : isRegister ? "Зарегистрироваться" : "Войти"}
        </button>

        {registrationEnabled && (
          <button
            type="button"
            className="login-switch"
            onClick={() => switchMode(isRegister ? "login" : "register")}
          >
            {isRegister ? "Уже есть аккаунт? Войти" : "Нет аккаунта? Зарегистрироваться"}
          </button>
        )}
      </form>
    </div>
  );
}
