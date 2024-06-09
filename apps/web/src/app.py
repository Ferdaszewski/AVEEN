#!/usr/bin/env python3

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def main():
    return '''
        <form action="/echo_user_input" method="POST">
            <input name="user_input">
            <input type="submit" value="Submit!">
        <form>
    '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    input_text = request.form.get("user_input", "", type=str)
    return f'You Entered: "{escape(input_text)}"'
