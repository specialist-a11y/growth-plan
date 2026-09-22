/**
 * Sends the three Pro emails: the weekly report, a reward waiting for approval,
 * and yesterday's missed deadlines.
 *
 * Called by a schedule, not by the browser. It runs with the service role, so
 * it is protected by a shared secret rather than by a user's login:
 *
 *   curl -X POST "$URL/functions/v1/notify?job=rewards" -H "x-cron-key: $CRON_KEY"
 *
 * Jobs:
 *   rewards    every 30 minutes  — a claim nobody has been told about
 *   weekly     Mondays, early    — last week, Monday to Sunday
 *   deadlines  daily, morning    — what yesterday's deadlines caught
 *
 * Add ?dry=1 to see what it would send without sending anything.
 */
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { readSettings, weeklyReport, newClaims, missedYesterday, lastWeekRange } from './report.js';

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!;
const SERVICE_KEY  = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const RESEND_KEY   = Deno.env.get('RESEND_API_KEY') ?? '';
const CRON_KEY     = Deno.env.get('CRON_KEY') ?? '';
const FROM         = Deno.env.get('EMAIL_FROM') ?? 'UNPROMPTED <hello@unprompted.app>';
const APP_URL      = Deno.env.get('APP_URL') ?? 'https://growth-plan-lake.vercel.app/Growth_Tracker_Pro.html';

const SETTINGS_ROW = 'teen-settings';
const db = createClient(SUPABASE_URL, SERVICE_KEY, { auth: { persistSession: false } });

/* ------------------------------------------------------------------ email */

const esc = (s: unknown) =>
  String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function shell(title: string, body: string) {
  return `<!doctype html><html><body style="margin:0;background:#f2f5f9;padding:24px 12px;
    font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#13161d;">
    <div style="max-width:520px;margin:0 auto;background:#fff;border:1px solid #d6e0eb;border-radius:16px;overflow:hidden;">
      <div style="padding:18px 22px;border-bottom:1px solid #e4ebf3;font-weight:800;letter-spacing:.12em;font-size:14px;">
        <span style="color:#dd3f45;">UN</span>PROMPTED
      </div>
      <div style="padding:22px;">
        <h1 style="margin:0 0 12px;font-size:20px;line-height:1.3;">${esc(title)}</h1>
        ${body}
      </div>
      <div style="padding:14px 22px;border-top:1px solid #e4ebf3;font-size:12px;color:#7c89a0;">
        <a href="${APP_URL}" style="color:#2743c9;">Open the tracker</a>
        &nbsp;·&nbsp; You can turn these off in the parent dashboard, under Settings.
      </div>
    </div></body></html>`;
}

async function send(to: string, subject: string, html: string, dry: boolean) {
  if (dry) return { dry: true, to, subject };
  if (!RESEND_KEY) throw new Error('RESEND_API_KEY is not set');
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${RESEND_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: FROM, to, subject, html })
  });
  if (!res.ok) throw new Error(`Resend ${res.status}: ${(await res.text()).slice(0, 200)}`);
  return await res.json();
}

/* ------------------------------------------------- what each email looks like */

const row = (label: string, value: string) =>
  `<tr><td style="padding:7px 0;color:#4e5a6e;">${esc(label)}</td>
       <td style="padding:7px 0;text-align:right;font-weight:700;">${esc(value)}</td></tr>`;

function weeklyEmail(r: any) {
  const when = `${r.start.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} – ${r.stop.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}`;
  const hw = r.homework
    ? row('Homework on time', `${r.homework.done} of ${r.homework.done + r.homework.late + r.homework.missed}`)
    : '';
  const waiting = r.pending.length
    ? `<p style="margin:16px 0 0;padding:12px 14px;background:#fbf0dc;border-radius:10px;font-size:14px;">
         <b>${r.pending.length} reward${r.pending.length === 1 ? '' : 's'} waiting for you:</b>
         ${r.pending.map((p: any) => esc(p.name)).join(', ')}.</p>` : '';
  return shell(`${r.childName}'s week`, `
    <p style="margin:0 0 16px;color:#4e5a6e;">${esc(when)}</p>
    <table style="width:100%;border-collapse:collapse;font-size:15px;">
      ${row('Average completion', r.average + '%')}
      ${row('Perfect days', String(r.perfect))}
      ${row('Days used', `${r.daysCounted} of 7`)}
      ${row('Current streak', r.streak === 1 ? '1 day' : r.streak + ' days')}
      ${hw}
    </table>${waiting}`);
}

function rewardEmail(childName: string, claims: any[]) {
  const list = claims.map(c =>
    `<li style="margin:6px 0;"><b>${esc(c.name)}</b> — ${esc(c.cost)} points</li>`).join('');
  return shell(
    claims.length === 1 ? `${childName} claimed a reward` : `${childName} claimed ${claims.length} rewards`,
    `<p style="margin:0 0 12px;color:#4e5a6e;">Waiting for you to approve or decline:</p>
     <ul style="margin:0;padding-left:20px;font-size:15px;">${list}</ul>`);
}

