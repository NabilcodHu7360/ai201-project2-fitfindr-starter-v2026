# Acceptance Criteria

## 1. Matching query

A matching query completes all three tools and returns a fit card in at least
4 of 5 tries.

**Why:** Keyword search may miss one unusual phrasing.

## 2. Impossible query

A query with no matches stops before `suggest_outfit` and names something the
user can change in 5 of 5 tries.

**Why:** The empty-list branch is deterministic and should always stop.

## 3. Session state

In 5 of 5 matching runs, the listing ID passed to `suggest_outfit` equals
`session["selected_item"]["id"]`.

**Why:** The selected search result must reach the next tool without re-entry.

## 4. Fit card

At least 4 of 5 fit cards contain 2–4 sentences and mention the selected item's
name, price, and platform.

**Why:** Wording may vary, but the important listing facts must remain.

## 5. Search filters

For 5 of 5 queries with a size and maximum price, every result matches the size
and stays at or below the price.

**Why:** Wrong-size or unaffordable results are unusable.
