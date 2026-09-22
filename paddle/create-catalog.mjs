#!/usr/bin/env node
/**
 * Create the Unprompted product catalogue in Paddle.
 *
 *   node paddle/create-catalog.mjs                 # dry run: prints what it would create
 *   PADDLE_API_KEY=pdl_sdbx_... node paddle/create-catalog.mjs --apply
 *   PADDLE_API_KEY=pdl_live_... node paddle/create-catalog.mjs --apply --live
 *
 * Nothing is written without --apply, and writing to a live key also needs --live,
 * so a mistyped command cannot create real products.
 *
 * Amounts are in the lowest denomination, as strings: $3.99 is "399".
 */

const API = 'https://api.paddle.com';
const args = new Set(process.argv.slice(2));
const APPLY = args.has('--apply');
const LIVE_OK = args.has('--live');
const KEY = process.env.PADDLE_API_KEY || '';

/* ---------------------------------------------------------------- catalogue
   Two plans, matching what the sales page sells today. Edit the amounts here;
   everything else follows.

   USD only, charged worldwide in USD — no country overrides. The first families
   are in Barbados and the US, and Paddle cannot charge in BBD in any case, so a
   Caribbean parent pays the same dollar price as an American one. Add
   unit_price_overrides later if a market earns it.   */
const TAX_CATEGORY = 'saas';          // software sold as a subscription

/* A trial set here is a PADDLE-run trial, which takes a card up front.
   Leave it null to run the 15 free days in your own database instead — see the
   notes at the bottom of this file. */
const PADDLE_TRIAL = null;            // or: { interval: 'day', frequency: 15 }

const CATALOG = [
  {
    key: 'standard',
    name: 'Unprompted Standard',
    description: 'Daily routine, timetable, points and rewards for one child, with automatic backup.',
    prices: [
      {
        key: 'standardMonthly',
        name: 'Standard monthly',
        description: 'Standard, billed monthly',
        billing_cycle: { interval: 'month', frequency: 1 },
        unit_price: { amount: '399', currency_code: 'USD' },      // $3.99
      },
      {
        key: 'standardYearly',
        name: 'Standard yearly',
        description: 'Standard, billed yearly — about two months free',
        billing_cycle: { interval: 'year', frequency: 1 },
        unit_price: { amount: '3900', currency_code: 'USD' },     // $39.00
      }
    ]
  },
  {
    key: 'pro',
    name: 'Unprompted Pro',
    description: 'Everything in Standard for up to four children, with a second parent login and weekly email reports.',
    prices: [
      {
        key: 'proMonthly',
        name: 'Pro monthly',
        description: 'Pro, billed monthly',
        billing_cycle: { interval: 'month', frequency: 1 },
        unit_price: { amount: '699', currency_code: 'USD' },      // $6.99
      },
      {
        key: 'proYearly',
        name: 'Pro yearly',
        description: 'Pro, billed yearly — about two months free',
        billing_cycle: { interval: 'year', frequency: 1 },
        unit_price: { amount: '6900', currency_code: 'USD' },     // $69.00
      }
    ]
  }
];

/* ---------------------------------------------------------------- helpers */
const money = (amount, code) => {
  const zeroDecimal = ['JPY', 'KRW', 'CLP', 'ISK', 'HUF', 'TWD'];
  const n = zeroDecimal.includes(code) ? Number(amount) : Number(amount) / 100;
  return `${code} ${n.toFixed(zeroDecimal.includes(code) ? 0 : 2)}`;
};

