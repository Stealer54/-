
import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

@app.get("/")
def index():
    return send_from_directory(".", "index.html")

@app.get("/style.css")
def style():
    return send_from_directory(".", "style.css")

@app.post("/submit")
def submit():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Некорректные данные анкеты"}), 400

    required_fields = [
        "nickname", "level", "account_id", "age", "name",
        "city", "discord", "online", "forum", "vk", "rp_bio",
        "personal_file", "reason", "high_position", "linked",
        "twinks", "position"
    ]

    if any(not str(data.get(field, "")).strip() for field in required_fields):
        return jsonify({"error": "Заполните все поля анкеты"}), 400

    bot_url = os.getenv("BOT_API_URL", "").rstrip("/")
    secret = os.getenv("SITE_SECRET", "")

    if not bot_url or not secret:
        app.logger.error("Не настроены BOT_API_URL или SITE_SECRET")
        return jsonify({"error": "Сервер не настроен"}), 500

    try:
        response = requests.post(
            f"{bot_url}/submit",
            json=data,
            headers={"X-Site-Secret": secret},
            timeout=20
        )

        if response.status_code != 200:
            app.logger.error(
                "Discord bot returned %s: %s",
                response.status_code,
                response.text[:500]
            )
            return jsonify({"error": "Не удалось отправить анкету"}), 502

        return jsonify({"message": "Анкета успешно отправлена"}), 200

    except requests.RequestException:
        app.logger.exception("Не удалось связаться с Discord-ботом")
        return jsonify({"error": "Сервер бота временно недоступен"}), 502


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
