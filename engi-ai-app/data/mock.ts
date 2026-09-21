// Dati dimostrativi per la V1 MVP: permettono di navigare l'app (Materie, Argomenti,
// Esercizi, Progressi) senza dover prima popolare il database Supabase.
// Quando il catalogo reale sarà in `subjects`/`chapters`/`topics`/`exercises`,
// sostituisci questi import con query a `lib/supabase.ts`.
import type { ChapterStatus } from "@/lib/theme";

export interface MockTopic {
  id: string;
  title: string;
  theory: string;
  formulas: string[];
  examples: string[];
}

export interface MockChapter {
  id: string;
  title: string;
  status: ChapterStatus;
  topics: MockTopic[];
}

export interface MockSubject {
  id: string;
  slug: string;
  name: string;
  icon: string;
  progressPct: number;
  chapters: MockChapter[];
}

export const mockSubjects: MockSubject[] = [
  {
    id: "analisi-1",
    slug: "analisi-1",
    name: "Analisi Matematica 1",
    icon: "📐",
    progressPct: 64,
    chapters: [
      { id: "insiemi", title: "Insiemi e funzioni", status: "buono", topics: [] },
      { id: "limiti", title: "Limiti", status: "buono", topics: [] },
      { id: "continuita", title: "Continuità", status: "buono", topics: [] },
      { id: "derivate", title: "Derivate", status: "da_ripassare", topics: [] },
      {
        id: "integrali",
        title: "Integrali",
        status: "debole",
        topics: [
          {
            id: "integrali-indefiniti",
            title: "Integrali indefiniti",
            theory:
              "L'integrale indefinito di una funzione f(x) è l'insieme di tutte le primitive di f, " +
              "cioè le funzioni F(x) tali che F'(x) = f(x). Si scrive ∫f(x)dx = F(x) + C.",
            formulas: ["∫xⁿdx = xⁿ⁺¹/(n+1) + C", "∫eˣdx = eˣ + C", "∫1/x dx = ln|x| + C"],
            examples: ["∫2x dx = x² + C", "∫cos(x) dx = sin(x) + C"],
          },
        ],
      },
      { id: "serie", title: "Serie", status: "debole", topics: [] },
      { id: "edo", title: "Equazioni differenziali", status: "non_studiato", topics: [] },
    ],
  },
  {
    id: "geometria",
    slug: "geometria",
    name: "Geometria",
    icon: "📏",
    progressPct: 45,
    chapters: [
      { id: "vettori", title: "Vettori e spazi vettoriali", status: "buono", topics: [] },
      { id: "matrici", title: "Matrici e determinanti", status: "debole", topics: [] },
      { id: "sistemi", title: "Sistemi lineari", status: "da_ripassare", topics: [] },
    ],
  },
  {
    id: "fisica-1",
    slug: "fisica-1",
    name: "Fisica",
    icon: "⚛️",
    progressPct: 72,
    chapters: [
      { id: "cinematica", title: "Cinematica", status: "buono", topics: [] },
      { id: "dinamica", title: "Dinamica", status: "buono", topics: [] },
      { id: "energia", title: "Lavoro ed energia", status: "da_ripassare", topics: [] },
    ],
  },
  {
    id: "chimica",
    slug: "chimica",
    name: "Chimica",
    icon: "🧪",
    progressPct: 81,
    chapters: [
      { id: "stechiometria", title: "Stechiometria", status: "buono", topics: [] },
      { id: "legami", title: "Legami chimici", status: "buono", topics: [] },
    ],
  },
  {
    id: "informatica",
    slug: "informatica",
    name: "Informatica",
    icon: "💻",
    progressPct: 58,
    chapters: [
      { id: "algoritmi", title: "Algoritmi di base", status: "buono", topics: [] },
      { id: "strutture-dati", title: "Strutture dati", status: "da_ripassare", topics: [] },
    ],
  },
  {
    id: "fondamenti-ing",
    slug: "fondamenti-ing",
    name: "Fondamenti di ingegneria",
    icon: "⚙️",
    progressPct: 30,
    chapters: [
      { id: "statica", title: "Statica", status: "non_studiato", topics: [] },
      { id: "materiali", title: "Scienza dei materiali", status: "non_studiato", topics: [] },
    ],
  },
];

export const weakAreas = ["Integrali", "Serie numeriche", "Matrici"];

export const overallProgressPct = 78;

export const nextExam = {
  subjectName: "Analisi Matematica 1",
  date: "2027-01-18",
};

export const todayGoal = {
  hoursTarget: 2.5,
  exercisesTarget: 15,
  goalPct: 70,
};
