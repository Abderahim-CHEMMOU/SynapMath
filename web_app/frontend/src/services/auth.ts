import api, { setAuthToken } from "./api";
import type {
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  UserProfile,
} from "../types";

export async function register(payload: RegisterPayload): Promise<UserProfile> {
  const { data } = await api.post<UserProfile>("/auth/register", payload);
  return data;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", payload);
  setAuthToken(data.access_token);
  return data;
}

export async function fetchCurrentUser(): Promise<UserProfile> {
  const { data } = await api.get<UserProfile>("/auth/me");
  return data;
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } finally {
    setAuthToken(null);
  }
}
