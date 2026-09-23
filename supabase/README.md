# The Pro emails

Three emails the sales page promises: a weekly report, a reward waiting for
approval, and yesterday's missed deadlines. They run on Supabase, not in the
browser, because a phone that is switched off cannot email anybody.

Nothing new has to be synced — the tracker already sends the month rows, the
task list, the claims and the deadline settings to `growth_months`, so the
server can work all of it out from what is already there.

## Which scripts have I already run?

Paste `00-where-am-i.sql` into the SQL editor. It prints one row per script
saying `done` or `RUN IT`, and it only reads, so it is always safe.

**Every script here is safe to run twice.** That is worth knowing because the
Supabase SQL editor does *not* wrap a script in a single transaction: if one
statement fails, everything before it has already been committed. A half-run
script is normal, and the fix is always to run the whole file again.

Errors name the table, and the table tells you the file:

| Table in the error | Script |
|---|---|
| `growth_months` | `../Supabase_Setup.sql` |
| `profiles` | `../supabase-profiles.sql` |
| `email_prefs`, `email_log` | `01-emails.sql` |
| `household_members`, `household_invites` | `02-household.sql` |
| `children` | `03-children.sql` |

## What you need first

- **A Resend account** (resend.com). The free tier sends 3,000 emails a month,
  which is more than a pilot will use. Verify the domain you want to send
  from; until then use their test sender.
- **The Supabase CLI**: `brew install supabase/tap/supabase`

## 1. The tables

Paste `01-emails.sql` into the Supabase SQL editor and run it. It creates:

- **`email_prefs`** — what each parent wants. They control it from the parent
  dashboard, under Settings.
- **`email_log`** — what has already been sent, so nobody is emailed twice
  about the same claim or the same week.

Both have row-level security. A parent can read their own rows and nothing
else; only the sender, which runs with the service role, writes the log.

While you are there, run `../supabase-profiles.sql` too if you have not —
it is the table that lets a chosen character follow a child to another device.

## 2. The sender

```bash
supabase login
supabase link --project-ref nbiokijwzipftiuawyrs
supabase functions deploy notify

supabase secrets set RESEND_API_KEY=re_...
supabase secrets set CRON_KEY="$(openssl rand -hex 24)"     # keep a copy
supabase secrets set EMAIL_FROM="UPNXT <hello@yourdomain>"
supabase secrets set APP_URL="https://growth-plan-lake.vercel.app/Growth_Tracker_Pro.html"
```

`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are already there — Supabase
sets them for you.

## 3. Try it without sending anything

`?dry=1` works everything out and reports what it *would* send:

```bash
curl -s -X POST "https://nbiokijwzipftiuawyrs.supabase.co/functions/v1/notify?job=weekly&dry=1" \
  -H "x-cron-key: $CRON_KEY" | jq
```

Do this for `weekly`, `rewards` and `deadlines` before scheduling anything.
Then send one to yourself for real by dropping `&dry=1`.

## 4. The schedule

In the Supabase dashboard, under Integrations → Cron, add three jobs. Each is
an HTTP POST to the function with the `x-cron-key` header.

| Job | When | Why then |
|---|---|---|
| `?job=rewards` | every 30 minutes | a claim should not sit unseen all day |
| `?job=weekly` | Mondays 07:00 | the week just gone, before the new one starts |
| `?job=deadlines` | daily 07:00 | yesterday's misses, at breakfast |

The half-hourly one is cheap: it does nothing at all unless a claim has
appeared that the parent has not been told about.

## What it will not do

- **It does not email about a week nothing happened in.** A row of zeros
  reads as an accusation, and usually means the family was away.
- **It does not email twice about the same thing**, even if a job is run again
  by hand or a schedule fires twice.
- **It does not email a device-only profile** — there is no address to use.
- **Deadline emails are off by default.** A daily list of misses is the one
  that gets a product muted, so a parent has to ask for it.

## A second parent

`02-household.sql` adds it. Run it after `01-emails.sql`.

The data keeps belonging to the parent who created it. A second parent is
granted access rather than given a copy, so **no existing row moves and
`growth_months` does not change shape** — only the policies on it do.

- `household_members` — who may see whose data
- `household_invites` — an eight-character code, good once, expires in 7 days
- `create_household_invite()` / `accept_household_invite()` — the only ways in,
  both `security definer`, because joining has to check an invitation the
  joiner is not allowed to read
- `household_owner()` — whose data this login opens, which the app asks on
  every sign-in before pulling anything

Email preferences stay personal: two parents can want different emails about
the same child.

**Prove it with two accounts before anyone relies on it**, the same way you
proved RLS:

```sql
-- as the parent who set it up
select create_household_invite('carer@example.com');
-- as the invited parent
select accept_household_invite('THATCODE');
select count(*) from growth_months;      -- sees the family's rows
-- as a stranger
select count(*) from growth_months;      -- must still be 0
```

## Up to four children

`03-children.sql`. **Run it, then deploy the app, in that order.** Between the
two there is a short window where browsers cannot sync: the app upserts against
a unique index this script replaces. Nothing is lost — the tracker keeps
working on the device and retries — but keep the gap to minutes.

- `children` — one row per child, with `archived_at` ready for the rule that
  children two to four are kept 30 days after a plan drops back to one
- `growth_months.child_id` — every month row now belongs to a child
- The four-child limit is a **trigger**, not a UI check: a rule that only
  exists in the browser is a suggestion

The script gives every account that already has data one child, named from the
tracker's own settings so nobody meets "Child 1" after months of use, and files
their existing rows under them.

On the device, the first child keeps the storage space the account already
used, so an existing family notices nothing; children two onwards get their
own. Switching child reloads the tracker into theirs.

Check before deploying:

```sql
select count(*) from children;                              -- one per account with data
select count(*) from growth_months where child_id is null;  -- must be 0
```

## Changing the email provider

Only `send()` in `functions/notify/index.ts` knows about Resend — it is one
`fetch`. Postmark or SES is a ten-line change; nothing else moves.
