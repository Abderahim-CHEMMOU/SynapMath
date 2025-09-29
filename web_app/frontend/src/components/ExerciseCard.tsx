import { FormEvent, useMemo, useState } from "react";
import type { Exercise } from "../types";

type Props = {
  exercise: Exercise;
  disabled?: boolean;
  onSubmit: (exercise: Exercise, answer: string) => void;
};

export function ExerciseCard({ exercise, disabled = false, onSubmit }: Props) {
  const [response, setResponse] = useState("");
  const hasOptions = useMemo(() => Array.isArray(exercise.options) && exercise.options.length > 0, [exercise.options]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (disabled) return;
    if (!response.trim()) return;
    onSubmit(exercise, response);
    setResponse("");
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>{exercise.prompt}</h3>
      <p className="meta">Compétence : {exercise.skill_id} ({exercise.difficulty})</p>
      {hasOptions ? (
        <div className="options">
          {exercise.options!.map((option) => (
            <label key={option} className={`option ${response === option ? "selected" : ""}`}>
              <input
                type="radio"
                name={`option-${exercise.id}`}
                value={option}
                checked={response === option}
                onChange={() => setResponse(option)}
                disabled={disabled}
              />
              <span>{option}</span>
            </label>
          ))}
        </div>
      ) : (
        <input
          type="text"
          value={response}
          onChange={(event) => setResponse(event.target.value)}
          placeholder="Votre réponse"
          disabled={disabled}
        />
      )}
      <button type="submit" disabled={disabled || !response}>
        Valider
      </button>
    </form>
  );
}
