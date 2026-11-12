export type LanguageCode = 'en' | 'hi' | 'te' | 'ta' | 'kn' | 'ml';

export interface LanguageMeta {
  code: LanguageCode;
  name: string;
  nativeName: string;
  script: string;
  sampleQuestion: string;
}

export const SUPPORTED_LANGUAGES: LanguageMeta[] = [
  { code: 'en', name: 'English', nativeName: 'English', script: 'Latin', sampleQuestion: 'What is photosynthesis?' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', script: 'Devanagari', sampleQuestion: 'ताजमहल कहां स्थित है?' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', script: 'Telugu', sampleQuestion: 'భారత రాజధాని ఎక్కడ ఉంది?' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', script: 'Tamil', sampleQuestion: 'தமிழ்நாட்டின் தலைநகரம் எது?' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', script: 'Kannada', sampleQuestion: 'ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಯಾವುದು?' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', script: 'Malayalam', sampleQuestion: 'കേരളത്തിന്റെ തലസ്ഥാനം ഏതാണ്?' },
];

export interface Citation {
  pid: string;
  source: string;
  score: number | string;
  text: string;
  rank?: number;
  id?: string;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'bot' | 'system';
  content: string;
  status?: string;
  citations?: Citation[];
  created_at?: string;
  model?: string;
  latency_ms?: number;
}

export interface ChatHistoryItem {
  id: string;
  session_id: string;
  title: string;
  created: number;
  updated_at?: number;
}

export interface StreamMetaEvent {
  type: 'meta';
  session_id: string;
  lang: string;
  input_lang: string;
  input_style: string;
  answer_lang: string;
  answer_script: string;
  mode: string;
  model: string;
  guest_message_count?: number | null;
  guest_limit?: number | null;
  guest_quota_reached?: boolean;
}

export interface StreamDeltaEvent {
  type: 'delta';
  text: string;
}

export interface StreamDoneEvent {
  type: 'done';
  answer: string;
  status: 'answered' | 'insufficient_evidence' | 'stopped' | string;
  citations: Citation[];
  model: string;
  latency_ms: number;
  input_lang?: string;
  input_style?: string;
  answer_lang?: string;
  answer_script?: string;
  guest_message_count?: number | null;
  guest_limit?: number | null;
  guest_quota_reached?: boolean;
}

export interface StreamErrorEvent {
  type: 'error';
  error: string;
  message?: string;
  retryable?: boolean;
}

export type ChatStreamEvent = StreamMetaEvent | StreamDeltaEvent | StreamDoneEvent | StreamErrorEvent;

export interface GuestStatus {
  authenticated: boolean;
  guest_message_count: number;
  guest_limit: number;
  guest_remaining: number | null;
  guest_quota_reached: boolean;
}

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  type: 'system' | 'research' | 'info';
}

export interface DashboardMetric {
  n: number;
  correctness: number | null;
  faithfulness: number | null;
  purity: number | null;
  in_lang_rate: number | null;
  f1: number | null;
  em: number | null;
}

export interface DashboardData {
  generator: string;
  generator_active: string;
  judge_model: string | null;
  counts: {
    judged: number;
    failures: number;
    languages: number;
    retrieval_rows: number;
  };
  by_language: Record<string, Record<string, DashboardMetric>>;
  retrieval: Array<{
    lang: string;
    mode: string;
    'recall@1'?: number;
    'recall@5'?: number;
    mrr?: number;
  }>;
}

export interface LanguageComparisonRow {
  lang: string;
  name: string;
  script: string;
  closed_book: number | null;
  gold_context: number | null;
  rag: number | null;
  rag_translit: number | null;
  recall_native: number | null;
  recall_romanized: number | null;
}

export type ComparisonLanguageRow = LanguageComparisonRow;

export interface ComparisonData {
  generator: string;
  languages: LanguageComparisonRow[];
}

export interface FailureItem {
  qid: string;
  lang: string;
  mode: string;
  correctness: number;
  faithfulness: number | null;
  issues: string[];
  retrieved_hit: boolean;
  purity?: number;
  question: string;
  gloss_question?: string;
  reference?: string;
  gloss_reference?: string;
  answer: string;
  gloss_answer?: string;
}

export interface FailuresResponse {
  failures: FailureItem[];
  total_matching: number;
}

export interface UserSession {
  authenticated: boolean;
  user: {
    id: number;
    name: string;
    email: string;
  } | null;
}
