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
import { groupByChild, weeklyReport, newClaims, missedYesterday, lastWeekRange } from './report.js';

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

function weeklySection(r: any, showName: boolean) {
  const hw = r.homework
    ? row('Homework on time', `${r.homework.done} of ${r.homework.done + r.homework.late + r.homework.missed}`)
    : '';
  const waiting = r.pending.length
    ? `<p style="margin:12px 0 0;padding:12px 14px;background:#fbf0dc;border-radius:10px;font-size:14px;">
         <b>${r.pending.length} reward${r.pending.length === 1 ? '' : 's'} waiting for you:</b>
         ${r.pending.map((p: any) => esc(p.name)).join(', ')}.</p>` : '';
  return `${showName ? `<h2 style="margin:22px 0 8px;font-size:16px;">${esc(r.childName)}</h2>` : ''}
    <table style="width:100%;border-collapse:collapse;font-size:15px;">
      ${row('Average completion', r.average + '%')}
      ${row('Perfect days', String(r.perfect))}
      ${row('Days used', `${r.daysCounted} of 7`)}
      ${row('Current streak', r.streak === 1 ? '1 day' : r.streak + ' days')}
      ${hw}
    </table>${waiting}`;
}

function weeklyEmail(reports: any[]) {
  const r0 = reports[0];
  const when = `${r0.start.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })} – ${r0.stop.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}`;
  const many = reports.length > 1;
  const title = many ? 'Your children\'s week' : `${r0.childName}'s week`;
  return shell(title, `<p style="margin:0 0 4px;color:#4e5a6e;">${esc(when)}</p>
    ${reports.map(r => weeklySection(r, many)).join('')}`);
}

function rewardEmail(claims: any[]) {
  const many = new Set(claims.map(c => c.childName)).size > 1;
  const list = claims.map(c =>
    `<li style="margin:6px 0;"><b>${esc(c.name)}</b> — ${esc(c.cost)} points${many ? ` <span style="color:#4e5a6e;">(${esc(c.childName)})</span>` : ''}</li>`).join('');
  const who = many ? 'Your children' : claims[0].childName;
  return shell(
    claims.length === 1 ? `${who} claimed a reward` : `${who} claimed ${claims.length} rewards`,
    `<p style="margin:0 0 12px;color:#4e5a6e;">Waiting for you to approve or decline:</p>
     <ul style="margin:0;padding-left:20px;font-size:15px;">${list}</ul>`);
}

function deadlineEmail(misses: any[]) {
  const when = misses[0].date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' });
  const many = misses.length > 1;
  const bit = (label: string, items: string[]) => items.length
    ? `<p style="margin:12px 0 4px;font-weight:700;">${label}</p>
       <ul style="margin:0;padding-left:20px;font-size:15px;color:#4e5a6e;">
         ${items.map(i => `<li style="margin:4px 0;">${esc(i)}</li>`).join('')}</ul>` : '';
  return shell(many ? `Yesterday: ${when}` : `${misses[0].childName}: ${when}`, `
    <p style="margin:0;color:#4e5a6e;">Here is what yesterday's deadlines caught. Nothing was taken away —
      late ticks simply earned no points.</p>
    ${misses.map(m => `${many ? `<h2 style="margin:20px 0 4px;font-size:16px;">${esc(m.childName)}</h2>` : ''}
      ${bit('Not done', m.missed)}${bit('Done, but late', m.late)}`).join('')}`);
}

/* ------------------------------------------------------------------ plumbing */

/* One account can hold up to four children, and a second parent can be reading
   the same account. An email goes to a person and covers every child they can
   see, rather than one email per child per parent. */
