import type {
  GenerationCreateResponse,
  GenerationStatusResponse,
  IdeConfig,
  Profile
} from "../types/ide";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
const DEMO_JWT = import.meta.env.VITE_DEMO_JWT ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string,
    public readonly details?: unknown
  ) {
    super(message);
  }
}

export function getJwtToken(): string {
  return localStorage.getItem("jwt_token") ?? DEMO_JWT;
}

function requireJwtToken(): string {
  const token = getJwtToken().trim();
  if (!token) {
    throw new ApiError("JWT token is required", 401, "auth_token_required");
  }
  return token;
}

function buildHeaders(extra?: Record<string, string>): HeadersInit {
  const token = requireJwtToken();
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
    ...extra
  };
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...buildHeaders(),
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(
      body.message ?? "Request failed",
      response.status,
      body.code ?? "api_error",
      body.details
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function createGeneration(prompt: string, locale: "ru" | "en"): Promise<GenerationCreateResponse> {
  return fetchJson<GenerationCreateResponse>("/generations", {
    method: "POST",
    body: JSON.stringify({ prompt, locale })
  });
}

export async function getGeneration(generationId: string): Promise<GenerationStatusResponse> {
  return fetchJson<GenerationStatusResponse>(`/generations/${generationId}`);
}

export async function createProfile(name: string, ideConfig: IdeConfig): Promise<Profile> {
  return fetchJson<Profile>("/profiles", {
    method: "POST",
    body: JSON.stringify({ name, ideConfig })
  });
}

export async function listProfiles(): Promise<Profile[]> {
  const response = await fetchJson<{ items: Profile[] }>("/profiles");
  return response.items;
}

export async function getProfile(profileId: string): Promise<Profile> {
  return fetchJson<Profile>(`/profiles/${profileId}`);
}

export async function updateProfile(
  profileId: string,
  payload: { name?: string; ideConfig?: IdeConfig }
): Promise<Profile> {
  return fetchJson<Profile>(`/profiles/${profileId}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export async function deleteProfile(profileId: string): Promise<void> {
  return fetchJson<void>(`/profiles/${profileId}`, { method: "DELETE" });
}

export function setJwtToken(token: string): void {
  const normalized = token.trim();
  if (!normalized) {
    localStorage.removeItem("jwt_token");
    return;
  }
  localStorage.setItem("jwt_token", normalized);
}
