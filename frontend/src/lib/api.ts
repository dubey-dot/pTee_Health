export interface PatientField {
  label: string;
  value: string;
}

export interface PatientSummary {
  id: string;
  name: string;
  fields: PatientField[];
  clinicalSummary: string;
  doctorsNotesCount: number;
}

export interface PatientCreateInput {
  name: string;
  age?: number;
  gender?: string;
  occupationSport?: string;
  chiefComplaint?: string;
  duration?: string;
  painScore?: string;
  aggravating?: string;
  relieving?: string;
  previousInjuries?: string;
}

export type AssessmentStatus = "reviewing" | "completed";
export type DiagnosisAction = "agree" | "update" | "fully-change";

export interface Assessment {
  id: string;
  patientId: string;
  status: AssessmentStatus;
  diagnosis: string;
  confidence: number;
  diagnosisAction: DiagnosisAction | null;
  version: number;
}

export interface FindingDetail {
  question: string;
  bullets: string[];
}

export interface Finding {
  id: string;
  assessmentId: string;
  tag: string;
  label: string;
  selected: boolean;
  detail: FindingDetail | null;
}

export type TestType = "joint" | "muscle" | "gait";

export interface LoggedTest {
  id: string;
  assessmentId: string;
  type: TestType;
  name: string;
  result: string;
}

export interface InsightTag {
  label: string;
  meta: string;
}

export interface Insights {
  assessmentId: string;
  summary: string;
  tags: InsightTag[];
}

export type NoteSource = "typed" | "voice";

export interface DoctorNote {
  id: string;
  assessmentId: string;
  content: string;
  source: NoteSource;
  createdAt: string;
}

export interface RecommendedTest {
  testName: string;
  summary: string;
  whyRecommended: string;
  confidence: number;
}

export interface TestRecommendationBatch {
  tests: RecommendedTest[];
  noRecommendationReason: string | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${init?.method ?? "GET"} ${path} failed: ${res.status} ${body}`);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  listPatients: () => request<PatientSummary[]>(`/patients`),

  getPatient: (patientId: string) => request<PatientSummary>(`/patients/${patientId}`),

  createPatient: (data: PatientCreateInput) =>
    request<PatientSummary>(`/patients`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listAssessmentsForPatient: (patientId: string) =>
    request<Assessment[]>(`/patients/${patientId}/assessments`),

  createAssessment: (patientId: string) =>
    request<Assessment>(`/patients/${patientId}/assessments`, { method: "POST" }),

  getAssessment: (assessmentId: string) => request<Assessment>(`/assessments/${assessmentId}`),

  updateAssessmentStatus: (assessmentId: string, status: AssessmentStatus) =>
    request<Assessment>(`/assessments/${assessmentId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  updateDiagnosis: (
    assessmentId: string,
    data: { action?: DiagnosisAction; diagnosis?: string }
  ) =>
    request<Assessment>(`/assessments/${assessmentId}/diagnosis`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  generateDiagnosis: (assessmentId: string) =>
    request<Assessment>(`/assessments/${assessmentId}/diagnosis/generate`, {
      method: "POST",
    }),

  getFindings: (assessmentId: string) =>
    request<Finding[]>(`/assessments/${assessmentId}/findings`),

  updateFinding: (findingId: string, label: string) =>
    request<Finding>(`/findings/${findingId}`, {
      method: "PATCH",
      body: JSON.stringify({ label }),
    }),

  deleteFinding: (findingId: string) => request<void>(`/findings/${findingId}`, { method: "DELETE" }),

  createTest: (assessmentId: string, data: { type: TestType; name: string; result: string }) =>
    request<LoggedTest>(`/assessments/${assessmentId}/tests`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getInsights: (assessmentId: string) => request<Insights>(`/assessments/${assessmentId}/insights`),

  getNotes: (assessmentId: string) => request<DoctorNote[]>(`/assessments/${assessmentId}/notes`),

  createNote: (assessmentId: string, data: { content: string; source?: NoteSource }) =>
    request<DoctorNote>(`/assessments/${assessmentId}/notes`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getTestRecommendations: (assessmentId: string) =>
    request<TestRecommendationBatch>(`/assessments/${assessmentId}/recommendations`, {
      method: "POST",
    }),
};
