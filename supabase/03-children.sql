-- Up to four children on one account.
--
-- The app that uses this is already deployed, so the only care needed is
-- timing: a browser with the tracker ALREADY OPEN is holding no child id and
-- upserts against the unique index this script replaces, so it cannot sync
-- until it is reloaded. Nothing is lost — the tracker keeps working on the
-- device and retries — but run this when nobody is mid-routine, not at 7am.
--
-- Run after 02-household.sql.

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

create policy "children: read"   on public.children
  for select using (in_household(owner_id));
create policy "children: insert" on public.children
  for insert with check (in_household(owner_id));
create policy "children: update" on public.children
  for update using (in_household(owner_id)) with check (in_household(owner_id));
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
