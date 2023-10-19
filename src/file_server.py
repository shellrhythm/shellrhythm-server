from flask import Flask, request, send_from_directory
from time import time_ns
from hashlib import file_digest
import json
from server import cht, acc
from src.charts_manager import ChartMetadata
from zipfile import ZipFile
app = Flask(__name__, static_folder="../storage")

def extract_zip(input_zip) -> dict:
    input_zip=ZipFile(input_zip)
    return {name: input_zip.read(name) for name in input_zip.namelist()}

@app.route('/', methods=['POST'])
def result():
    # print(request.form)
    if request.form["TOKEN"] not in acc.logged_in_users:
        return {"code": 401, "status":"NOT_LOGGED_IN"}
    file = request.files["upload_file"]
    digest = file_digest(file, "sha256")
    time_upload = time_ns()
    filename = str(time_upload) + "-" + digest.hexdigest()
    # with open("./storage/charts/"  + filename + ".zip", "x", encoding="utf-8") as _:
    #     pass
    zip_data = extract_zip(file)
    metadata = ChartMetadata()
    if "data.json" in zip_data.keys():
        chart_data = json.loads(zip_data["data.json"])
        metadata.checksum = digest.hexdigest()
        metadata.file_name = filename
        metadata.upload_time = time_upload

        metadata.song_title = chart_data["metadata"]["title"]
        metadata.song_artist = chart_data["metadata"]["artist"]
        metadata.chart_author = chart_data["metadata"]["author"]
        metadata.description = chart_data["metadata"]["description"]

        metadata.difficulty = chart_data["difficulty"]
        metadata.author_id = acc.get_user_id_from_token(request.form["TOKEN"])
    else:
        return {"code": 400, "status":"MALFORMED_ZIP"}
    cht.create_chart(metadata)
    file.save("./storage/charts/"  + filename + ".zip")

    return {'code':200, "status":"SUCCESSFULLY_UPLOADED"}

@app.route('/charts/<path:path>')
def send_chart(path):
    print("yup!")
    out = send_from_directory('../storage/charts', path)
    print("File: ", out)
    return out
