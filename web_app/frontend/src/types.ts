export type Difficulty = "easy" | "medium" | "hard";

export type Exercise = {
  id: string;
  skill_id: string;
  skill_external_id?: string | null;
  prompt: string;
  difficulty: Difficulty;
  options?: string[] | null;
  answer?: string | null;
  solution?: string | null;
};

export type Interaction = {
  id: string;
  user_id: string;
  exercise_id: string;
  skill_id: string;
  correct: boolean;
  timestamp: string;
  probability_before?: number | null;
  probability_after?: number | null;
};

export type InteractionPayload = {
  user_id: string;
  exercise_id: string;
  skill_id: string;
  correct: boolean;
  timestamp?: string;
};

export type Recommendation = {
  user_id: string;
  exercise_id: string;
  skill_id: string;
  skill_external_id?: string | null;
  prompt: string;
  options?: string[] | null;
  answer?: string | null;
  probability: number;
  difficulty: Difficulty;
};

export type SkillProgress = {
  skillId: string;
  attempts: number;
  correct: number;
  lastProbAfter: number | null;
  lastTimestamp: number;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type UserProfile = {
  id: string;
  user_id: string;
  name: string;
  level?: string | null;
  created_at: string;
};

export type LoginPayload = {
  user_id: string;
  password: string;
};

export type RegisterPayload = {
  user_id: string;
  name: string;
  password: string;
  level?: string | null;
};
