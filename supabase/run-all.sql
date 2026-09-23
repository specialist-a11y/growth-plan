-- ============================================================================
-- EVERYTHING, IN ORDER. Paste this whole file into the Supabase SQL editor.
--
-- GENERATED FILE — do not edit. Run supabase/build-run-all.sh to rebuild it
-- after changing any of the scripts below.
--
-- Safe to run as many times as you like: every statement in here either
-- creates something that is not there or replaces what is. So if it fails
-- part-way, fix the cause and run the whole thing again — the Supabase SQL
-- editor does not roll a script back, so a half-finished run is normal and
-- re-running is always the right answer.
--
-- One timing note, the only one that matters: this changes the key that the
-- tracker syncs against, so a browser with the app ALREADY OPEN cannot save
-- to the cloud until it is reloaded. Nothing is lost — it keeps working on
-- the device and retries. Run it when nobody is mid-routine, not at 7am.
--
-- Afterwards, run 00-where-am-i.sql to confirm.
-- ============================================================================


-- ############################################################################
-- ## Supabase_Setup.sql
-- ############################################################################

-- ====================================================================
-- SUPABASE DATABASE SETUP FOR GROWTH TRACKER
-- Run this script in your Supabase SQL Editor (Database -> SQL Editor)
-- ====================================================================

