import base64, os
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

API_KEY = os.environ["MIMO_API_KEY"]
REF_AUDIO = os.environ.get("REF_AUDIO_PATH", "voice_preview_daddy.mp3")

with open(REF_AUDIO, "rb") as f:
    VOICE = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode('utf-8')}"

client = OpenAI(api_key=API_KEY, base_url="https://api.xiaomimimo.com/v1")


@app.route("/api/tts", methods=["GET", "POST"])
def tts():
    if request.method == "POST" and request.is_json:
        raw = request.json.get("text", "")
    else:
        raw = request.args.get("text", "")

    if not raw:
        return {"error": "text required"}, 400

    # 支持情绪指令: "文本 ||| 情绪描述" → user 指令 + assistant 文本
    if " ||| " in raw:
        text, instruction = raw.split(" ||| ", 1)
        messages = [
            {"role": "user", "content": instruction.strip()},
            {"role": "assistant", "content": text.strip()},
        ]
    else:
        messages = [{"role": "assistant", "content": raw.strip()}]

    r = client.chat.completions.create(
        model="mimo-v2.5-tts-voiceclone",
        messages=messages,
        audio={"format": "wav", "voice": VOICE},
    )
    return {
        "choices": [{
            "message": {
                "audio": {
                    "data": r.choices[0].message.audio.data
                }
            }
        }]
    }


@app.route("/", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
