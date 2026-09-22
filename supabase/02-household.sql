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
create policy "household: read own side" on public.household_members
  for select using (auth.uid() = owner_id or auth.uid() = member_id);
create policy "household: owner removes" on public.household_members
  for delete using (auth.uid() = owner_id);
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
create policy "invites: owner reads"   on public.household_invites
  for select using (auth.uid() = owner_id);
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

create policy "household months: read"   on public.growth_months
  for select using (in_household(user_id));
create policy "household months: insert" on public.growth_months
  for insert with check (in_household(user_id));
create policy "household months: update" on public.growth_months
  for update using (in_household(user_id)) with check (in_household(user_id));
create policy "household months: delete" on public.growth_months
  for delete using (in_household(user_id));

drop policy if exists "own profile: read"   on public.profiles;
drop policy if exists "own profile: insert" on public.profiles;
drop policy if exists "own profile: update" on public.profiles;

create policy "household profile: read"   on public.profiles
  for select using (in_household(user_id));
create policy "household profile: insert" on public.profiles
  for insert with check (in_household(user_id));
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
