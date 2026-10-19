# FitFindr

## What This Does

FitFindr searches thrift listings, selects a match, suggests an outfit from a
saved wardrobe, and writes a short caption.

## Tool Inventory

- `search_listings(description, size, max_price)` returns matching listings.
- `suggest_outfit(new_item, wardrobe)` returns an outfit suggestion.
- `create_fit_card(outfit, new_item)` returns a 2–4 sentence caption.

Each tool returns an empty-result explanation when it cannot continue.

## Planning Loop

`agent.py::run_agent` parses the request, searches through MCP, selects the
first result, suggests an outfit, and creates a fit card. If search returns
nothing, it gives a useful message and stops.

## Sample Run

```text
$ python app.py ask "vintage graphic tee under $30"
Found: Y2K Baby Tee — Butterfly Print — $18.00 on depop
Outfit: Baggy jeans, a black crossbody bag, and white sneakers.
Fit card: Y2K Baby Tee — Butterfly Print — $18.00 on depop. Easy Y2K style.
```

```text
$ python app.py ask "designer ballgown size XXS under $5"
No matching listings were found. Try a larger size range, a higher price
limit, or fewer description words.
```

## How I Used AI

AI drafted the search ranking; I increased the weight of titles and tags after
a mesh top ranked too high. AI drafted the caption prompt; I required the exact
item title, price, and platform after it changed those details.

## Run Log — Before

Full evidence: `results/run_2026-10-11_2246_before.md`.

| Criterion | Target | Result | Verdict |
|---|---:|---:|---|
| Complete all three tools | 4/5 | 5/5 | MET |
| Stop after empty search | 5/5 | 5/5 | MET |
| Preserve selected item | 5/5 | 5/5 | MET |
| Short caption with details | 4/5 | 5/5 | MET |
| Respect size and price | 5/5 | 5/5 | MET |

## Verdicts and Diagnoses

All criteria passed. The selected item was preserved, but the before trace did
not print both IDs, making that result harder to verify directly.

## Loop Trace

```text
1. search_listings via MCP → selected lst_004
2. suggest_outfit → item_id=lst_004; selected_item_id=lst_004
3. create_fit_card → caption created
```

## The Improvement

I added `outfit_item_id` to the session and printed both item IDs. The after
run (`results/run_2026-10-11_2250_after.md`) still passed every criterion 5/5
and now proves the IDs match.

## What's Still Broken

Keyword search may miss unusual paraphrases. More varied search tests would be
the next improvement.