async function paddle(path, method = 'GET', body) {
  const res = await fetch(API + path, {
    method,
    headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = json.error || {};
    throw new Error(`${method} ${path} → ${res.status} ${err.code || ''} ${err.detail || JSON.stringify(json)}`);
  }
  return json.data;
}

function priceBody(productId, p) {
  const body = {
    product_id: productId,
    name: p.name,
    description: p.description,
    billing_cycle: p.billing_cycle,
    unit_price: p.unit_price,
    tax_mode: 'account_setting',
    quantity: { minimum: 1, maximum: 1 }          // one subscription per family
  };
  if (p.overrides?.length) {
    body.unit_price_overrides = p.overrides.map(o => ({
      country_codes: o.country_codes,
      unit_price: { amount: o.amount, currency_code: o.currency_code }
    }));
  }
  if (PADDLE_TRIAL) body.trial_period = PADDLE_TRIAL;
  return body;
}

function printPlan() {
  console.log('\nCatalogue to create\n' + '─'.repeat(72));
  for (const product of CATALOG) {
    console.log(`\n▸ ${product.name}   [tax category: ${TAX_CATEGORY}]`);
    console.log(`  ${product.description}`);
    for (const p of product.prices) {
      const cycle = `${p.billing_cycle.frequency} ${p.billing_cycle.interval}`;
      console.log(`   · ${p.name.padEnd(18)} ${money(p.unit_price.amount, p.unit_price.currency_code).padEnd(12)} every ${cycle}`
        + (PADDLE_TRIAL ? `  (+${PADDLE_TRIAL.frequency}-${PADDLE_TRIAL.interval} trial, card up front)` : ''));
      for (const o of p.overrides || []) {
        console.log(`       ${o.country_codes.join(', ').padEnd(6)} → ${money(o.amount, o.currency_code)}`);
      }
    }
  }
  console.log('\n' + '─'.repeat(72));
}

/* ---------------------------------------------------------------- run */
async function main() {
  printPlan();

  if (!APPLY) {
    console.log('\nDry run — nothing was created.');
    console.log('To create it:  PADDLE_API_KEY=... node paddle/create-catalog.mjs --apply');
    console.log('Live keys also need --live.\n');
    return;
  }
  if (!KEY) throw new Error('Set PADDLE_API_KEY first.');
  const isLive = KEY.startsWith('pdl_live_');
  if (isLive && !LIVE_OK) {
    throw new Error('That is a LIVE key. Re-run with --live if you really mean to create live products.');
  }
  console.log(`\nWriting to the ${isLive ? 'LIVE' : 'sandbox'} account…\n`);

  // Paddle has no "create or update", so refuse to make a second copy of a product
  const existing = await paddle('/products?status=active&per_page=200');
  const clash = CATALOG.filter(c => existing.some(e => e.name === c.name));
  if (clash.length) {
    throw new Error(`Already in this account: ${clash.map(c => c.name).join(', ')}. `
      + 'Archive or rename them first — running this twice would create duplicates.');
  }

  const made = { products: [], prices: {} };
  for (const product of CATALOG) {
    const created = await paddle('/products', 'POST', {
      name: product.name,
      description: product.description,
      tax_category: TAX_CATEGORY,
      type: 'standard'
    });
    made.products.push({ key: product.key, id: created.id, name: created.name });
    console.log(`product  ${created.id}  ${created.name}`);

    for (const p of product.prices) {
      const price = await paddle('/prices', 'POST', priceBody(created.id, p));
      made.prices[p.key] = price.id;
      console.log(`  price  ${price.id}  ${p.name.padEnd(18)} ${money(p.unit_price.amount, p.unit_price.currency_code)}`);
    }
  }

  const { writeFileSync } = await import('node:fs');
  const out = { created_at: new Date().toISOString(), environment: isLive ? 'production' : 'sandbox', ...made };
  writeFileSync(new URL('./catalog-ids.json', import.meta.url), JSON.stringify(out, null, 2));

  console.log('\n' + '─'.repeat(72));
  console.log('Paste this into the CONFIG block in index.html:\n');
  console.log(`      priceIds: {
        standardMonthly: '${made.prices.standardMonthly}',
        standardYearly:  '${made.prices.standardYearly}',
        proMonthly:      '${made.prices.proMonthly}',
        proYearly:       '${made.prices.proYearly}'
      }`);
  console.log(`\n      environment: '${isLive ? 'production' : 'sandbox'}'`);
  console.log('\nIDs also written to paddle/catalog-ids.json\n');
}

main().catch(e => { console.error('\n✗ ' + e.message + '\n'); process.exit(1); });

/* ---------------------------------------------------------------- notes

   ON THE TRIAL
   The sales page, the FAQ and the sign-up screen all promise 15 days. If you
   set a trial here, set 15 — not the 7 in the template you pasted — or the
   site is lying to the customer at the moment they hand over a card.

   A Paddle trial takes a payment method up front. Paddle does have cardless
   trials, but they are in developer preview and cannot be created through
   Paddle Checkout, which is what the sales page uses — they need a transaction
   created through the API instead. So the realistic choice is:

     a) Paddle runs the trial, card up front. Set PADDLE_TRIAL above.
        Paddle handles the reminder emails and the charge on day 16.

     b) You run the trial, no card. Leave PADDLE_TRIAL null: these prices are
        then just the subscription price, and the 15 free days live in your own
        subscriptions table. Checkout only happens when a family decides to pay.

   (b) is the plan of record and the lower-friction option for a family app,
   but it is more code: your own trial clock, your own paywall, your own
   reminder emails.
*/
