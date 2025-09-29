import { useMemo } from "react";
import type { Interaction, SkillProgress } from "../types";

type Props = {
  history: Interaction[];
};

const masteryLabel = (prob: number | null): string => {
  if (prob === null) return "-";
  if (prob > 0.7) return "Maîtrisé";
  if (prob >= 0.4) return "En progression";
  return "À renforcer";
};

export function ProgressSummary({ history }: Props) {
  const summaries = useMemo<SkillProgress[]>(() => {
    if (!history.length) return [];

    const map = new Map<string, SkillProgress>();

    history.forEach((item) => {
      const current = map.get(item.skill_id) ?? {
        skillId: item.skill_id,
        attempts: 0,
        correct: 0,
        lastProbAfter: null,
        lastTimestamp: 0,
      };
      current.attempts += 1;
      if (item.correct) current.correct += 1;

      const ts = new Date(item.timestamp ?? Date.now()).getTime();
      if (item.probability_after !== null && item.probability_after !== undefined) {
        if (ts >= current.lastTimestamp) {
          current.lastProbAfter = item.probability_after;
          current.lastTimestamp = ts;
        }
      }

      map.set(item.skill_id, current);
    });

    return Array.from(map.values()).sort((a, b) => (b.lastProbAfter ?? 0) - (a.lastProbAfter ?? 0));
  }, [history]);

  if (!summaries.length) {
    return <p>Aucune donnée disponible.</p>;
  }

  return (
    <table className="progress-table">
      <thead>
        <tr>
          <th>Compétence</th>
          <th>Essais</th>
          <th>Taux de réussite</th>
          <th>Probabilité (t)</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {summaries.map((item) => {
          const successRate = item.attempts ? (item.correct / item.attempts) * 100 : 0;
          const prob = item.lastProbAfter !== null && item.lastProbAfter !== undefined
            ? `${(item.lastProbAfter * 100).toFixed(1)}%`
            : "-";
          return (
            <tr key={item.skillId}>
              <td>{item.skillId}</td>
              <td>{item.attempts}</td>
              <td>{successRate.toFixed(1)}%</td>
              <td>{prob}</td>
              <td>{masteryLabel(item.lastProbAfter)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
