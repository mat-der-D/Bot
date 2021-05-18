import os
from typing import NamedTuple, Optional
import psycopg2

DATABASE_URL = os.environ["DATABASE_URL"]


class ScoreTuple(NamedTuple):
    win: int
    lose: int
    win_hard: Optional[int]
    lose_hard: Optional[int]


def get_score(user_id: str) -> ScoreTuple:
    q = (
        f"SELECT i_win, i_lose, i_win_hard, i_lose_hard "
        f"  FROM score "
        f" WHERE s_user_id='{user_id}'"
    )
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
            score_list = cur.fetchall()
    if len(score_list) > 1:
        raise Exception(f"score for user_id={user_id} is duplicated")
    if len(score_list) == 0:
        return ScoreTuple(0, 0, None, None)
    return ScoreTuple(*score_list[0])


def update_score(user_id: str, win: int, lose: int, win_hard: Optional[int], lose_hard: Optional[int]):
    def to_null(x):
        if x is None:
            return "NULL"
        return x

    win_hard = to_null(win_hard)
    lose_hard = to_null(lose_hard)
    q = (
        f"DELETE FROM score WHERE s_user_id='{user_id}';"
        f"INSERT INTO score VALUES ('{user_id}', {win}, {lose}, {win_hard}, {lose_hard}) "
    )
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
        conn.commit()


def clear_score(user_id: str):
    q = f"DELETE FROM score WHERE s_user_id='{user_id}'"
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(q)
        conn.commit()
