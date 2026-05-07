from flask import Flask, request, jsonify, render_template
import sqlite3
import time
from datetime import datetime
import os

DB_PATH = os.environ.get("DB_PATH", "/data/app.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            curtain_players TEXT NOT NULL,
            door_players TEXT NOT NULL,
            curtain_score INTEGER NOT NULL,
            door_score INTEGER NOT NULL,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__)

    init_db()

    # Static Pages

    @app.route("/")
    def index():
        return render_template("index.html")

    # REST API

    @app.route("/api/scores", methods=["GET"])
    def get_scores():
        conn = get_db()

        start_timestamp = int(datetime.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ).timestamp())


        rows = conn.execute(
            """
            SELECT *
            FROM scores
            WHERE timestamp >= ?
            ORDER BY id DESC
            """,
            (start_timestamp,)
        ).fetchall()

        conn.close()

        scores = [dict(row) for row in rows]

        return jsonify(scores)


    @app.route("/api/scores", methods=["POST"])
    def add_score():
        data = request.json

        curtain_players = data.get("curtain_players")
        door_players = data.get("door_players")
        curtain_score = data.get("curtain_score")
        door_score = data.get("door_score")
        notes = data.get("notes")

        if notes is not None:
            notes = notes.strip()

        if notes == "":
            notes = None

        if not all([curtain_players, door_players, curtain_score is not None, door_score is not None]):
            return jsonify({"error": "Missing at least one required input"}), 400

        conn = get_db()

        conn.execute(
            "INSERT INTO scores (timestamp, curtain_players, door_players, curtain_score, door_score, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (int(time.time()), curtain_players, door_players, curtain_score, door_score, notes)
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True})

    return app

app = create_app()


if __name__ == "__main__":
    init_db()
    #app.run(host="0.0.0.0", port=5000, debug=True)