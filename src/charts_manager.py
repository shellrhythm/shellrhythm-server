import sqlite3

class ChartMetadata:
    """Object used when creating a new chart"""
    checksum:str = ""
    song_title:str = ""
    song_artist:str = ""
    difficulty:float = 0.0
    chart_author:str = ""
    author_id:int = 0
    description:str = ""
    upload_time:int = 0
    file_name:str = ""

class ChartsManager:
    con = sqlite3.connect("charts.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    def get_chart(self, chart_id):
        self.cur.execute("SELECT * FROM charts WHERE id=?",
            (chart_id,)).fetchall()

    def create_chart(self, chart_data:ChartMetadata):
        self.cur.execute("INSERT INTO charts (checksum, songname, difficulty, artist, author, "+\
            "author_id, description, upload_time, chart_version, ) VALUES (?,?,?,?,?,?,?,?,?)",
            (chart_data.checksum, chart_data.song_title, chart_data.difficulty,
            chart_data.song_artist, chart_data.chart_author, chart_data.author_id,
            chart_data.description, chart_data.upload_time, 0
            )
        )
