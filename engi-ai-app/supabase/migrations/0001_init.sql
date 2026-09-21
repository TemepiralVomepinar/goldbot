-- ENGI AI — schema iniziale (V1 MVP)
-- Copre: account/profilo, catalogo materie/capitoli/argomenti, esercizi e tentativi,
-- materiali caricati, conversazioni con l'AI Tutor.

create extension if not exists "pgcrypto";

-- ── PROFILO STUDENTE ─────────────────────────────────────────────
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text,
  course text,
  university text,
  year smallint,
  ai_explanation_style text not null default 'universitario'
    check (ai_explanation_style in ('semplice', 'universitario', 'tecnico', 'dettagliato')),
  ai_error_mode text not null default 'suggerimento'
    check (ai_error_mode in ('soluzione', 'suggerimento', 'ragionare')),
  ai_level text not null default 'intermedio'
    check (ai_level in ('principiante', 'intermedio', 'avanzato')),
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

create policy "Un utente vede e modifica solo il proprio profilo"
  on public.profiles for all
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Crea automaticamente una riga profilo alla registrazione.
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end;
$$ language plpgsql security definer set search_path = public;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ── CATALOGO: MATERIE → CAPITOLI → ARGOMENTI ────────────────────
create table if not exists public.subjects (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  icon text not null default '📘',
  order_index int not null default 0
);

create table if not exists public.chapters (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.subjects (id) on delete cascade,
  title text not null,
  order_index int not null default 0
);

create table if not exists public.topics (
  id uuid primary key default gen_random_uuid(),
  chapter_id uuid not null references public.chapters (id) on delete cascade,
  title text not null,
  theory_md text,
  formulas_md text,
  examples_md text,
  order_index int not null default 0
);

alter table public.subjects enable row level security;
alter table public.chapters enable row level security;
alter table public.topics enable row level security;

create policy "Catalogo leggibile da chiunque sia autenticato"
  on public.subjects for select using (auth.role() = 'authenticated');
create policy "Catalogo leggibile da chiunque sia autenticato"
  on public.chapters for select using (auth.role() = 'authenticated');
create policy "Catalogo leggibile da chiunque sia autenticato"
  on public.topics for select using (auth.role() = 'authenticated');

-- ── PROGRESSO PER STUDENTE ───────────────────────────────────────
create table if not exists public.user_subject_progress (
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid not null references public.subjects (id) on delete cascade,
  progress_pct smallint not null default 0 check (progress_pct between 0 and 100),
  updated_at timestamptz not null default now(),
  primary key (user_id, subject_id)
);

create table if not exists public.user_chapter_status (
  user_id uuid not null references auth.users (id) on delete cascade,
  chapter_id uuid not null references public.chapters (id) on delete cascade,
  status text not null default 'non_studiato'
    check (status in ('non_studiato', 'debole', 'da_ripassare', 'buono')),
  updated_at timestamptz not null default now(),
  primary key (user_id, chapter_id)
);

alter table public.user_subject_progress enable row level security;
alter table public.user_chapter_status enable row level security;

create policy "Un utente gestisce solo il proprio progresso"
  on public.user_subject_progress for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Un utente gestisce solo il proprio stato capitoli"
  on public.user_chapter_status for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── ESERCIZI ──────────────────────────────────────────────────────
create table if not exists public.exercises (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.subjects (id) on delete cascade,
  chapter_id uuid references public.chapters (id) on delete set null,
  topic_id uuid references public.topics (id) on delete set null,
  difficulty smallint not null default 1 check (difficulty between 1 and 4),
  prompt text not null,
  solution text,
  created_at timestamptz not null default now()
);

alter table public.exercises enable row level security;
create policy "Esercizi leggibili da chiunque sia autenticato"
  on public.exercises for select using (auth.role() = 'authenticated');

create table if not exists public.exercise_attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  exercise_id uuid not null references public.exercises (id) on delete cascade,
  is_correct boolean,
  user_answer text,
  created_at timestamptz not null default now()
);

alter table public.exercise_attempts enable row level security;
create policy "Un utente vede e crea solo i propri tentativi"
  on public.exercise_attempts for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── MATERIALI CARICATI ────────────────────────────────────────────
create table if not exists public.materials (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid references public.subjects (id) on delete set null,
  file_name text not null,
  storage_path text not null,
  mime_type text,
  uploaded_at timestamptz not null default now()
);

alter table public.materials enable row level security;
create policy "Un utente gestisce solo i propri materiali"
  on public.materials for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Bucket di storage per i file caricati (PDF, immagini, ecc).
insert into storage.buckets (id, name, public)
values ('materials', 'materials', false)
on conflict (id) do nothing;

create policy "Un utente accede solo alla propria cartella nel bucket materials"
  on storage.objects for all
  using (bucket_id = 'materials' and auth.uid()::text = (storage.foldername(name))[1])
  with check (bucket_id = 'materials' and auth.uid()::text = (storage.foldername(name))[1]);

-- ── AI TUTOR: CONVERSAZIONI E MESSAGGI ────────────────────────────
create table if not exists public.ai_conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  mode text not null default 'spiegami'
    check (mode in ('spiegami', 'esercitati', 'aiutami', 'controlla', 'interrogami')),
  subject_id uuid references public.subjects (id) on delete set null,
  topic_id uuid references public.topics (id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.ai_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.ai_conversations (id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  created_at timestamptz not null default now()
);

alter table public.ai_conversations enable row level security;
alter table public.ai_messages enable row level security;

create policy "Un utente gestisce solo le proprie conversazioni"
  on public.ai_conversations for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Un utente gestisce solo i messaggi delle proprie conversazioni"
  on public.ai_messages for all
  using (
    exists (
      select 1 from public.ai_conversations c
      where c.id = conversation_id and c.user_id = auth.uid()
    )
  )
  with check (
    exists (
      select 1 from public.ai_conversations c
      where c.id = conversation_id and c.user_id = auth.uid()
    )
  );
