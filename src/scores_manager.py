import json
import sqlite3
from time import time_ns
from enum import IntEnum

class Rank(IntEnum):
    P = 6 # @
    S = 5
    A = 4
    B = 3
    C = 2
    D = 1
    F = 0
    X = -1

class Score(dict):
    @property
    def chart_id(self) -> int:
        return self["chart_id"]
    @chart_id.setter
    def chart_id(self, value:int):
        self["chart_id"] = value

    @property
    def user_id(self) -> int:
        return self["user_id"]
    @user_id.setter
    def user_id(self, value:int):
        self["user_id"] = value

    @property
    def rank(self) -> int:
        return self["rank"]
    @rank.setter
    def rank(self, value:int):
        self["rank"] = value

    @property
    def score(self) -> int:
        return self["score"]
    @score.setter
    def score(self, value:int):
        self["score"] = value

    @property
    def accuracy(self) -> float:
        return self["accuracy"]
    @accuracy.setter
    def accuracy(self, value:float):
        self["accuracy"] = value

    @property
    def judgements(self) -> list:
        return self["judgements"]
    @judgements.setter
    def judgements(self, value:list):
        self["judgements"] = value

class ScoresManager:
    con = sqlite3.connect("charts.db")
    cur = con.cursor()

    def post_score(self, score_object:Score, poster_id:int):
        output = {"success": True}
        if poster_id != score_object.user_id:
            return {"success": False, "error": "wrong_user"}
        self.cur.execute("INSERT INTO scores (chart_id, user_id, rank, "+\
            "score, accuracy, judgements, upload_time) VALUES (?,?,?,?,?,?,?)", (
                score_object.chart_id, poster_id, int(score_object.rank),
                score_object.score, score_object.accuracy,
                json.dumps(score_object.judgements), time_ns()
            ))
        output["score_id"] = self.cur.lastrowid
        self.con.commit()
        return output

    def get_score(self, score_id:int):
        scores = self.cur.execute("SELECT * FROM scores WHERE id=?", (score_id,)).fetchone()
        return scores

    def get_chart_scores(self, chart_id:int = 0):
        scores = self.cur.execute("SELECT * FROM scores WHERE chart_id=?", (chart_id,)).fetchall()
        return scores

    def get_user_scores(self, user_id:int = 0):
        scores = self.cur.execute("SELECT * FROM scores WHERE user_id=?", (user_id,)).fetchall()
        return scores
