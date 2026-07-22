import base64, io, os
from flask import Flask, request, send_file
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
        text = request.json.get("text", "")
    else:
        text = request.args.get("text", "")

    if not text:
        return {"error": "text required"}, 400

    r = client.chat.completions.create(
        model="mimo-v2.5-tts-voiceclone",
        messages=[{"role": "assistant", "content": text}],
        audio={"format": "wav", "voice": VOICE},
    )
    audio = base64.b64decode(r.choices[0].message.audio.data)
    return send_file(io.BytesIO(audio), mimetype="audio/wav")


@app.route("/", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)
