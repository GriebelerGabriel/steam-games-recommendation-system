from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse


@dataclass(frozen=True)
class Steam200kDataset:
    interactions: pd.DataFrame
    user_ids: np.ndarray
    game_titles: np.ndarray
    user_index: dict[int, int]
    game_index: dict[str, int]


def load_steam_200k_csv(csv_path: str | Path) -> pd.DataFrame:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {path}")

    df = pd.read_csv(
        path,
        header=None,
        names=["user_id", "game", "behavior", "value", "extra"],
    )

    expected_behaviors = {"purchase", "play"}
    unknown = set(df["behavior"].unique()) - expected_behaviors
    if unknown:
        raise ValueError(f"Unexpected behavior types: {sorted(unknown)}")

    return df


def build_implicit_interactions(
    raw: pd.DataFrame,
    *,
    purchase_weight: float = 1.0,
    play_weight: float = 1.0,
    min_play_hours: float = 0.1,
) -> pd.DataFrame:
    df = raw[["user_id", "game", "behavior", "value"]].copy()

    is_purchase = df["behavior"] == "purchase"
    is_play = df["behavior"] == "play"

    weights = np.zeros(len(df), dtype=np.float32)
    weights[is_purchase.to_numpy()] = purchase_weight

    play_hours = df.loc[is_play, "value"].astype(float)
    play_hours = play_hours.clip(lower=min_play_hours)
    weights[is_play.to_numpy()] = (np.log1p(play_hours.to_numpy()) * play_weight).astype(
        np.float32
    )

    interactions = pd.DataFrame(
        {
            "user_id": df["user_id"].astype(int),
            "game": df["game"].astype(str),
            "weight": weights,
        }
    )

    interactions = (
        interactions.groupby(["user_id", "game"], as_index=False)["weight"].sum()
    )
    interactions = interactions[interactions["weight"] > 0]
    return interactions


def index_dataset(interactions: pd.DataFrame) -> Steam200kDataset:
    user_ids = np.sort(interactions["user_id"].unique())
    game_titles = np.sort(interactions["game"].unique())

    user_index = {int(uid): int(i) for i, uid in enumerate(user_ids)}
    game_index = {str(g): int(i) for i, g in enumerate(game_titles)}

    return Steam200kDataset(
        interactions=interactions,
        user_ids=user_ids,
        game_titles=game_titles,
        user_index=user_index,
        game_index=game_index,
    )


def build_user_item_matrix(ds: Steam200kDataset) -> sparse.csr_matrix:
    users = ds.interactions["user_id"].map(ds.user_index).to_numpy(dtype=np.int32)
    items = ds.interactions["game"].map(ds.game_index).to_numpy(dtype=np.int32)
    data = ds.interactions["weight"].to_numpy(dtype=np.float32)

    mat = sparse.csr_matrix(
        (data, (users, items)),
        shape=(len(ds.user_ids), len(ds.game_titles)),
        dtype=np.float32,
    )
    return mat
