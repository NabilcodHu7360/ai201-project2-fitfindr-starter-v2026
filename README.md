# FitFindr

## What This Does

FitFindr searches thrift listings from a plain-language request. It selects a
match, suggests an outfit from the user's wardrobe collection, and creates a
short caption.

## Tool Inventory

- **`search_listings`:** Inputs are `description` (`str`), `size`
  (`str | None`), and `max_price` (`float | None`). It returns up to 10 ranked
  listing dictionaries or `[]` when nothing matches.
- **`suggest_outfit`:** Inputs are `new_item` (`dict`) and `wardrobe` (`dict`).
  It returns an outfit suggestion, or general advice for an empty wardrobe.
- **`create_fit_card`:** Inputs are `outfit` (`str`) and `new_item` (`dict`). It
  returns a 2–4 sentence caption, or an explanation when the outfit is blank.

## Planning Loop

If search returns nothing, the loop saves a message suggesting changes and
stops. Otherwise it selects the first result, suggests an outfit, and creates
the fit card. This is implemented in `agent.py::run_agent`.

Regex extracts size and price. State moves through `parsed`, `search_results`,
`selected_item`, `outfit_suggestion`, and `fit_card`.

## Sample Run

```text
$ python app.py ask 'vintage graphic tee under $30'

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
Outfit: Pair the Y2K baby tee with the baggy straight-leg jeans, black
crossbody bag, and chunky white sneakers for a casual streetwear look.
Alternatively, style it with the wide-leg khaki trousers, brown leather belt,
and chunky white sneakers for an earth-toned outfit.
Fit card: Y2K Baby Tee — Butterfly Print — $18.00 on depop. Easy streetwear
energy with a nostalgic nod to the early 2000s.
```

```text
$ python app.py ask 'designer ballgown size XXS under $5'

No matching listings were found. Try a larger size range, a higher price
limit, or fewer description words.
```

The three tools were also tested separately:

```text
$ python -c "from tools import search_listings; print(len(search_listings('graphic tee', max_price=30)))"
3
```

```text
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[1], get_example_wardrobe()))"
Pair the Y2K baby tee with the baggy straight-leg jeans, black crossbody bag,
and chunky white sneakers for a casual streetwear look. Alternatively, style
the Y2K baby tee with the wide-leg khaki trousers, brown leather belt, and
chunky white sneakers for an earth-toned outfit.
```

```text
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Baggy jeans and white sneakers.', load_listings()[1]))"
Y2K Baby Tee — Butterfly Print — $18.00 on depop. Nothing beats the effortless,
zero-effort cool of broken-in denim and crisp white kicks.
```

## How I Used AI

AI helped draft the search, but a mesh top ranked too high, so I weighted titles
and tags more than descriptions. AI also drafted the caption prompt, but it
changed the item title, so I added the exact title, price, and platform in code.
For Unit 4, AI helped compare the traces; I kept the change that exposes both
item IDs so the state transfer is easy to verify.

## Run Log — Before

The full run is in `results/run_2026-10-11_2246_before.md`.

| Criterion | Target | Result | Verdict |
|---|---:|---:|---|
| Complete all three tools | 4/5 | 5/5 | MET |
| Stop after an empty search | 5/5 | 5/5 | MET |
| Pass the selected item to outfit tool | 5/5 | 5/5 | MET |
| Short caption with key details | 4/5 | 5/5 | MET |
| Respect size and price filters | 5/5 | 5/5 | MET |

Evidence included a complete Y2K tee fit card, five useful no-match messages,
the same track-jacket selection in every state-transfer run, five two-sentence
denim-jacket captions, and only the US 8, $48 sneaker for the filter test.

## Verdicts and Diagnoses

All five criteria were met. Criteria 1 and 4 exceeded their 4/5 targets. The
state transfer in criterion 3 worked, but the before trace did not print the
two IDs being compared, so that result was harder to check directly.

## Loop Trace

`search_listings` is registered in `mcp_server.py`, and the loop calls it
through `mcp_client.call_tool`. Its `list[dict]` result and search behavior stay
the same.

```text
[1] search_listings (via MCP)
    in:  description='90s track jacket'; size='M'; max_price=50.0
    out: 1 items; selected lst_004; branch=match
[2] suggest_outfit
    in:  item_id=lst_004; selected_item_id=lst_004; wardrobe_items=10
    out: outfit suggestion created
[3] create_fit_card
    in:  selected item and outfit suggestion
    out: two-sentence fit card created
```

An impossible search ends after step 1 and returns a message suggesting a
larger size range, higher price, or fewer description words.

## The Improvement

I added `outfit_item_id` to the session and printed it beside
`selected_item_id` in the trace. This makes criterion 3 directly observable.
The after run in `results/run_2026-10-11_2250_after.md` still passed every
criterion 5/5, and all five state-transfer traces now show matching IDs.

## What's Still Broken

The five fixed scenarios pass, but keyword search may still miss unusual
paraphrases. I stopped after one improvement as required; with more time I
would test more ways of describing the same clothing item.

See [RUNNING.md](RUNNING.md) for commands.
