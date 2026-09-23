-- Email notifications for Pro: the weekly report, the reward-waiting email and
-- the missed-deadline email. Run this once in the Supabase SQL editor.
--
-- Two tables. A parent controls what they receive; the server records what it
-- has already sent so nobody is emailed twice about the same thing.

create table if not exists public.email_prefs (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  weekly      boolean not null default true,   -- Sunday evening report
  rewards     boolean not null default true,   -- a claim is waiting for approval
  deadlines   boolean not null default false,  -- yesterday's misses; off by default, it can nag
  send_to     text,                            -- optional: somewhere other than the login address
  timezone    text not null default 'UTC',     -- so "yesterday" means their yesterday
  updated_at  timestamptz not null default now()
);

alter table public.email_prefs enable row level security;

drop policy if exists "own email prefs: read" on public.email_prefs;
create policy "own email prefs: read"   on public.email_prefs
  for select using (auth.uid() = user_id);
drop policy if exists "own email prefs: insert" on public.email_prefs;
create policy "own email prefs: insert" on public.email_prefs
  for insert with check (auth.uid() = user_id);
drop policy if exists "own email prefs: update" on public.email_prefs;
create policy "own email prefs: update" on public.email_prefs
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- What has been sent. `ref` is the thing the email was about: a claim id for a
-- reward, a week's Monday for the report, a date for a missed deadline.
create table if not exists public.email_log (
  id       bigserial primary key,
  user_id  uuid not null references auth.users(id) on delete cascade,
  kind     text not null check (kind in ('weekly', 'reward', 'deadline')),
  ref      text not null,
  sent_at  timestamptz not null default now(),
  unique (user_id, kind, ref)
);

alter table public.email_log enable row level security;

-- A parent may see what was sent to them. Nobody writes this from the browser:
-- the sender runs with the service role, which bypasses RLS.
drop policy if exists "own email log: read" on public.email_log;
create policy "own email log: read" on public.email_log
  for select using (auth.uid() = user_id);

create index if not exists email_log_user_kind_idx on public.email_log (user_id, kind, sent_at desc);
