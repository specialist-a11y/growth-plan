/**
 * What the emails say.
 *
 * Everything here is a pure function over the rows already in Supabase, so it
 * runs the same in the Edge Function and in the tests. The rules must match the
 * app: a task ticked after its deadline still shows as done but earns nothing,
 * a perfect day is the whole list, and school-only tasks are not expected on a
 * day off.
 */

const MONTH_PREFIX = 'teen-growth-month-';
const SETTINGS_ROW = 'teen-settings';

/** The app stores its settings as a bundle of JSON strings; unwrap them. */
export function readSettings(bundle) {
  const get = (key, fallback) => {
    const raw = bundle && bundle[key];
    if (raw === undefined || raw === null) return fallback;
    try { return JSON.parse(raw); } catch (e) { return typeof raw === 'string' ? raw : fallback; }
  };
  return {
    childName: String(get('teen-child-name', '') || '').trim(),
    parent: get('teen-parent-config', {}) || {},
    tasks: get('teen-custom-tasks', null),
    rewards: get('teen-rewards', []) || [],
    redemptions: get('teen-redemptions', []) || [],
    deadlines: get('teen-deadlines', { enabled: false }) || { enabled: false },
    country: get('teen-country-v1', '') || ''
  };
}

/** Days Monday–Friday count as school days unless a country calendar says otherwise. */
export function isSchoolDay(date) {
  const d = date.getDay();
  return d !== 0 && d !== 6;
}

/** Mirrors completion() in the app: what share of the day's list was done. */
export function dayCompletion(date, rec, tasks) {
  if (!tasks || !tasks.length) return null;         // no routine set up yet
  const weekend = date.getDay() === 0 || date.getDay() === 6;
  const school = isSchoolDay(date);
  const ticks = (rec && rec.tasks) || {};
  const tidy = (rec && rec.tidy) || {};
  let total = 0, done = 0;
  tasks.forEach(t => {
    if (t.schoolOnly && !school) return;
    if (t.weekendOnly && !weekend) return;
    total++;
    if (ticks[t.id]) done++;
  });
  if (weekend) total += 4;
  ['floor', 'desk', 'bed', 'sweepMop'].forEach(k => { if (tidy[k]) done++; });
  if (total === 0) return null;
  return Math.min(100, Math.round((done / total) * 100));
}

/** Every stored day, oldest first, as { date, rec }. */
export function daysFromRows(rows) {
  const out = [];
  rows.forEach(row => {
    const key = row.month_key || '';
    if (key.indexOf(MONTH_PREFIX) !== 0) return;
    const month = key.slice(MONTH_PREFIX.length);
    if (!/^\d{4}-\d{2}$/.test(month)) return;
    const tracker = (row.tracker_data && row.tracker_data.tracker) || {};
    const [y, m] = month.split('-').map(Number);
    const last = new Date(Date.UTC(y, m, 0)).getUTCDate();
    for (let day = 1; day <= last; day++) {
      out.push({ date: new Date(y, m - 1, day), rec: tracker[day] || null });
    }
  });
  return out.sort((a, b) => a.date - b.date);
}

/** The week that just ended, Monday to Sunday, relative to `today`. */
export function lastWeekRange(today) {
  const end = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const back = (end.getDay() + 6) % 7;               // days since Monday
  const thisMonday = new Date(end.getFullYear(), end.getMonth(), end.getDate() - back);
  const start = new Date(thisMonday.getFullYear(), thisMonday.getMonth(), thisMonday.getDate() - 7);
  const stop = new Date(thisMonday.getFullYear(), thisMonday.getMonth(), thisMonday.getDate() - 1);
  return { start, stop };
}

const sameDay = (a, b) => a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();

