#!/bin/sh
# Rebuilds run-all.sql from the real scripts, in order.
#
# run-all.sql is generated, never edited by hand — edit the numbered scripts
# and run this. Keeping it generated is the point: a hand-maintained copy
# drifts from the originals and then nobody knows which one is true.

set -e
cd "$(dirname "$0")/.."
OUT=supabase/run-all.sql

{
  cat <<'HEADER'
-- ============================================================================
-- EVERYTHING, IN ORDER. Paste this whole file into the Supabase SQL editor.
--
-- GENERATED FILE — do not edit. Run supabase/build-run-all.sh to rebuild it
-- after changing any of the scripts below.
--
-- Safe to run as many times as you like: every statement in here either
-- creates something that is not there or replaces what is. So if it fails
-- part-way, fix the cause and run the whole thing again — the Supabase SQL
-- editor does not roll a script back, so a half-finished run is normal and
-- re-running is always the right answer.
--
-- One timing note, the only one that matters: this changes the key that the
-- tracker syncs against, so a browser with the app ALREADY OPEN cannot save
-- to the cloud until it is reloaded. Nothing is lost — it keeps working on
-- the device and retries. Run it when nobody is mid-routine, not at 7am.
--
-- Afterwards, run 00-where-am-i.sql to confirm.
-- ============================================================================

HEADER

  for f in Supabase_Setup.sql supabase-profiles.sql \
           supabase/01-emails.sql supabase/02-household.sql supabase/03-children.sql; do
    echo ""
    echo "-- ############################################################################"
    echo "-- ## $f"
    echo "-- ############################################################################"
    echo ""
    cat "$f"
  done
} > "$OUT"

echo "wrote $OUT ($(wc -l < "$OUT" | tr -d ' ') lines)"
