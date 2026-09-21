// Tipi manuali che rispecchiano supabase/migrations/0001_init.sql.
// Se preferisci i tipi generati automaticamente, sostituiscili con:
//   npx supabase gen types typescript --project-id <id> > types/database.ts
//
// NB: usiamo `type` (non `interface`) per ogni riga: solo i type alias a oggetto
// ricevono da TypeScript un'index signature implicita, necessaria perché
// @supabase/supabase-js verifichi che ogni riga estenda `Record<string, unknown>`.
// Con `interface` la stessa identica forma non verrebbe accettata e insert/update
// risulterebbero tipizzati come `never`.

export type ChapterStatus = "non_studiato" | "debole" | "da_ripassare" | "buono";
export type ExplanationStyle = "semplice" | "universitario" | "tecnico" | "dettagliato";
export type ErrorMode = "soluzione" | "suggerimento" | "ragionare";
export type StudentLevel = "principiante" | "intermedio" | "avanzato";
export type AiTutorMode = "spiegami" | "esercitati" | "aiutami" | "controlla" | "interrogami";

export type Profile = {
  id: string;
  full_name: string | null;
  course: string | null;
  university: string | null;
  year: number | null;
  ai_explanation_style: ExplanationStyle;
  ai_error_mode: ErrorMode;
  ai_level: StudentLevel;
  created_at: string;
};

export type Subject = {
  id: string;
  slug: string;
  name: string;
  icon: string;
  order_index: number;
};

export type Chapter = {
  id: string;
  subject_id: string;
  title: string;
  order_index: number;
};

export type Topic = {
  id: string;
  chapter_id: string;
  title: string;
  theory_md: string | null;
  formulas_md: string | null;
  examples_md: string | null;
  order_index: number;
};

export type UserSubjectProgress = {
  user_id: string;
  subject_id: string;
  progress_pct: number;
  updated_at: string;
};

export type UserChapterStatus = {
  user_id: string;
  chapter_id: string;
  status: ChapterStatus;
  updated_at: string;
};

export type Exercise = {
  id: string;
  subject_id: string;
  chapter_id: string | null;
  topic_id: string | null;
  difficulty: 1 | 2 | 3 | 4;
  prompt: string;
  solution: string | null;
  created_at: string;
};

export type ExerciseAttempt = {
  id: string;
  user_id: string;
  exercise_id: string;
  is_correct: boolean | null;
  user_answer: string | null;
  created_at: string;
};

export type Material = {
  id: string;
  user_id: string;
  subject_id: string | null;
  file_name: string;
  storage_path: string;
  mime_type: string | null;
  uploaded_at: string;
};

export type AiConversation = {
  id: string;
  user_id: string;
  mode: AiTutorMode;
  subject_id: string | null;
  topic_id: string | null;
  created_at: string;
};

export type AiMessage = {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

// Shape minima richiesta da @supabase/supabase-js (>=2.116) per il generic client:
// ogni tabella deve includere `Relationships`, e lo schema `Views`/`Functions`,
// anche se qui li lasciamo vuoti.
type Table<Row, Insert = Partial<Row>, Update = Partial<Row>> = {
  Row: Row;
  Insert: Insert;
  Update: Update;
  Relationships: [];
};

export type Database = {
  public: {
    Tables: {
      profiles: Table<Profile>;
      subjects: Table<Subject>;
      chapters: Table<Chapter>;
      topics: Table<Topic>;
      user_subject_progress: Table<UserSubjectProgress>;
      user_chapter_status: Table<UserChapterStatus>;
      exercises: Table<Exercise>;
      exercise_attempts: Table<ExerciseAttempt>;
      materials: Table<Material>;
      ai_conversations: Table<AiConversation>;
      ai_messages: Table<AiMessage>;
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
  };
};
