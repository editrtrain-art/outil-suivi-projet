/**
 * API Client for interacting with the FastAPI backend.
 * Provides standard wrappers for HTTP methods, handling authentication
 * and error responses.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export interface ApiErrorDetail {
  detail: string | { loc: string[]; msg: string; type: string }[];
}

export class ApiError extends Error {
  status: number;
  detail: ApiErrorDetail;

  constructor(status: number, detail: ApiErrorDetail) {
    const message = typeof detail.detail === "string" 
      ? detail.detail 
      : "Validation Error";
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

/**
 * Perform a typed HTTP request to the backend.
 *
 * @param path - API path (relative to /api/v1 or absolute from base URL).
 * @param options - Request options including method, body, headers.
 * @param token - Optional Clerk JWT token for authentication.
 * @returns Parsed response body.
 */
export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE_URL}/api/v1${path}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail: ApiErrorDetail = { detail: "An unknown error occurred" };
    try {
      errorDetail = await response.json();
    } catch {
      // JSON parsing failed, keep fallback
    }
    throw new ApiError(response.status, errorDetail);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