/** The numbers a parent actually wants on a Sunday evening. */
export function weeklyReport(rows, settings, today) {
  const { start, stop } = lastWeekRange(today);
  const tasks = settings.tasks;
  const days = daysFromRows(rows).filter(d => d.date >= start && d.date <= stop);

  let counted = 0, sum = 0, perfect = 0, ticks = 0;
  let hwDone = 0, hwLate = 0, hwMissed = 0;
  const hasHomework = !!(tasks || []).find(t => t.id === 'homework');
  const deadlinesOn = !!(settings.deadlines && settings.deadlines.enabled);

  days.forEach(({ date, rec }) => {
    // a day with no record is a day nobody opened, not a day that went badly:
    // counting it as 0% turns a holiday into a week of failure
    if (!rec) return;
    const pct = dayCompletion(date, rec, tasks);
    if (pct !== null) { counted++; sum += pct; if (pct === 100) perfect++; }
    ticks += Object.values((rec && rec.tasks) || {}).filter(Boolean).length;
    if (hasHomework && isSchoolDay(date)) {
      const done = !!(rec && rec.tasks && rec.tasks.homework);
      // the same rule the app scores by: no deadlines in force, nothing is late
      const late = deadlinesOn && !!(rec && rec.late && rec.late.homework);
      const excused = !!(rec && rec.excused);
      if (done && (!late || excused)) hwDone++;
      else if (done) hwLate++;
      else hwMissed++;
    }
  });

  // the streak as it stands today, counting back from yesterday
  const all = daysFromRows(rows);
  let streak = 0;
  for (let i = all.length - 1; i >= 0; i--) {
    const d = all[i];
    if (d.date > today) continue;
    if (sameDay(d.date, today)) continue;            // today is not over yet
    if (!d.rec) break;                               // an untouched day breaks it
    const pct = dayCompletion(d.date, d.rec, tasks);
    if (pct && pct > 0) streak++; else break;
  }

  const pending = (settings.redemptions || []).filter(r => r.status === 'Pending');
  return {
    start, stop,
    childName: settings.childName || 'your child',
    average: counted ? Math.round(sum / counted) : 0,
    perfect, ticks, streak, daysCounted: counted,
    homework: hasHomework ? { done: hwDone, late: hwLate, missed: hwMissed } : null,
    pending: pending.map(r => ({ id: r.id, name: r.name, cost: r.cost })),
    /* A week with nothing in it means something is wrong, not that the child
       had a bad week: say nothing rather than send a scoreboard of zeros. */
    worthSending: counted > 0 || pending.length > 0
  };
}

/** Split one account's rows into a child each: settings row plus month rows.
    Rows from before children existed carry no child_id; they are the one
    child that account always had. */
export function groupByChild(rows) {
  const byChild = new Map();
  for (const r of rows || []) {
    const key = r.child_id || 'legacy';
    if (!byChild.has(key)) byChild.set(key, { childId: r.child_id || null, settings: null, months: [] });
    const c = byChild.get(key);
    if (r.month_key === SETTINGS_ROW) c.settings = readSettings(r.tracker_data || {});
    else c.months.push(r);
  }
  // a child with no settings row has never synced: nothing to report on
  return [...byChild.values()].filter(c => c.settings);
}

/** Claims the parent has not been told about yet. */
export function newClaims(settings, alreadyTold) {
  const told = new Set(alreadyTold || []);
  return (settings.redemptions || [])
    .filter(r => r.status === 'Pending' && r.id && !told.has(String(r.id)))
    .map(r => ({ id: String(r.id), name: r.name, cost: r.cost }));
}

/** Deadlines that passed yesterday with the task still not done. */
export function missedYesterday(rows, settings, today) {
  if (!settings.deadlines || !settings.deadlines.enabled) return null;
  const tasks = settings.tasks || [];
  const y = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1);
  const day = daysFromRows(rows).find(d => sameDay(d.date, y));
  if (!day) return null;
  if (day.rec && day.rec.excused) return null;       // the parent already excused it
  const school = isSchoolDay(y);
  const weekend = y.getDay() === 0 || y.getDay() === 6;
  const ticks = (day.rec && day.rec.tasks) || {};
  const late = (day.rec && day.rec.late) || {};
  const missed = [], lateOnes = [];
  tasks.forEach(t => {
    if (t.schoolOnly && !school) return;
    if (t.weekendOnly && !weekend) return;
    if (!ticks[t.id]) missed.push(t.name);
    else if (late[t.id]) lateOnes.push(t.name);
  });
  if (!missed.length && !lateOnes.length) return null;
  return { date: y, missed, late: lateOnes, childName: settings.childName || 'your child' };
}
