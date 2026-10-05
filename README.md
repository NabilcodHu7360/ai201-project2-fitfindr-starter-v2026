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

See [RUNNING.md](RUNNING.md) for commands.