-- 1. Create growth_months table
CREATE TABLE IF NOT EXISTS public.growth_months (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid(),
  month_key TEXT NOT NULL,
  tracker_data JSONB DEFAULT '{}'::jsonb,
  intentions JSONB DEFAULT '{}'::jsonb,
  books JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT unique_user_month UNIQUE (user_id, month_key)
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.growth_months ENABLE ROW LEVEL SECURITY;

-- 3. Drop existing policies if re-running
DROP POLICY IF EXISTS "Users can select their own growth months" ON public.growth_months;
DROP POLICY IF EXISTS "Users can insert their own growth months" ON public.growth_months;
DROP POLICY IF EXISTS "Users can update their own growth months" ON public.growth_months;
DROP POLICY IF EXISTS "Users can delete their own growth months" ON public.growth_months;

-- 4. Create RLS Policies for authenticated users
CREATE POLICY "Users can select their own growth months"
  ON public.growth_months FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own growth months"
  ON public.growth_months FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own growth months"
  ON public.growth_months FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own growth months"
  ON public.growth_months FOR DELETE
  USING (auth.uid() = user_id);

-- 5. Create automatic updated_at trigger function
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_growth_months_modtime ON public.growth_months;
CREATE TRIGGER update_growth_months_modtime
    BEFORE UPDATE ON public.growth_months
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Optional: Add real-time sync table publication.
-- Adding it twice is an error, and the publication does not exist at all
-- outside Supabase, so both cases are swallowed — this has to be safe to
-- re-run like everything else here.
do $$
begin
  alter publication supabase_realtime add table public.growth_months;
exception
  when duplicate_object then null;   -- already published
  when undefined_object then null;   -- no such publication (not on Supabase)
end $$;

-- ############################################################################
-- ## supabase-profiles.sql
-- ############################################################################

-- The app saves the chosen character here so it follows a child to another
-- device. Without it the avatar is device-only; nothing else breaks.
create table if not exists public.profiles (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  avatar     text,
  updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- a parent may read and write their own row, and no one else's
drop policy if exists "own profile: read" on public.profiles;
create policy "own profile: read"   on public.profiles
  for select using (auth.uid() = user_id);
drop policy if exists "own profile: insert" on public.profiles;
create policy "own profile: insert" on public.profiles
  for insert with check (auth.uid() = user_id);
drop policy if exists "own profile: update" on public.profiles;
create policy "own profile: update" on public.profiles
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ############################################################################
-- ## supabase/01-emails.sql
-- ############################################################################

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

-- ############################################################################
-- ## supabase/02-household.sql
-- ############################################################################

-- A second parent or carer, with their own login, on the same child's data.
--
-- The data keeps belonging to the parent who created it. A second parent is
-- granted access to it rather than getting a copy, which means no existing row
-- has to move and nothing already in growth_months changes shape.
--
-- Run after 01-emails.sql.

-- ---------------------------------------------------------------- membership
create table if not exists public.household_members (
  owner_id   uuid not null references auth.users(id) on delete cascade,  -- whose data
  member_id  uuid not null references auth.users(id) on delete cascade,  -- who may see it
  role       text not null default 'parent' check (role in ('parent', 'carer')),
  created_at timestamptz not null default now(),
  primary key (owner_id, member_id),
  constraint no_self_membership check (owner_id <> member_id)
);

alter table public.household_members enable row level security;

-- Either side may see the link. Only the owner may break it, and nobody
-- inserts directly — joining goes through accept_household_invite below.
drop policy if exists "household: read own side" on public.household_members;
create policy "household: read own side" on public.household_members
  for select using (auth.uid() = owner_id or auth.uid() = member_id);
drop policy if exists "household: owner removes" on public.household_members;
create policy "household: owner removes" on public.household_members
  for delete using (auth.uid() = owner_id);
drop policy if exists "household: member leaves" on public.household_members;
create policy "household: member leaves" on public.household_members
  for delete using (auth.uid() = member_id);

-- ---------------------------------------------------------------- invitations
create table if not exists public.household_invites (
  code          text primary key,
  owner_id      uuid not null references auth.users(id) on delete cascade,
  invited_email text,
  created_at    timestamptz not null default now(),
  expires_at    timestamptz not null default now() + interval '7 days',
  accepted_by   uuid references auth.users(id) on delete set null,
  accepted_at   timestamptz
);

alter table public.household_invites enable row level security;

-- An owner sees their own invitations. Nobody else can list them: a code is
-- only useful to someone who was given it.
drop policy if exists "invites: owner reads" on public.household_invites;
create policy "invites: owner reads"   on public.household_invites
  for select using (auth.uid() = owner_id);
drop policy if exists "invites: owner deletes" on public.household_invites;
create policy "invites: owner deletes" on public.household_invites
  for delete using (auth.uid() = owner_id);

create index if not exists household_invites_owner_idx on public.household_invites (owner_id, created_at desc);

-- ---------------------------------------------------------------- joining
-- Both of these run as the definer so they can check things the caller is not
-- allowed to read — an invite belonging to someone else, for instance.

create or replace function public.create_household_invite(p_email text default null)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_code text;
  v_live int;
begin
  if auth.uid() is null then raise exception 'sign in first'; end if;

  -- a second parent may not invite a third: only the data owner invites
  if exists (select 1 from household_members where member_id = auth.uid()) then
    raise exception 'only the parent who set up the account can invite someone';
  end if;

  select count(*) into v_live from household_invites
   where owner_id = auth.uid() and accepted_by is null and expires_at > now();
  if v_live >= 3 then raise exception 'too many invitations already open'; end if;

  -- 8 characters, no look-alikes: people read these over the phone
  v_code := upper(translate(substr(encode(gen_random_bytes(8), 'base64'), 1, 8), 'OI01+/=', 'XYZW234'));
  insert into household_invites (code, owner_id, invited_email) values (v_code, auth.uid(), p_email);
  return v_code;
end;
$$;

create or replace function public.accept_household_invite(p_code text)
returns uuid
language plpgsql security definer set search_path = public
as $$
declare
  v_owner uuid;
begin
  if auth.uid() is null then raise exception 'sign in first'; end if;

  select owner_id into v_owner from household_invites
   where code = upper(trim(p_code)) and accepted_by is null and expires_at > now();
  if v_owner is null then raise exception 'that code is not valid, or it has expired'; end if;
  if v_owner = auth.uid() then raise exception 'that is your own invitation'; end if;

  -- one household at a time: a carer cannot hold two children's data at once
  if exists (select 1 from household_members where member_id = auth.uid() and owner_id <> v_owner) then
    raise exception 'you are already part of another family';
  end if;

  insert into household_members (owner_id, member_id) values (v_owner, auth.uid())
    on conflict (owner_id, member_id) do nothing;
  update household_invites set accepted_by = auth.uid(), accepted_at = now() where code = upper(trim(p_code));
  return v_owner;
end;
$$;

grant execute on function public.create_household_invite(text) to authenticated;
grant execute on function public.accept_household_invite(text) to authenticated;

-- Whose data this login should open: their own, unless they were invited.
create or replace function public.household_owner()
returns uuid
language sql stable security definer set search_path = public
as $$
  select coalesce((select owner_id from household_members where member_id = auth.uid() limit 1), auth.uid());
$$;

grant execute on function public.household_owner() to authenticated;

-- ---------------------------------------------------------------- access
-- The rule everything hangs on: a row belongs to its owner, and to anyone the
-- owner has added to the household.
create or replace function public.in_household(p_owner uuid)
returns boolean
language sql stable security definer set search_path = public
as $$
  select auth.uid() = p_owner
      or exists (select 1 from household_members where owner_id = p_owner and member_id = auth.uid());
$$;

grant execute on function public.in_household(uuid) to authenticated;

-- Replace the single-user policies on the data tables.
drop policy if exists "own months: read"   on public.growth_months;
drop policy if exists "own months: write"  on public.growth_months;
drop policy if exists "own months: update" on public.growth_months;
drop policy if exists "own months: delete" on public.growth_months;

drop policy if exists "household months: read" on public.growth_months;
create policy "household months: read"   on public.growth_months
  for select using (in_household(user_id));
drop policy if exists "household months: insert" on public.growth_months;
create policy "household months: insert" on public.growth_months
  for insert with check (in_household(user_id));
drop policy if exists "household months: update" on public.growth_months;
create policy "household months: update" on public.growth_months
  for update using (in_household(user_id)) with check (in_household(user_id));
drop policy if exists "household months: delete" on public.growth_months;
create policy "household months: delete" on public.growth_months
  for delete using (in_household(user_id));

drop policy if exists "own profile: read"   on public.profiles;
drop policy if exists "own profile: insert" on public.profiles;
drop policy if exists "own profile: update" on public.profiles;

drop policy if exists "household profile: read" on public.profiles;
create policy "household profile: read"   on public.profiles
  for select using (in_household(user_id));
drop policy if exists "household profile: insert" on public.profiles;
create policy "household profile: insert" on public.profiles
  for insert with check (in_household(user_id));
drop policy if exists "household profile: update" on public.profiles;
create policy "household profile: update" on public.profiles
  for update using (in_household(user_id)) with check (in_household(user_id));

-- Email preferences stay personal: two parents can want different emails.
-- The policies from 01-emails.sql already do that, and are left alone.

-- ---------------------------------------------------------------- checking it
-- After running this, prove it from two accounts:
--   1. as the owner:   select create_household_invite('carer@example.com');
--   2. as the invitee: select accept_household_invite('THATCODE');
--   3. as the invitee: select count(*) from growth_months;   -- sees the family's rows
--   4. as a stranger:  select count(*) from growth_months;   -- must still be 0

-- ############################################################################
-- ## supabase/03-children.sql
-- ############################################################################

-- Up to four children on one account.
--
-- The app that uses this is already deployed, so the only care needed is
-- timing: a browser with the tracker ALREADY OPEN is holding no child id and
-- upserts against the unique index this script replaces, so it cannot sync
-- until it is reloaded. Nothing is lost — the tracker keeps working on the
-- device and retries — but run this when nobody is mid-routine, not at 7am.
--
-- Run after 02-household.sql. Safe to run twice: the Supabase SQL editor does
-- not wrap a script in one transaction, so a failure part-way leaves earlier
-- statements committed, and the fix is always to run the whole file again.

-- ---------------------------------------------------------------- the children
create table if not exists public.children (
  id          uuid primary key default gen_random_uuid(),
  owner_id    uuid not null references auth.users(id) on delete cascade,
  name        text not null default '',
  sort        int  not null default 0,
  created_at  timestamptz not null default now(),
  -- set when a plan drops back to one child; the row is kept for 30 days so a
  -- parent can resubscribe or export before anything is deleted
  archived_at timestamptz
);

alter table public.children enable row level security;

drop policy if exists "children: read" on public.children;
create policy "children: read"   on public.children
  for select using (in_household(owner_id));
drop policy if exists "children: insert" on public.children;
create policy "children: insert" on public.children
  for insert with check (in_household(owner_id));
drop policy if exists "children: update" on public.children;
create policy "children: update" on public.children
  for update using (in_household(owner_id)) with check (in_household(owner_id));
drop policy if exists "children: delete" on public.children;
create policy "children: delete" on public.children
  for delete using (auth.uid() = owner_id);      -- only the account holder

create index if not exists children_owner_idx on public.children (owner_id, sort, created_at);

-- Four is the limit on Pro, and the database is where that has to be true:
-- a UI check is a suggestion, not a rule.
create or replace function public.children_limit()
returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  if (select count(*) from children
       where owner_id = new.owner_id and archived_at is null) >= 4 then
    raise exception 'this account already has four children';
  end if;
  return new;
end;
$$;

drop trigger if exists children_limit_trigger on public.children;
create trigger children_limit_trigger before insert on public.children
  for each row execute function public.children_limit();

-- ---------------------------------------------------------------- the column
alter table public.growth_months add column if not exists child_id uuid references public.children(id) on delete cascade;

-- Everyone who already has data gets a child row, and their rows are filed
-- under it. The name comes from the tracker's own settings bundle where there
-- is one, so a parent does not meet "Child 1" after using this for months.
do $$
declare
  r record;
  v_child uuid;
  v_name  text;
begin
  for r in select distinct user_id from public.growth_months where child_id is null loop
    -- the settings bundle holds localStorage values, so a name may arrive
    -- still wearing its JSON quotes
    select coalesce(
             nullif(btrim(tracker_data ->> 'teen-child-name', '"'), ''),
             '')
      into v_name
      from public.growth_months
     where user_id = r.user_id and month_key = 'teen-settings'
     limit 1;

    insert into public.children (owner_id, name, sort)
    values (r.user_id, coalesce(v_name, ''), 0)
    returning id into v_child;

    update public.growth_months set child_id = v_child
     where user_id = r.user_id and child_id is null;
  end loop;
end $$;

-- ---------------------------------------------------------------- the key
-- A month row is now one child's month. The old key allowed a single row per
-- account per month, which is exactly what stops a second child existing.
create unique index if not exists growth_months_child_month_idx
  on public.growth_months (user_id, child_id, month_key);

-- The old key has to go, or a second child's September collides with the
-- first child's September. Drop it by what it IS rather than by name: this
-- database calls it unique_user_month, a stock Postgres one would call it
-- growth_months_user_id_month_key_key, and a "drop if exists" on the wrong
-- name is a NOTICE, not an error — it would leave the limit in place and
-- every check below would still pass.
do $$
declare c record;
begin
  for c in
    select con.conname
      from pg_constraint con
      join pg_class t on t.oid = con.conrelid
     where t.relname = 'growth_months' and con.contype = 'u'
       and (select array_agg(att.attname::text order by att.attname)
              from unnest(con.conkey) k
              join pg_attribute att on att.attrelid = con.conrelid and att.attnum = k)
           = array['month_key','user_id']
  loop
    execute format('alter table public.growth_months drop constraint %I', c.conname);
    raise notice 'dropped the old one-child key: %', c.conname;
  end loop;
end $$;

-- ---------------------------------------------------------------- checking it
-- After running this:
--   select count(*) from children;                                  -- one per account with data
--   select count(*) from growth_months where child_id is null;      -- must be 0
--
--   -- the one that actually matters: no unique key on (user_id, month_key)
--   -- may survive, or a second child cannot have the same month as the first
--   select conname from pg_constraint
--    where conrelid = 'public.growth_months'::regclass and contype = 'u';
--   -- expect only keys involving child_id; nothing on user_id + month_key alone
--   select name, (select count(*) from growth_months g where g.child_id = c.id) as rows
--     from children c;                                              -- every child has their months
