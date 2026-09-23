# Prompt to hand Paddle

Paste one of these. **A** matches the plan of record (you run the 15 free days,
no card up front). **B** hands the trial to Paddle, which means a card up front.
Pick one — don't paste both.

---

## A — no Paddle trial (recommended)

```
Create my product catalog in my Paddle live account.

I sell a subscription web app for families called UPNXT: a daily routine,
homework and timetable tracker that a parent sets up for their child.

Create two products, tax category "saas", each with a monthly and an annual
price:

- UPNXT Standard — one child
  Monthly: USD 3.99   (amount "399")
  Annual:  USD 39.00  (amount "3900")

- UPNXT Pro — up to four children, second parent login, weekly email reports
  Monthly: USD 6.99   (amount "699")
  Annual:  USD 69.00  (amount "6900")

Do not add a trial period to any price. The 15-day free trial is handled in my
own database, and customers only reach Paddle checkout when they decide to pay.

Notes:
- USD only. Do not create country price overrides or any other currency —
  everyone is charged in USD for now.
- Paddle amounts are in the lowest denomination as strings: USD 3.99 is "399",
  not "3.99" and not "399.00".
- One product per plan, with both of its prices attached to it.
- Set quantity minimum 1 and maximum 1 on every price: a family buys one
  subscription, not a number of seats.
- Set tax_mode to "account_setting" so my account's tax handling applies.
- Give each price a clear internal description, e.g. "Standard, billed monthly".

When you are done, list every product and price you created with its Paddle ID,
as a table, so I can map them into my checkout config.
```

---

## B — Paddle runs a 15-day trial, card up front

Same as A, but replace the trial paragraph with:

```
Add a 15-day free trial to all four prices (trial_period: interval "day",
frequency 15). The customer enters a card at sign-up and is charged
automatically when the trial ends.
```

**Fifteen days, not seven.** The sales page, the FAQ and the sign-up screen all
promise 15. A 7-day trial in Paddle would contradict the site at the exact moment
someone hands over a card.

---

## What to do with the IDs you get back

Four price IDs come back, looking like `pri_01h...`. They go into the CONFIG
block near the bottom of `index.html`:

```js
billing: {
  paddleToken: 'live_...',        // Paddle > Developer tools > Authentication
  environment: 'production',      // 'sandbox' while testing
  priceIds: {
    standardMonthly: 'pri_...',
    standardYearly:  'pri_...',
    proMonthly:      'pri_...',
    proYearly:       'pri_...'
  }
}
```

The checkout code that uses them is already written and tested — those five
values are the whole switch-on.

## Before anyone can actually buy Pro

Pro's description promises a second parent login and weekly email reports.
Neither is built yet. Creating the price is fine; taking money for it is not,
until those exist or the claim comes off the page.
