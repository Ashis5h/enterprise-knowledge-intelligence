const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const AUTH_TOKEN_KEY = "eki_access_token";

export type User = {
  email: string;
  name: string;
  role: string;
  department: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type ChatResponse = {
  answer: string;
  validation_status: string;
  validation_notes: string[];
  sources: Array<{
    document_name: string;
    chunk_id: string;
    page_number?: number | null;
    confidence: number;
    excerpt: string;
    department: string;
    document_type: string;
    access_level: string;
  }>;
};

export type DocumentMetadata = {
  department: string;
  document_type: string;
  access_level: string;
};

export type DocumentRecord = {
  id: string;
  filename: string;
  chunks_created: number;
  status: string;
  uploaded_at: string;
  source_path: string;
  department: string;
  document_type: string;
  access_level: string;
};

export type AnalyticsSummary = {
  queries_processed: number;
  faithfulness: number;
  context_precision: number;
  answer_relevancy: number;
  hallucination_rate: number;
};

export type EvaluationCase = {
  id: string;
  question: string;
  answer: string;
  expected_source: string;
  top_source: string | null;
  faithfulness: number;
  context_precision: number;
  answer_relevancy: number;
  context_recall: number;
  passed: boolean;
};

export type EvaluationResult = {
  generated_at: string | null;
  summary: {
    total_cases: number;
    faithfulness: number;
    context_precision: number;
    answer_relevancy: number;
    context_recall: number;
    hallucination_rate: number;
  };
  cases: EvaluationCase[];
};

export type FineTuningExample = {
  instruction: string;
  input: string;
  output: string;
  metadata: Record<string, string>;
};

export type FineTuningDataset = {
  status: string;
  examples_count: number;
  dataset_path: string;
  format: string;
  preview: FineTuningExample[];
};

export function getStoredToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setStoredToken(token: string) {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = getStoredToken();
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  const payload: LoginResponse = await response.json();
  setStoredToken(payload.access_token);
  return payload;
}

export async function getCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    clearStoredToken();
    throw new Error("Session expired");
  }

  return response.json();
}

export async function sendChat(question: string, mode: "qa" | "report" = "qa"): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ question, mode }),
  });

  if (!response.ok) {
    throw new Error("Chat request failed");
  }

  return response.json();
}

export async function uploadDocument(
  file: File,
  metadata: DocumentMetadata,
): Promise<{ id: string; filename: string; chunks_created: number; status: string }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("department", metadata.department);
  formData.append("document_type", metadata.document_type);
  formData.append("access_level", metadata.access_level);

  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Document upload failed");
  }

  return response.json();
}

export async function listDocuments(): Promise<DocumentRecord[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Document list request failed");
  }

  const payload: { documents: DocumentRecord[] } = await response.json();
  return payload.documents;
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/summary`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Analytics request failed");
  }

  return response.json();
}

export async function getEvaluationResult(): Promise<EvaluationResult> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/evaluation`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Evaluation request failed");
  }

  return response.json();
}

export async function runEvaluation(): Promise<EvaluationResult> {
  const response = await fetch(`${API_BASE_URL}/api/analytics/evaluation/run`, {
    method: "POST",
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Evaluation run failed");
  }

  return response.json();
}

export async function getFineTuningDataset(): Promise<FineTuningDataset> {
  const response = await fetch(`${API_BASE_URL}/api/fine-tuning/dataset`, {
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Fine-tuning dataset request failed");
  }

  return response.json();
}

export async function generateFineTuningDataset(): Promise<FineTuningDataset> {
  const response = await fetch(`${API_BASE_URL}/api/fine-tuning/dataset/generate`, {
    method: "POST",
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error("Fine-tuning dataset generation failed");
  }

  return response.json();
}
