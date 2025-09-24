from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import base64
import uvicorn
from typing import Optional

from vocalysis_clean import run_vocalysis_analysis
from audio_converter import convert_audio_to_wav_if_needed

app = FastAPI(title="CITTAA Vocalysis API", version="0.1.0")

origins_env = os.getenv("BACKEND_CORS_ORIGINS", "") or os.getenv("CORS_ORIGIN", "")
origins = [o.strip() for o in origins_env.split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_voice(
    audio: UploadFile = File(...),
    region: str = Form("south_india"),
    language: str = Form("english"),
    age_group: str = Form("adult"),
    gender: str = Form("other"),
):
    try:
        content = await audio.read()
        original_filename = audio.filename or "upload"
        wav_bytes = convert_audio_to_wav_if_needed(content, original_filename)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
            tmp_wav.write(wav_bytes)
            tmp_wav.flush()
            wav_path = tmp_wav.name

        cultural_context = {
            "region": region,
            "language": language,
            "age_group": age_group,
            "gender": gender,
        }

        results = run_vocalysis_analysis(file_path=wav_path, cultural_context=cultural_context)

        pdf_bytes = results.get("pdf_report")
        if isinstance(pdf_bytes, str):
            try:
                pdf_bytes = pdf_bytes.encode("latin1")
            except Exception:
                pdf_bytes = pdf_bytes.encode("utf-8", errors="ignore")
        if pdf_bytes:
            results["pdf_report_b64"] = base64.b64encode(pdf_bytes).decode("ascii")
            results.pop("pdf_report", None)

        return JSONResponse(results)
    finally:
        try:
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception:
            pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port)
