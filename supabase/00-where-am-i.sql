-- WHERE AM I? Paste this into the Supabase SQL editor whenever you are not
-- sure which scripts have been run. It only reads — it changes nothing, so it
-- is always safe, and safe to run twice.
--
-- Read the "verdict" column. Anything that says RUN IT is still to do.

select
  step,
  case when done then 'done' else 'RUN IT' end as verdict,
  detail
from (
  values
    ('Supabase_Setup.sql  (the months table)',
     to_regclass('public.growth_months') is not null,
     'growth_months: ' || coalesce((select count(*)::text from growth_months), 'missing') || ' rows'),

    ('supabase-profiles.sql  (character follows the child)',
     to_regclass('public.profiles') is not null,
     'profiles table'),

    ('01-emails.sql  (the Pro emails)',
     to_regclass('public.email_prefs') is not null
       and to_regclass('public.email_log') is not null,
     'email_prefs + email_log'),

    ('02-household.sql  (a second parent)',
     to_regclass('public.household_members') is not null
       and to_regclass('public.household_invites') is not null
       and exists (select 1 from pg_proc where proname = 'in_household'),
     'household_members + household_invites + in_household()'),

    ('03-children.sql  (up to four children)',
     to_regclass('public.children') is not null
       and exists (select 1 from information_schema.columns
                    where table_name = 'growth_months' and column_name = 'child_id'),
     'children table + growth_months.child_id')
) as t(step, done, detail);

-- The one check that a table's existence does NOT prove: 03 also has to remove
-- the old one-child key. If anything comes back here, a second child still
-- cannot share a month with the first, and 03 needs running again.
select
  case when count(*) = 0
       then 'good — no one-child key left on growth_months'
       else 'STILL BLOCKED by: ' || string_agg(conname, ', ')
  end as second_child_check
from pg_constraint con
join pg_class t on t.oid = con.conrelid
where t.relname = 'growth_months' and con.contype = 'u'
  and (select array_agg(att.attname::text order by att.attname)
         from unnest(con.conkey) k
         join pg_attribute att on att.attrelid = con.conrelid and att.attnum = k)
      = array['month_key','user_id'];

-- And the backfill: every month row should belong to a child.
select count(*) as months_with_no_child from public.growth_months where child_id is null;
