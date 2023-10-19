# so this is the part where i have no idea what im doing
# forgive me

import asyncio
import json
import sqlite3
import subprocess
from http.server import SimpleHTTPRequestHandler
from websockets.server import serve
from src.account_manager import AccountManager
from src.scores_manager import Score, ScoresManager
from src.charts_manager import ChartsManager

Handler = SimpleHTTPRequestHandler

FILES_PORT = 6969

acc = AccountManager()
sco = ScoresManager()
cht = ChartsManager()

con = sqlite3.connect("charts.db")
cur = con.cursor()

#region Create tables
cur.execute("""CREATE TABLE IF NOT EXISTS charts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checksum STRING NOT NULL,
    songname STRING,
    difficulty REAL,
    artist STRING,
    author STRING,
    author_id INTEGER,
    description STRING,
    filenames STRING NOT NULL,
    status INTEGER DEFAULT 0,
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME,
    chart_version INTEGER DEFAULT 0,
    chart_checksums STRING
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username STRING NOT NULL,
    discriminator INTEGER NOT NULL DEFAULT 0,
    password STRING NOT NULL,
    description STRING,
    is_bot INTEGER DEFAULT 0
)""")
cur.execute("""CREATE TABLE IF NOT EXISTS scores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rank STRING NOT NULL,
    score INTEGER NOT NULL,
    accuracy INTEGER NOT NULL,
    judgements STRING,
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)""")
#endregion

# cur.execute("""ALTER TABLE charts
#     ADD filenames STRING""")
con.commit()
async def echo(websocket):
    async for message in websocket:
        data:dict = json.loads(message)
        response = {
            "code": 404,
            "content": "what"
        }
        match data["type"]:
            case "whats_9_plus_10":
                response = {
                    "code": 21,
                    "content": "twenty_one"
                }
            case "register":
                if ("username" in data) and ("password" in data):
                    result = acc.create_account(data["username"], data["password"])
                    response = {
                        "code": 200 if result[0] else 401,
                        "content": result[1]
                    }
            case "login":
                if ("username" in data) and ("password" in data):
                    print(data)
                    result = acc.login(data["username"], data["password"])
                    print(result)
                    if not result[0]:
                        response = {
                            "code": 401,
                            "content": "wrong_account"
                        }
                    else:
                        response = {
                            "code": 200,
                            "content": result
                        }
            case "post_score":
                if "token" in data:
                    if data["token"] in acc.logged_in_users:
                        score = Score(data["score_data"])
                        result = sco.post_score(score, acc.logged_in_users[data["token"]].user_id)
                        response = {
                            "code": 200,
                            "content": result
                        }
            case "get_score":
                result = sco.get_score(data["score_id"])
                response = {
                    "code": 200,
                    "content": result
                }
            case "chart_data":
                result = cur.execute("SELECT * FROM charts WHERE id=?",
                    (data["chart_id"],)).fetchone()
                response = {
                    "code": 200,
                    "content": result
                }
            case _:
                response = {
                    "code": 404,
                    "content": "empty_request"
                }
        await websocket.send(json.dumps(response))

async def main():
    print("ws at port 8765")
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    subprocess.Popen(['flask', '--app', './src/file_server', 'run', '--port', str(FILES_PORT)])
    # app.run(port=FILES_PORT, ssl_context="adhoc")

    while True:
        asyncio.run(main())
