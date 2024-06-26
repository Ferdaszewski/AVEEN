#!/usr/bin/env python3
import os

from flask import Flask, request, render_template
from support.database import setup_db_connection

app = Flask(__name__)


@app.route("/aveey")
@app.route("/aveey/<date>")
def main(date=None):
    with setup_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT video_key FROM video_pop ORDER BY video_day desc LIMIT 1")
            row = cursor.fetchone()
            video_key = row if row is None else row[0]
    video_url = f'https://{os.environ.get("BUCKETEER_BUCKET_NAME")}.s3.us-east-1.amazonaws.com/{video_key}'
    world_pop = 0
    space_pop = 0
    return render_template(
        'video.html',
        video_url=video_url,
        world_pop=world_pop,
        space_pop=space_pop,
    )


@app.route("/metrics")
def main():
    with setup_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT sum(*) FROM video_pop")
            row = cursor.fetchone()
            videos = 0 if row is None else row[0]
            cursor.execute("SELECT sum(*) FROM epic_images")
            row = cursor.fetchone()
            images = 0 if row is None else row[0]

            return {
                "images_dowloaded": images,
                "videos_processed": videos,
            }
