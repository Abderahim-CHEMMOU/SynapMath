import axios from "axios";
import type { Exercise, Interaction, InteractionPayload, Recommendation } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"
});

let authToken: string | null = null;

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

export function setAuthToken(token: string | null): void {
  authToken = token;
  if (typeof window !== "undefined") {
    if (token) {
      window.localStorage.setItem("auth_token", token);
    } else {
      window.localStorage.removeItem("auth_token");
    }
  }
}

export function getStoredToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== "undefined") {
    const stored = window.localStorage.getItem("auth_token");
    authToken = stored;
    return stored;
  }
  return null;
}

type ExerciseResponse = Exercise[];

export async function fetchInitialExercises(): Promise<ExerciseResponse> {
  const { data } = await api.get<ExerciseResponse>("/exercises/initial");
  return data;
}

export async function submitInteraction(payload: InteractionPayload): Promise<Interaction> {
  const { data } = await api.post<Interaction>("/interactions/", payload);
  return data;
}

export async function fetchRecommendation(userId: string): Promise<Recommendation> {
  const { data } = await api.get<Recommendation>("/recommendations/next", { params: { user_id: userId } });
  return data;
}

export async function fetchHistory(userId: string): Promise<Interaction[]> {
  const { data } = await api.get<Interaction[]>(`/students/${userId}/history`);
  return data;
}

export default api;