function deadlineEmail(m: any) {
  const when = m.date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
  const bit = (label: string, items: string[]) => items.length
    ? `<p style="margin:12px 0 4px;font-weight:700;">${label}</p>
       <ul style="margin:0;padding-left:20px;font-size:15px;color:#4e5a6e;">
         ${items.map(i => `<li style="margin:4px 0;">${esc(i)}</li>`).join('')}</ul>` : '';
  return shell(`${m.childName}: ${when}`, `
    <p style="margin:0;color:#4e5a6e;">Here is what yesterday's deadlines caught. Nothing was taken away —
      late ticks simply earned no points.</p>
    ${bit('Not done', m.missed)}${bit('Done, but late', m.late)}`);
}

/* ------------------------------------------------------------------ plumbing */

async function everyParent() {
  const { data: rows, error } = await db
    .from('growth_months').select('user_id, month_key, tracker_data')
    .order('user_id');
  if (error) throw error;

  const byUser = new Map<string, { settings: any; months: any[] }>();
  for (const r of rows ?? []) {
    if (!byUser.has(r.user_id)) byUser.set(r.user_id, { settings: null, months: [] });
    const u = byUser.get(r.user_id)!;
    if (r.month_key === SETTINGS_ROW) u.settings = readSettings(r.tracker_data || {});
    else u.months.push(r);
  }

  const { data: prefs } = await db.from('email_prefs').select('*');
  const prefBy = new Map((prefs ?? []).map((p: any) => [p.user_id, p]));

  const out: any[] = [];
  for (const [user_id, u] of byUser) {
    if (!u.settings) continue;                       // never synced: nothing to report on
    const pref = prefBy.get(user_id) ?? { weekly: true, rewards: true, deadlines: false };
    const { data: who } = await db.auth.admin.getUserById(user_id);
    const email = pref.send_to || who?.user?.email;
    if (!email || String(email).includes('(Local Profile)')) continue;
    out.push({ user_id, email, pref, ...u });
  }
  return out;
}

async function alreadySent(user_id: string, kind: string) {
  const { data } = await db.from('email_log').select('ref').eq('user_id', user_id).eq('kind', kind);
  return (data ?? []).map((r: any) => r.ref);
}
const logSent = (user_id: string, kind: string, refs: string[]) =>
  refs.length ? db.from('email_log').insert(refs.map(ref => ({ user_id, kind, ref }))) : null;

/* ------------------------------------------------------------------ jobs */

async function runRewards(dry: boolean) {
  const sent = [];
  for (const p of await everyParent()) {
    if (!p.pref.rewards) continue;
    const told = await alreadySent(p.user_id, 'reward');
    const fresh = newClaims(p.settings, told);
    if (!fresh.length) continue;
    const name = p.settings.childName || 'Your child';
    await send(p.email, `${name} claimed a reward`, rewardEmail(name, fresh), dry);
    if (!dry) await logSent(p.user_id, 'reward', fresh.map((c: any) => c.id));
    sent.push({ to: p.email, claims: fresh.length });
  }
  return sent;
}

async function runWeekly(dry: boolean, today = new Date()) {
  const sent = [];
  const ref = lastWeekRange(today).start.toISOString().slice(0, 10);
  for (const p of await everyParent()) {
    if (!p.pref.weekly) continue;
    if ((await alreadySent(p.user_id, 'weekly')).includes(ref)) continue;
    const r = weeklyReport(p.months, p.settings, today);
    if (!r.worthSending) continue;                   // an unused week is not a scoreboard of zeros
    await send(p.email, `${r.childName}'s week: ${r.average}% and ${r.perfect} perfect days`, weeklyEmail(r), dry);
    if (!dry) await logSent(p.user_id, 'weekly', [ref]);
    sent.push({ to: p.email, average: r.average });
  }
  return sent;
}

async function runDeadlines(dry: boolean, today = new Date()) {
  const sent = [];
  for (const p of await everyParent()) {
    if (!p.pref.deadlines) continue;
    const m = missedYesterday(p.months, p.settings, today);
    if (!m) continue;
    const ref = m.date.toISOString().slice(0, 10);
    if ((await alreadySent(p.user_id, 'deadline')).includes(ref)) continue;
    await send(p.email, `${m.childName}: ${m.missed.length} missed yesterday`, deadlineEmail(m), dry);
    if (!dry) await logSent(p.user_id, 'deadline', [ref]);
    sent.push({ to: p.email, missed: m.missed.length });
  }
  return sent;
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  if (CRON_KEY && req.headers.get('x-cron-key') !== CRON_KEY) {
    return new Response('Not allowed', { status: 401 });
  }
  const job = url.searchParams.get('job') ?? '';
  const dry = url.searchParams.get('dry') === '1';
  try {
    const sent =
      job === 'rewards'   ? await runRewards(dry) :
      job === 'weekly'    ? await runWeekly(dry) :
      job === 'deadlines' ? await runDeadlines(dry) :
      null;
    if (!sent) return new Response('job must be rewards, weekly or deadlines', { status: 400 });
    return Response.json({ job, dry, count: sent.length, sent });
  } catch (e) {
    console.error(job, e);
    return Response.json({ job, error: String(e?.message ?? e) }, { status: 500 });
  }
});
