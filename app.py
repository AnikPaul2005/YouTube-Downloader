import os
import shutil
import tempfile
from urllib.parse import urlparse

import yt_dlp

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file
)

app = Flask(__name__)

MAX_DURATION = 1800


def validate_url(url):

    try:
        parsed = urlparse(url)

        allowed_domains = {
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
            "music.youtube.com"
        }

        return (
            parsed.scheme in ("http", "https")
            and parsed.hostname in allowed_domains
        )

    except Exception:
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():

    data = request.get_json(silent=True) or {}

    url = data.get("url", "").strip()
    mode = data.get("mode", "video")
    quality = data.get("quality", "720")

    if not validate_url(url):
        return jsonify({
            "error": "Please enter a valid YouTube URL."
        }), 400

    if mode not in ("video", "audio"):
        return jsonify({
            "error": "Invalid download mode."
        }), 400

    quality_map = {
        "1080": 1080,
        "720": 720,
        "480": 480,
        "best": None
    }

    if quality not in quality_map:
        return jsonify({
            "error": "Invalid video quality."
        }), 400

    if not shutil.which("ffmpeg"):
        return jsonify({
            "error": "FFmpeg is not installed on the server."
        }), 500

    temp_dir = tempfile.mkdtemp(prefix="yt_download_")

    try:

        if mode == "audio":

            format_option = "bestaudio/best"

            postprocessors = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]

        else:

            height = quality_map[quality]

            if height:

                format_option = (
                    f"bestvideo[height<={height}]"
                    f"[vcodec^=avc1][ext=mp4]+"
                    f"bestaudio[ext=m4a]/"
                    f"best[height<={height}][ext=mp4]/best"
                )

            else:

                format_option = (
                    "bestvideo[vcodec^=avc1][ext=mp4]+"
                    "bestaudio[ext=m4a]/"
                    "best[ext=mp4]/best"
                )

            postprocessors = []

        ydl_options = {

            "format": format_option,

            "outtmpl": os.path.join(
                temp_dir,
                "%(title).150B.%(ext)s"
            ),

            "noplaylist": True,

            "merge_output_format": "mp4",

            "postprocessors": postprocessors,

            "quiet": True,

            "no_warnings": True,

            "retries": 5,

            "fragment_retries": 5,

            "socket_timeout": 30,

            "match_filter": lambda info, incomplete: (
                "Video duration exceeds 30 minutes"
                if info.get("duration")
                and info["duration"] > MAX_DURATION
                else None
            ),

        }

        with yt_dlp.YoutubeDL(ydl_options) as downloader:

            downloader.download([url])

        downloaded_files = [
            os.path.join(temp_dir, filename)
            for filename in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, filename))
            and not filename.endswith((".part", ".ytdl"))
        ]

        if not downloaded_files:
            raise Exception("Downloaded file not found.")

        file_path = max(
            downloaded_files,
            key=os.path.getsize
        )

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )

        response.call_on_close(
            lambda: shutil.rmtree(temp_dir, ignore_errors=True)
        )

        return response

    except Exception as error:

        shutil.rmtree(temp_dir, ignore_errors=True)

        print("Download Error:", str(error))

        return jsonify({
            "error": "Download failed. Please try another video or quality."
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )