import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchInitialExercises,
  submitInteraction,
  fetchRecommendation,
  fetchHistory,
  getStoredToken,
  setAuthToken,
} from "./services/api";
import { login as loginService, register as registerService, fetchCurrentUser, logout as logoutService } from "./services/auth";
import { ExerciseCard } from "./components/ExerciseCard";
import { ProgressSummary } from "./components/ProgressSummary";
import { AuthPanel } from "./components/AuthPanel";
import type {
  Exercise,
  Interaction,
  InteractionPayload,
  Recommendation,
  LoginPayload,
  RegisterPayload,
  UserProfile,
} from "./types";

function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [tokenChecked, setTokenChecked] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialBundle, setInitialBundle] = useState<Exercise[]>([]);
  const [bundleIndex, setBundleIndex] = useState(0);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [recommendedExercise, setRecommendedExercise] = useState<Exercise | null>(null);
  const [masteryMessage, setMasteryMessage] = useState<string | null>(null);
  const [history, setHistory] = useState<Interaction[]>([]);

  const currentExercise = useMemo(() => {
    if (bundleIndex < initialBundle.length) {
      return initialBundle[bundleIndex] ?? null;
    }
    return recommendedExercise;
  }, [bundleIndex, initialBundle, recommendedExercise]);
  const finishedInitial = bundleIndex >= initialBundle.length && initialBundle.length > 0;

  const userId = user?.user_id;

  const refreshHistory = useCallback(
    async (customUserId?: string) => {
      const target = customUserId ?? userId;
      if (!target) return;
      try {
        const entries = await fetchHistory(target);
        setHistory(entries);
      } catch (err) {
        console.warn(err);
      }
    },
    [userId]
  );

  const loadInitialBundle = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchInitialExercises();
      setInitialBundle(data);
      setBundleIndex(0);
      setRecommendation(null);
      setRecommendedExercise(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible de charger les exercices initiaux");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setTokenChecked(true);
      return;
    }
    setAuthLoading(true);
    fetchCurrentUser()
      .then((profile) => {
        setUser(profile);
      })
      .catch(() => {
        setAuthToken(null);
        setAuthError("Session expirée, veuillez vous reconnecter.");
      })
      .finally(() => {
        setAuthLoading(false);
        setTokenChecked(true);
      });
  }, []);

  useEffect(() => {
    if (!userId) {
      setInitialBundle([]);
      setBundleIndex(0);
      setRecommendation(null);
      setRecommendedExercise(null);
      setHistory([]);
      return;
    }
    void (async () => {
      await loadInitialBundle();
      await refreshHistory(userId);
    })();
  }, [userId, loadInitialBundle, refreshHistory]);

  const handleLogin = async (payload: LoginPayload) => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      await loginService(payload);
      const profile = await fetchCurrentUser();
      setUser(profile);
      await refreshHistory(profile.user_id);
      setMasteryMessage(null);
    } catch (err) {
      setAuthToken(null);
      setAuthError(err instanceof Error ? err.message : "Connexion impossible");
    } finally {
      setAuthLoading(false);
      setTokenChecked(true);
    }
  };

  const handleRegister = async (payload: RegisterPayload) => {
    setAuthLoading(true);
    setAuthError(null);
    try {
      await registerService(payload);
      await handleLogin({ user_id: payload.user_id, password: payload.password });
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : "Inscription impossible");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logoutService();
    } catch (err) {
      console.warn(err);
    }
    setUser(null);
    setInitialBundle([]);
    setBundleIndex(0);
    setRecommendation(null);
    setRecommendedExercise(null);
    setHistory([]);
    setMasteryMessage(null);
    setAuthError(null);
    setTokenChecked(true);
  };

  const handleAnswer = async (exercise: Exercise, givenAnswer: string) => {
    if (!userId) {
      setError("Veuillez vous connecter");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const isCorrect = exercise.answer ? exercise.answer.trim().toLowerCase() === givenAnswer.trim().toLowerCase() : false;
      const payload: InteractionPayload = {
        user_id: userId,
        exercise_id: exercise.id,
        skill_id: exercise.skill_id,
        correct: isCorrect,
        timestamp: new Date().toISOString()
      };
      await submitInteraction(payload);
      await refreshHistory(userId);
      setMasteryMessage(null);

      if (bundleIndex + 1 < initialBundle.length) {
        setBundleIndex((index) => index + 1);
      } else {
        setBundleIndex(initialBundle.length);
        const reco = await fetchRecommendation(userId);
        setRecommendation(reco);
        if (reco.mastery && !reco.exercise_id) {
          setRecommendedExercise(null);
          setMasteryMessage(reco.prompt || `Compétence ${reco.skill_id} validée, bravo !`);
        } else {
          setRecommendedExercise({
            id: reco.exercise_id,
            skill_id: reco.skill_id,
            skill_external_id: reco.skill_external_id ?? null,
            prompt: reco.prompt,
            difficulty: reco.difficulty,
            options: reco.options ?? undefined,
            answer: reco.answer ?? null,
            solution: null,
          });
          setMasteryMessage(reco.mastery ? `Compétence ${reco.skill_id} validée, bravo !` : null);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'enregistrement de la réponse");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadRecommendation = async () => {
    if (!userId) return;
    setIsLoading(true);
    setError(null);
    try {
      const reco = await fetchRecommendation(userId);
      setRecommendation(reco);
      if (reco.mastery && !reco.exercise_id) {
        setRecommendedExercise(null);
        setMasteryMessage(reco.prompt || `Compétence ${reco.skill_id} validée, bravo !`);
      } else {
        setRecommendedExercise({
          id: reco.exercise_id,
          skill_id: reco.skill_id,
          skill_external_id: reco.skill_external_id ?? null,
          prompt: reco.prompt,
          difficulty: reco.difficulty,
          options: reco.options ?? undefined,
          answer: reco.answer ?? null,
          solution: null,
        });
        setMasteryMessage(reco.mastery ? `Compétence ${reco.skill_id} validée, bravo !` : null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Aucune recommandation disponible");
    } finally {
      setIsLoading(false);
    }
  };

  if (!tokenChecked || authLoading) {
    return (
      <div className="layout">
        <p>Chargement…</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="layout">
        <AuthPanel
          onLogin={handleLogin}
          onRegister={handleRegister}
          isLoading={authLoading}
          error={authError}
        />
      </div>
    );
  }

  return (
    <div className="layout">
      <header>
        <h1>Adaptive Learning Demo</h1>
        <div className="user-info">
          <div>
            <strong>{user.name}</strong>
            <span> ({user.user_id})</span>
          </div>
          <button className="link" onClick={handleLogout}>
            Se déconnecter
          </button>
        </div>
      </header>

      {authError && <p className="error">{authError}</p>}
      {error && <p className="error">{error}</p>}

      {masteryMessage && (
        <section className="mastery-message">
          <div className="card success">
            <strong>{masteryMessage}</strong>
          </div>
        </section>
      )}

      <main>
        {isLoading && <p>Chargement…</p>}

        {!isLoading && currentExercise && (
          <section>
            {bundleIndex < initialBundle.length ? (
              <h2>Exercice de calibration {bundleIndex + 1} / {initialBundle.length}</h2>
            ) : (
              <h2>Entraînement sur la compétence {currentExercise.skill_id}</h2>
            )}
            <ExerciseCard
              key={currentExercise.id}
              exercise={currentExercise}
              onSubmit={handleAnswer}
              disabled={isLoading}
            />
          </section>
        )}

        {!isLoading && finishedInitial && recommendation && (
          <section className="recommendation">
            <h2>Recommandation</h2>
            <div className="card">
              <h3>{recommendation.exercise_id}</h3>
              <p>Compétence : {recommendation.skill_id}</p>
              <p>Difficulté : {recommendation.difficulty}</p>
              <p>Probabilité de réussite estimée : {(recommendation.probability * 100).toFixed(1)}%</p>
              <button onClick={handleLoadRecommendation}>Mettre à jour</button>
            </div>
          </section>
        )}

        <section className="history">
          <h2>Historique récent</h2>
          {history.length === 0 ? (
            <p>Aucune interaction enregistrée.</p>
          ) : (
            <ul>
              {history.slice(-10).reverse().map((item, index) => (
                <li key={`${item.exercise_id}-${index}`}>
                  <span>{new Date(item.timestamp ?? Date.now()).toLocaleString()}</span>
                  <span> | {item.exercise_id}</span>
                  <span> | {item.correct ? "✔️" : "❌"}</span>
                  {item.probability_before !== null && item.probability_before !== undefined && (
                    <span> | p(t)={(item.probability_before * 100).toFixed(1)}%</span>
                  )}
                  {item.probability_after !== null && item.probability_after !== undefined && (
                    <span> → {(item.probability_after * 100).toFixed(1)}%</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="progress">
          <h2>Progression par compétence</h2>
          <ProgressSummary history={history} />
        </section>
      </main>
    </div>
  );
}

export default App;
