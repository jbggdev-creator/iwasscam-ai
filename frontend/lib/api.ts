const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ApiResponse<T> = {
  success: boolean;
  data: T | null;
  error: string | null;
};

async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${path}`;
  const isFormData = init?.body instanceof FormData;

  const headers: HeadersInit = isFormData
    ? { ...(init?.headers ?? {}) }
    : { "Content-Type": "application/json", ...(init?.headers ?? {}) };

  const response = await fetch(url, { ...init, headers });

  if (!response.ok) {
    let errorMessage = response.statusText;
    try {
      const json = await response.json();
      errorMessage = json.detail ?? json.message ?? errorMessage;
    } catch {
      const text = await response.text().catch(() => "");
      errorMessage = text || errorMessage;
    }
    return { success: false, data: null, error: errorMessage };
  }

  const data: T = await response.json();
  return { success: true, data, error: null };
}

export const api = {
  get: <T>(path: string, init?: Omit<RequestInit, "method">) =>
    apiFetch<T>(path, { ...init, method: "GET" }),

  post: <T>(path: string, body: unknown, init?: Omit<RequestInit, "method" | "body">) =>
    apiFetch<T>(path, { ...init, method: "POST", body: JSON.stringify(body) }),

  postForm: <T>(path: string, body: FormData, init?: Omit<RequestInit, "method" | "body">) =>
    apiFetch<T>(path, { ...init, method: "POST", body }),
};
