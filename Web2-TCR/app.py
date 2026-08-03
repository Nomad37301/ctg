from flask import Flask, request, jsonify, make_response, send_from_directory, abort
import base64
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# ── CREDENTIALS (server-side only) ──────────────────────────────────────────
USERS = {
    "player": "ctf2026",
    "user":   "password",
}

# ── FLAG (never sent to client unless cookie is valid) ───────────────────────
FLAG = "tecart{mY_l11tl3_B0lu_k3t4n}"


# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if USERS.get(username) == password:
        # Encode role as base64 — cookie value the player will see & manipulate
        encoded_role = base64.b64encode(b"user").decode()
        resp = make_response(jsonify({"ok": True, "username": username}))
        resp.set_cookie(
            "role",
            encoded_role,
            max_age=86400,
            httponly=False,   # intentionally readable — that's the challenge
            samesite="Lax",
        )
        return resp

    return jsonify({"ok": False, "message": "Username atau password salah."}), 401


@app.route("/api/whoami", methods=["GET"])
def whoami():
    """
    Server verifies the 'role' cookie.
    Flag is ONLY returned here — never embedded in HTML.
    """
    role_cookie = request.cookies.get("role", "")

    if not role_cookie:
        return jsonify({"authenticated": False}), 401

    try:
        decoded_role = base64.b64decode(role_cookie).decode("utf-8")
    except Exception:
        return jsonify({"authenticated": False, "error": "Invalid cookie encoding"}), 400

    response = {
        "authenticated": True,
        "role": decoded_role,
    }

    if decoded_role == "admin":
        response["flag"] = FLAG

    return jsonify(response)


@app.route("/api/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie("role")
    return resp


# ── STATIC FILES ─────────────────────────────────────────────────────────────

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=False, port=8082)
