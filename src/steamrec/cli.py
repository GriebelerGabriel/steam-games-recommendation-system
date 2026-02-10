from __future__ import annotations

import argparse
from pathlib import Path

from steamrec.data import (
    build_implicit_interactions,
    build_user_item_matrix,
    index_dataset,
    load_steam_200k_csv,
)
from steamrec.recommenders import ItemCFRecommender, PopularityRecommender


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="steamrec")
    p.add_argument(
        "--dataset",
        default="dataset/steam-200k.csv",
        help="Path to steam-200k.csv",
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    top = sub.add_parser("top", help="Show top games by popularity")
    top.add_argument("--n", type=int, default=20)

    rec = sub.add_parser("recommend", help="Recommend games for a user")
    rec.add_argument("--user-id", type=int, required=True)
    rec.add_argument("--n", type=int, default=10)
    rec.add_argument(
        "--method",
        choices=["popularity", "itemcf"],
        default="itemcf",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    raw = load_steam_200k_csv(Path(args.dataset))
    interactions = build_implicit_interactions(raw)

    if args.cmd == "top":
        pop = PopularityRecommender(interactions)
        recs = pop.recommend(n=args.n)
        for i, r in enumerate(recs, start=1):
            print(f"{i:02d}. {r.title}  score={r.score:.3f}")
        return 0

    ds = index_dataset(interactions)

    if args.user_id not in ds.user_index:
        print(
            f"Unknown user_id={args.user_id}. "
            f"Try one of: {ds.user_ids[:10].tolist()} ..."
        )
        return 2

    user_item = build_user_item_matrix(ds)

    user_idx = ds.user_index[args.user_id]
    owned_items = user_item.getrow(user_idx).indices
    owned_titles = {str(ds.game_titles[i]) for i in owned_items}

    if args.method == "popularity":
        pop = PopularityRecommender(interactions)
        recs = pop.recommend(n=args.n, exclude=owned_titles)
    else:
        model = ItemCFRecommender(user_item=user_item, game_titles=ds.game_titles)
        recs = model.recommend_for_user(user_idx, n=args.n)

        if len(recs) < args.n:
            pop = PopularityRecommender(interactions)
            fill = pop.recommend(n=args.n - len(recs), exclude=owned_titles | {r.title for r in recs})
            recs = recs + fill

    print(f"User {args.user_id} owns {len(owned_titles)} games")
    for i, r in enumerate(recs, start=1):
        print(f"{i:02d}. {r.title}  score={r.score:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
