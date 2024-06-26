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
            cursor.execute("SELECT v.video_key, s.pop, w.pop FROM video_pop v JOIN space_pop s ON v.space_pop_id = s.id JOIN world_pop w ON v.world_pop_id = w.id ORDER BY v.video_day desc LIMIT 1")
            row = cursor.fetchone()
            video_key, space_pop, world_pop = (None, None, None) if row is None else row
    video_url = f'https://{os.environ.get("BUCKETEER_BUCKET_NAME")}.s3.us-east-1.amazonaws.com/{video_key}'
    return render_template(
        'video.html',
        video_url=video_url,
        world_pop=0 if world_pop is None else world_pop,
        space_pop=0 if space_pop is None else space_pop,
    )


@app.route("/metrics")
def metrics():
    with setup_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM video_pop")
            row = cursor.fetchone()
            videos = 0 if row is None else row[0]
            cursor.execute("SELECT count(*) FROM epic_images")
            row = cursor.fetchone()
            images = 0 if row is None else row[0]

            return {
                "images_dowloaded": images,
                "videos_processed": videos,
            }