async function everyParent() {
  const { data: rows, error } = await db
    .from('growth_months').select('user_id, child_id, month_key, tracker_data')
    .order('user_id');
  if (error) throw error;

  const byOwner = new Map<string, any[]>();
  for (const r of rows ?? []) {
    if (!byOwner.has(r.user_id)) byOwner.set(r.user_id, []);
    byOwner.get(r.user_id)!.push(r);
  }

  const { data: prefs } = await db.from('email_prefs').select('*');
  const prefBy = new Map<string, any>((prefs ?? []).map((p: any) => [p.user_id, p]));
  const { data: members } = await db.from('household_members').select('owner_id, member_id');
  const { data: kids } = await db.from('children').select('id, name, archived_at');
  const nameOf = new Map<string, string>((kids ?? []).filter((k: any) => !k.archived_at).map((k: any) => [k.id, k.name]));

  // everyone who should hear about an account: the owner, and anyone they added
  const readers = new Map<string, Set<string>>();          // owner_id -> user ids
  for (const owner of byOwner.keys()) readers.set(owner, new Set([owner]));
  for (const m of members ?? []) {
    if (!readers.has(m.owner_id)) continue;
    readers.get(m.owner_id)!.add(m.member_id);
  }

  const out: any[] = [];
  for (const [owner_id, ownerRows] of byOwner) {
    const children = groupByChild(ownerRows).map((c: any) => ({
      ...c,
      name: (c.childId && nameOf.get(c.childId)) || c.settings.childName || 'your child'
    }));
    if (!children.length) continue;                        // never synced
    for (const user_id of readers.get(owner_id)!) {
      const pref = prefBy.get(user_id) ?? { weekly: true, rewards: true, deadlines: false };
      const { data: who } = await db.auth.admin.getUserById(user_id);
      const email = pref.send_to || who?.user?.email;
      if (!email || String(email).includes('(Local Profile)')) continue;
      out.push({ user_id, owner_id, email, pref, children });
    }
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
    const fresh: any[] = [];
    for (const c of p.children) {
      // the claim id is only unique within a child, so the record is keyed by both
      const mine = newClaims(c.settings, told.map((t: string) => t.split(':').pop()));
      const seen = new Set(told);
      for (const claim of mine) {
        const ref = `${c.childId ?? 'legacy'}:${claim.id}`;
        if (seen.has(ref)) continue;
        fresh.push({ ...claim, ref, childName: c.name });
      }
    }
    if (!fresh.length) continue;
    const who = new Set(fresh.map(c => c.childName)).size > 1 ? 'Your children' : fresh[0].childName;
    await send(p.email, `${who} claimed a reward`, rewardEmail(fresh), dry);
    if (!dry) await logSent(p.user_id, 'reward', fresh.map(c => c.ref));
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
    const reports = p.children
      .map((c: any) => ({ ...weeklyReport(c.months, c.settings, today), childName: c.name }))
      .filter((r: any) => r.worthSending);           // an unused week is not a scoreboard of zeros
    if (!reports.length) continue;
    const subject = reports.length > 1
      ? `Your children's week: ${reports.map((r: any) => `${r.childName} ${r.average}%`).join(', ')}`
      : `${reports[0].childName}'s week: ${reports[0].average}% and ${reports[0].perfect} perfect days`;
    await send(p.email, subject, weeklyEmail(reports), dry);
    if (!dry) await logSent(p.user_id, 'weekly', [ref]);
    sent.push({ to: p.email, children: reports.length });
  }
  return sent;
}

async function runDeadlines(dry: boolean, today = new Date()) {
  const sent = [];
  for (const p of await everyParent()) {
    if (!p.pref.deadlines) continue;
    const misses = p.children
      .map((c: any) => { const m = missedYesterday(c.months, c.settings, today); return m ? { ...m, childName: c.name } : null; })
      .filter(Boolean) as any[];
    if (!misses.length) continue;
    const ref = misses[0].date.toISOString().slice(0, 10);
    if ((await alreadySent(p.user_id, 'deadline')).includes(ref)) continue;
    const total = misses.reduce((n, m) => n + m.missed.length, 0);
    const who = misses.length > 1 ? 'Your children' : misses[0].childName;
    await send(p.email, `${who}: ${total} missed yesterday`, deadlineEmail(misses), dry);
    if (!dry) await logSent(p.user_id, 'deadline', [ref]);
    sent.push({ to: p.email, missed: total });
  }
  return sent;
}

Deno.serve(async (req: Request) => {
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
    return Response.json({ job, error: String((e as Error)?.message ?? e) }, { status: 500 });
  }
});
