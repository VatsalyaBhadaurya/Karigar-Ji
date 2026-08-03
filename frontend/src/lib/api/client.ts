import { ApiResult, ApiError } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function apiRequest<TResponse>(
  endpoint: string,
  options: {
    method: "GET" | "POST" | "PATCH" | "DELETE";
    body?: Record<string, unknown> | FormData;
    token: string;
    isFormData?: boolean;
  }
): Promise<ApiResult<TResponse>> {
  const { method, body, token, isFormData } = options;

  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
  };
  if (!isFormData && body) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers,
      body: isFormData
        ? (body as FormData)
        : body !== undefined
        ? JSON.stringify(body)
        : undefined,
    });

    if (res.status === 401) {
      window.location.href = "/auth/login";
      return { data: null, error: { error_code: "UNAUTHORIZED", message: "Session expired", status: 401 } };
    }

    const json = await res.json();

    if (!res.ok) {
      const err: ApiError = {
        error_code: json.detail?.error_code ?? "API_ERROR",
        message: json.detail?.message ?? json.message ?? "Request failed",
        status: res.status,
      };
      return { data: null, error: err };
    }

    return { data: json as TResponse, error: null };
  } catch {
    return {
      data: null,
      error: { error_code: "NETWORK_ERROR", message: "Network request failed" },
    };
  }
}
