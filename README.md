# Steam games recommender
Project designed to study how to create recommendation systems.

This repository currently contains a **Steam games recommender** built on the `steam-200k` dataset (implicit feedback).

## Steam games recommender (steam-200k)

### Objective

Given a user id from the dataset, the CLI can:

- **Show the most popular games** (baseline).
- **Recommend games for a specific user** using either:
  - **Popularity** (global baseline, excluding already-owned games)
  - **Item-based Collaborative Filtering (ItemCF)** (personalized), with popularity fallback.

The focus is on a small, readable codebase showing the end-to-end flow:

- **Load dataset**
- **Convert raw events to implicit interactions**
- **Index users/items**
- **Build sparse user-item matrix**
- **Generate recommendations**

### Dataset brief (how to read “what the user likes”)

This dataset does not contain explicit ratings (like 1–5 stars). Instead it logs **implicit feedback**:

- **`purchase`**: the user bought the game (strong positive signal)
- **`play`**: the user played the game for some number of hours (positive signal that grows with hours)

In this project, a user “likes” a game when they **purchased it and/or played it**. These events are converted into a single numeric **interaction weight** per `(user, game)` (purchases + a log-scaled version of playtime).

### Project structure

Relevant files:

- **`src/steamrec/__main__.py`**
  - Module entrypoint so you can run `python -m steamrec ...`.
- **`src/steamrec/cli.py`**
  - CLI definition (`top`, `recommend`) and orchestration of the full flow.
- **`src/steamrec/data.py`**
  - Dataset loading and preprocessing helpers.
  - Builds a sparse matrix representation for recommenders.
- **`src/steamrec/recommenders.py`**
  - Recommendation algorithms (Popularity, ItemCF) and shared `Recommendation` type.

### Data model (what the code expects)

The `steam-200k.csv` dataset is loaded with these columns:

- **`user_id`**: integer id
- **`game`**: game title (string)
- **`behavior`**: `purchase` or `play`
- **`value`**:
  - for `purchase`: usually `1`
  - for `play`: hours played

The code converts these events into an **implicit interaction weight** per `(user_id, game)`:

- purchases contribute `purchase_weight`
- plays contribute `log1p(hours_played_clipped) * play_weight`

Then interactions are aggregated by `(user_id, game)`.

### Recommendation methods (high level)

- **Popularity**
  - Recommends the globally most interacted-with games (highest total interaction weight across all users).
  - When recommending for a user, it excludes games the user already owns.
  - Useful as a simple baseline.

- **Item-based Collaborative Filtering (ItemCF)**
  - Builds a sparse user-item matrix from the interaction weights.
  - Finds games similar to the ones the user already interacted with.
  - Scores candidate games by how similar they are to the user’s “profile” (the set of owned/played games).
  - Excludes already-owned games.
  - If not enough personalized results are found, the CLI fills the remaining slots with the popularity baseline.

### Setup
```bash
python -m pip install -r requirements.txt
```

### Dataset

The dataset file is expected at `dataset/steam-200k.csv`.

You can override it with `--dataset /path/to/steam-200k.csv`.

### Run
```bash
PYTHONPATH=src python -m steamrec top --n 10
PYTHONPATH=src python -m steamrec recommend --user-id 151603712 --n 10 --method itemcf
PYTHONPATH=src python -m steamrec recommend --user-id 151603712 --n 10 --method popularity
```

### How it works (end-to-end flow)

When you run `python -m steamrec ...`, the following happens:

1. **CLI parsing** (`steamrec/cli.py`)
   - Reads `--dataset` and the selected command (`top` or `recommend`).
2. **Load raw CSV** (`load_steam_200k_csv` in `steamrec/data.py`)
   - Validates the file exists.
   - Ensures `behavior` contains only `purchase` and `play`.
3. **Build implicit interactions** (`build_implicit_interactions`)
   - Converts raw events to a clean DataFrame with:
     - `user_id` (int)
     - `game` (str)
     - `weight` (float)
4. **If `top` command**
   - Uses `PopularityRecommender` to rank games by total interaction weight.
5. **If `recommend` command**
   - Indexes users and games (`index_dataset`).
   - Builds a CSR sparse matrix (`build_user_item_matrix`) with shape:
     - `(num_users, num_games)`
   - Selects a recommendation strategy:
     - **Popularity**: returns global top games excluding already-owned items.
     - **ItemCF**:
       - Computes an item-to-item similarity implicitly by normalizing the item-user matrix.
       - Scores items for the user by propagating from the user's interacted items.
       - Excludes already-owned items.
       - If fewer than `n` items are produced (e.g. sparse user), fills with popularity.

### CLI reference

All commands accept:

- **`--dataset`**: path to `steam-200k.csv` (default: `dataset/steam-200k.csv`)

Commands:

- **`top`**
  - **`--n`**: number of games to list (default: `20`)
- **`recommend`**
  - **`--user-id`**: user id from the dataset (required)
  - **`--n`**: number of recommendations (default: `10`)
  - **`--method`**: `itemcf` (default) or `popularity`

If you pass an unknown `--user-id`, the CLI prints a few valid ids from the dataset to help you pick one.
