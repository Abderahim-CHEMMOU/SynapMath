import { FormEvent, useState } from "react";
import type { LoginPayload, RegisterPayload } from "../types";

type AuthPanelProps = {
  onLogin: (payload: LoginPayload) => Promise<void>;
  onRegister: (payload: RegisterPayload) => Promise<void>;
  isLoading: boolean;
  error: string | null;
};

type Mode = "login" | "register";

const initialState = {
  user_id: "",
  name: "",
  password: ""
};

export function AuthPanel({ onLogin, onRegister, isLoading, error }: AuthPanelProps) {
  const [mode, setMode] = useState<Mode>("login");
  const [form, setForm] = useState(initialState);

  const switchMode = () => {
    setForm(initialState);
    setMode((prev) => (prev === "login" ? "register" : "login"));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!form.user_id || !form.password || (mode === "register" && !form.name)) {
      return;
    }
    if (mode === "login") {
      await onLogin({ user_id: form.user_id, password: form.password });
    } else {
      await onRegister({ user_id: form.user_id, name: form.name, password: form.password });
    }
  };

  return (
    <div className="auth-panel">
      <form className="card" onSubmit={handleSubmit}>
        <h2>{mode === "login" ? "Connexion" : "Créer un compte"}</h2>
        <label>
          Identifiant
          <input
            type="text"
            value={form.user_id}
            onChange={(event) => setForm((prev) => ({ ...prev, user_id: event.target.value }))}
            placeholder="student_demo"
            disabled={isLoading}
          />
        </label>
        {mode === "register" && (
          <label>
            Nom affiché
            <input
              type="text"
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              placeholder="Jean Dupont"
              disabled={isLoading}
            />
          </label>
        )}
        <label>
          Mot de passe
          <input
            type="password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            placeholder="••••••"
            disabled={isLoading}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={isLoading}>
          {mode === "login" ? "Se connecter" : "S'inscrire"}
        </button>
        <button
          type="button"
          className="link"
          onClick={switchMode}
          disabled={isLoading}
        >
          {mode === "login" ? "Pas de compte ? Inscription" : "Déjà inscrit ? Connexion"}
        </button>
      </form>
    </div>
  );
}
