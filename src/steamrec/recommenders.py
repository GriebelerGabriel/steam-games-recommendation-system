from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.preprocessing import normalize


@dataclass(frozen=True)
class Recommendation:
    title: str
    score: float


class PopularityRecommender:
    def __init__(self, interactions: pd.DataFrame):
        if not {"game", "weight"}.issubset(interactions.columns):
            raise ValueError("interactions must have columns: game, weight")

        pop = (
            interactions.groupby("game", as_index=False)["weight"].sum().rename(
                columns={"weight": "score"}
            )
        )
        pop = pop.sort_values("score", ascending=False, kind="mergesort")
        self._pop = pop

    def recommend(
        self,
        *,
        n: int = 10,
        exclude: set[str] | None = None,
    ) -> list[Recommendation]:
        exclude = exclude or set()
        recs: list[Recommendation] = []
        for _, row in self._pop.iterrows():
            title = str(row["game"])
            if title in exclude:
                continue
            recs.append(Recommendation(title=title, score=float(row["score"])))
            if len(recs) >= n:
                break
        return recs


class ItemCFRecommender:
    def __init__(
        self,
        user_item: sparse.csr_matrix,
        game_titles: np.ndarray,
    ):
        if not sparse.isspmatrix_csr(user_item):
            user_item = user_item.tocsr()

        self._user_item = user_item
        self._game_titles = game_titles

        item_user = user_item.T.tocsr()
        self._item_user_norm = normalize(item_user, norm="l2", axis=1, copy=True)

    def recommend_for_user(
        self,
        user_index: int,
        *,
        n: int = 10,
    ) -> list[Recommendation]:
        user_vec = self._user_item.getrow(user_index)
        if user_vec.nnz == 0:
            return []

        owned_idx = set(user_vec.indices.tolist())

        profile = user_vec
        scores = self._item_user_norm @ (self._item_user_norm.T @ profile.T)
        if sparse.issparse(scores):
            scores = scores.toarray().ravel()
        else:
            scores = np.asarray(scores).ravel()

        if owned_idx:
            scores[list(owned_idx)] = -np.inf

        top_idx = np.argpartition(-scores, kth=min(n, len(scores) - 1))[:n]
        top_idx = top_idx[np.argsort(-scores[top_idx])]

        recs: list[Recommendation] = []
        for i in top_idx:
            s = float(scores[i])
            if not np.isfinite(s):
                continue
            recs.append(Recommendation(title=str(self._game_titles[i]), score=s))
        return recs
