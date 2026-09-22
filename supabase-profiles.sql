-- The app saves the chosen character here so it follows a child to another
-- device. Without it the avatar is device-only; nothing else breaks.
create table if not exists public.profiles (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  avatar     text,
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- a parent may read and write their own row, and no one else's
create policy "own profile: read"   on public.profiles
  for select using (auth.uid() = user_id);
create policy "own profile: insert" on public.profiles
  for insert with check (auth.uid() = user_id);
create policy "own profile: update" on public.profiles
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
