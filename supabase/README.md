# The Pro emails

Three emails the sales page promises: a weekly report, a reward waiting for
approval, and yesterday's missed deadlines. They run on Supabase, not in the
browser, because a phone that is switched off cannot email anybody.

Nothing new has to be synced — the tracker already sends the month rows, the
task list, the claims and the deadline settings to `growth_months`, so the
server can work all of it out from what is already there.

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
supabase secrets set EMAIL_FROM="UNPROMPTED <hello@yourdomain>"
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

## Changing the email provider

Only `send()` in `functions/notify/index.ts` knows about Resend — it is one
`fetch`. Postmark or SES is a ten-line change; nothing else moves.
