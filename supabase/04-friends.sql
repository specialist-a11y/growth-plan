-- A leaderboard between friends, with both parents holding the gate.
--
-- Run after 03-children.sql. Safe to run twice.
--
-- Three decisions this file exists to enforce, none of which can live in the
-- browser:
--
--  1. NOTHING IS SHARED UNTIL BOTH PARENTS AGREE. One parent types a friend's
--     code; the other parent's account has to approve before either child sees
--     the other. A link with one approval shows nothing to anybody.
--
--  2. FRIENDS SEE A PERCENTAGE, NOTHING ELSE. What crosses between households
--     is a first name, a chosen character and a number out of 100. Never a
--     task, a reward, a note, a timetable, an email address or a birth date.
--     That is why scores live in their own table rather than being read out of
--     growth_months — there is no query a friend can run that reaches the
--     real data.
--
--  3. RANK IS SHARE OF YOUR OWN ROUTINE. A twelve-year-old with six tasks and
--     a sixteen-year-old with twenty are both measured against themselves.
--     Ranking by points would mean the child with the longest list always
--     wins, which is a reason to quit, not to carry on.

-- ---------------------------------------------------------------- the code
-- One code per child, shared out loud or over a message by the parent.
create table if not exists public.friend_codes (
  child_id   uuid primary key references public.children(id) on delete cascade,
  owner_id   uuid not null references auth.users(id) on delete cascade,
  code       text not null unique,
  created_at timestamptz not null default now()
);

alter table public.friend_codes enable row level security;

-- A code is readable only by the family it belongs to. Looking one up happens
-- inside request_friend below, which runs as the definer — so a stranger
-- cannot sit and guess codes against the table.
drop policy if exists "friend codes: own" on public.friend_codes;
create policy "friend codes: own" on public.friend_codes
  for select using (in_household(owner_id));

-- ---------------------------------------------------------------- the link
create table if not exists public.friend_links (
  id         uuid primary key default gen_random_uuid(),
  a_child    uuid not null references public.children(id) on delete cascade,
  b_child    uuid not null references public.children(id) on delete cascade,
  a_owner    uuid not null references auth.users(id) on delete cascade,
  b_owner    uuid not null references auth.users(id) on delete cascade,
  a_ok       boolean not null default true,    -- the parent who typed the code
  b_ok       boolean not null default false,   -- the parent who has to agree
  created_at timestamptz not null default now(),
  decided_at timestamptz,
  constraint friend_no_self check (a_child <> b_child)
);

alter table public.friend_links enable row level security;

-- one link per pair, whichever way round it was made
create unique index if not exists friend_links_pair_idx on public.friend_links
  (least(a_child::text, b_child::text), greatest(a_child::text, b_child::text));
create index if not exists friend_links_b_idx on public.friend_links (b_owner, b_ok);

-- Either family sees the link, so a pending request can be shown to the
-- parent who has to decide. Only ever through these policies — creating and
-- approving go through the functions below.
drop policy if exists "friend links: either side" on public.friend_links;
create policy "friend links: either side" on public.friend_links
  for select using (in_household(a_owner) or in_household(b_owner));

drop policy if exists "friend links: either side ends it" on public.friend_links;
create policy "friend links: either side ends it" on public.friend_links
  for delete using (in_household(a_owner) or in_household(b_owner));

-- ---------------------------------------------------------------- the score
-- The only thing that crosses between households.
create table if not exists public.friend_scores (
  child_id     uuid primary key references public.children(id) on delete cascade,
  owner_id     uuid not null references auth.users(id) on delete cascade,
  display_name text not null default '',
  avatar       text,
  week_key     text not null default '',
  pct          int  not null default 0 check (pct between 0 and 100),
  streak       int  not null default 0 check (streak >= 0),
  updated_at   timestamptz not null default now()
);

alter table public.friend_scores enable row level security;

-- Are this child and anyone in my household approved friends? Both sides ok,
-- or it is not a friendship.
create or replace function public.are_friends(p_child uuid)
returns boolean
language sql stable security definer set search_path = public
as $$
  select exists (
    select 1
      from friend_links l
      join children c
        on c.id = case when l.a_child = p_child then l.b_child else l.a_child end
     where l.a_ok and l.b_ok
       and (l.a_child = p_child or l.b_child = p_child)
       and in_household(c.owner_id)
  );
