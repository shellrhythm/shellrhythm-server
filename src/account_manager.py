import sqlite3
from time import time_ns
from secrets import token_hex
from bcrypt import checkpw
from random import randrange

allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

class UserSession:
    user_id:int
    expires_at:int

    def __init__(self, user_id:int = -1, expires_at = -1):
        self.user_id = user_id
        self.expires_at = expires_at

class AccountManager:
    con = sqlite3.connect("charts.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    logged_in_users:dict[str, UserSession] = {}

    def create_account(self, username, password):
        discrim = 0
        homonyms = self.cur.execute("SELECT discriminator FROM users WHERE username=?",
            (username,)).fetchall()
        if username and len(username) >= 2 and allowed.issuperset(username): #valid username
            if len(homonyms) > 0 and len(homonyms) < (16**4):
                while discrim in homonyms:
                    discrim = randrange(0, 16**4)
            if len(homonyms) >= (16**4):
                return (False, "name_too_common")
            self.cur.execute(
                "INSERT INTO users (username, discriminator, password) VALUES (?, ?, ?)",
                (username, discrim, password)
            )
            self.con.commit()
            return (True, "successful")
        return (False, "invalid_name")

    def login(self, username:str, password:str):
        userdata:list = username.split("#")
        if len(userdata) == 1:
            userdata.append("0")
        user = self.cur.execute("SELECT * FROM users WHERE username=? AND discriminator=? ",
                                (userdata[0], int(userdata[1], base=16))).fetchone()
        if user is None:
            return (False, "user_doesnt_exist")
        if checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            # ok we good, log the guy in
            token = token_hex(32) # have your token good sir, don't share it
            loggedin_data = [usr.user_id for usr in self.logged_in_users]
            log_time = time_ns()
            if user["id"] in loggedin_data:
                del loggedin_data[loggedin_data.index(user["id"])]
            self.logged_in_users[token] = UserSession(user["id"], log_time + 6*3600*(10**9))
            return (True, user["id"], token)
        return (False, "wrong_password")

    def refresh_token(self, token) -> str|bool:
        try:
            session = [user.auth_token for user in self.logged_in_users].index(token)
            new_token = token_hex(64)
            self.logged_in_users[session].auth_token = new_token
            self.logged_in_users[session].expires_at = time_ns() + 6*3600*(10**9)
            return new_token
        except ValueError:
            return False

    def get_user_id_from_token(self, token) -> int:
        session = [user.auth_token for user in self.logged_in_users].index(token)
        return session
