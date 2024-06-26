#!/usr/bin/env python3

from flask import Flask, request, render_template
from markupsafe import escape

app = Flask(__name__)

@app.route("/aveey")
@app.route("/aveey/<date>")
def main(date=None):
    video_url = 'https://bucketeer-3f5efd47-dcff-47cf-ab77-76a0f9c3b9b9.s3.us-east-1.amazonaws.com/videos/2024-06-11-earth.mp4'
    world_pop = 0
    space_pop = 0
    return render_template(
        'video.html',
        video_url=video_url,
        world_pop=world_pop,
        space_pop=space_pop,
    )