$$;

grant execute on function public.are_friends(uuid) to authenticated;

drop policy if exists "friend scores: mine or my friends" on public.friend_scores;
create policy "friend scores: mine or my friends" on public.friend_scores
  for select using (in_household(owner_id) or are_friends(child_id));

drop policy if exists "friend scores: write my own" on public.friend_scores;
create policy "friend scores: write my own" on public.friend_scores
  for insert with check (in_household(owner_id));
drop policy if exists "friend scores: update my own" on public.friend_scores;
create policy "friend scores: update my own" on public.friend_scores
  for update using (in_household(owner_id)) with check (in_household(owner_id));

-- ---------------------------------------------------------------- the code again
create or replace function public.my_friend_code(p_child uuid)
returns text
language plpgsql security definer set search_path = public
as $$
declare
  v_owner uuid;
  v_code  text;
begin
  select owner_id into v_owner from children where id = p_child;
  if v_owner is null or not in_household(v_owner) then
    raise exception 'that is not your child';
  end if;

  select code into v_code from friend_codes where child_id = p_child;
  if v_code is not null then return v_code; end if;

  -- six characters, no look-alikes: parents read these to each other
  loop
    v_code := upper(translate(substr(encode(gen_random_bytes(6), 'base64'), 1, 6), 'OI01+/=', 'XYZW234'));
    exit when not exists (select 1 from friend_codes where code = v_code);
  end loop;

  insert into friend_codes (child_id, owner_id, code) values (p_child, v_owner, v_code);
  return v_code;
end;
$$;

-- ---------------------------------------------------------------- asking
create or replace function public.request_friend(p_child uuid, p_code text)
returns uuid
language plpgsql security definer set search_path = public
as $$
declare
  v_owner  uuid;
  v_target uuid;
  v_towner uuid;
  v_id     uuid;
  v_count  int;
begin
  select owner_id into v_owner from children where id = p_child;
  if v_owner is null or not in_household(v_owner) then
    raise exception 'that is not your child';
  end if;

  select child_id, owner_id into v_target, v_towner
    from friend_codes where code = upper(btrim(p_code));
  if v_target is null then raise exception 'that code does not exist'; end if;
  if v_target = p_child then raise exception 'that is your own code'; end if;
  if v_towner = v_owner then raise exception 'those two already share an account'; end if;

  -- ten friends each: a leaderboard nobody can read is not a leaderboard
  select count(*) into v_count from friend_links
   where (a_child = p_child or b_child = p_child) and a_ok and b_ok;
  if v_count >= 10 then raise exception 'that is already ten friends'; end if;

  select id into v_id from friend_links
   where (a_child = p_child and b_child = v_target)
      or (a_child = v_target and b_child = p_child);
  if v_id is not null then raise exception 'those two are already connected, or waiting to be'; end if;

  insert into friend_links (a_child, b_child, a_owner, b_owner, a_ok, b_ok)
  values (p_child, v_target, v_owner, v_towner, true, false)
  returning id into v_id;
  return v_id;
end;
$$;

-- ---------------------------------------------------------------- agreeing
create or replace function public.approve_friend(p_link uuid)
returns boolean
language plpgsql security definer set search_path = public
as $$
declare v_b uuid;
begin
  select b_owner into v_b from friend_links where id = p_link and not b_ok;
  if v_b is null then raise exception 'there is nothing to approve'; end if;
  if not in_household(v_b) then
    raise exception 'only the other child''s parent can agree to this';
  end if;
  update friend_links set b_ok = true, decided_at = now() where id = p_link;
  return true;
end;
$$;

grant execute on function public.my_friend_code(uuid)    to authenticated;
grant execute on function public.request_friend(uuid, text) to authenticated;
grant execute on function public.approve_friend(uuid)    to authenticated;

-- ---------------------------------------------------------------- checking it
-- After running this, from two real accounts:
--   1. family A: select my_friend_code('<child id>');
--   2. family B: select request_friend('<their child id>', 'THATCODE');
--   3. family B: select count(*) from friend_scores;   -- still only their own
--   4. family A: select approve_friend('<link id>');   -- the second parent agrees
--   5. either:   select display_name, pct from friend_scores;  -- now both
--
-- Step 3 is the one that matters: a request nobody has agreed to must leak
-- nothing at all.
