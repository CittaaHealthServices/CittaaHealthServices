import os
import io
import base64
import numpy as np
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import numbers

try:
    import librosa  # type: ignore
    import librosa.feature  # noqa: F401
except Exception:
    librosa = None
librosa = None

from scipy.io import wavfile
from fpdf import FPDF
from audio_converter import convert_audio_to_wav_if_needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vocalysis")

app = FastAPI(title="CITTAA Vocalysis API", version="0.1.0")

cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if cors_origins == "*" else [o.strip() for o in cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


def _analyze_numpy_wav(y: np.ndarray, sr: int):
    y = y.astype(np.float32)
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    y = y / (np.max(np.abs(y)) + 1e-9)

    zc = np.mean(np.abs(np.diff(np.sign(y)))) / 2.0
    energy = np.sqrt(np.mean(y ** 2))
    if y.size > sr:
        frames = y.size // sr
        if frames > 0:
            frame_means = y[:frames * sr].reshape(frames, sr).mean(axis=1)
            energy_std = float(np.std(frame_means))
        else:
            energy_std = float(np.std(y))
    else:
        energy_std = float(np.std(y))

    n = 2048
    hop = 512
    frames = max(1, (len(y) - n) // hop + 1)
    cents = []
    window = np.hanning(n)
    for i in range(frames):
        seg = y[i * hop:i * hop + n]
        if len(seg) < n:
            break
        S = np.abs(np.fft.rfft(seg * window))
        freqs = np.fft.rfftfreq(n, d=1.0 / sr)
        denom = np.sum(S) + 1e-9
        cents.append(float(np.sum(freqs * S) / denom))
    spectral_centroid_mean = float(np.mean(cents)) if cents else 0.0
    spectral_centroid_std = float(np.std(cents)) if cents else 0.0

    depression = 0.0
    if energy_std < 0.02:
        depression += 30.0
    if energy < 0.05:
        depression += 20.0
    depression = min(100.0, depression)

    stress = 0.0
    if spectral_centroid_std > 1000:
        stress += 35.0
    if zc > 0.1:
        stress += min(30.0, (zc - 0.1) * 300.0)
    stress = min(100.0, stress)

    anxiety = 0.0
    if spectral_centroid_mean > 2000:
        anxiety += min(60.0, (spectral_centroid_mean - 2000) / 2000 * 35.0)
    if energy_std > 0.05:
        anxiety += 25.0
    anxiety = min(100.0, anxiety)

    primary = ["depression", "stress", "anxiety"][int(np.argmax([depression, stress, anxiety]))]
    score_range = max(depression, stress, anxiety) - min(depression, stress, anxiety)
    confidence = round(min(95.0, 60.0 + score_range * 0.7), 1)

    features = {
        "zcr_mean": float(zc),
        "energy_mean": float(energy),
        "energy_std": float(energy_std),
        "spectral_centroid_mean": spectral_centroid_mean,
        "spectral_centroid_std": spectral_centroid_std,
    }

    return {
        "depression_score": round(float(depression), 1),
        "stress_score": round(float(stress), 1),
        "anxiety_score": round(float(anxiety), 1),
        "primary_concern": primary,
        "confidence_level": confidence,
        "processing_time": "< 2 seconds",
        "features": features,
    }


def _make_pdf(report: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "CITTAA Voice Analysis Report", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.ln(4)
    pdf.cell(0, 8, f"Depression Risk: {report['depression_score']}/100", ln=True)
    pdf.cell(0, 8, f"Stress Level: {report['stress_score']}/100", ln=True)
    pdf.cell(0, 8, f"Anxiety Level: {report['anxiety_score']}/100", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Primary Concern: {report['primary_concern']}", ln=True)
    pdf.cell(0, 8, f"Confidence: {report['confidence_level']}%", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, "Voice Biomarkers (heuristic):", ln=True)
    pdf.set_font("Arial", size=11)
    feats = report.get("features", {})
    for k in ["zcr_mean", "energy_mean", "energy_std", "spectral_centroid_mean", "spectral_centroid_std"]:
        if k in feats:
            pdf.cell(0, 8, f"- {k}: {feats[k]}", ln=True)
    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin1")
    return pdf_bytes
def _to_py(obj):
    if isinstance(obj, dict):
        return {str(k): _to_py(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_py(v) for v in obj]
    try:
        import numpy as _np
        if isinstance(obj, _np.generic):
            return obj.item()
        if isinstance(obj, _np.ndarray):
            return obj.tolist()
    except Exception:
        pass
    if isinstance(obj, numbers.Number):
        return float(obj)
    return obj



@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.post("/analyze")
async def analyze(
    audio: UploadFile = File(...),
    region: str = Form("south_india"),
    language: str = Form("english"),
    age_group: str = Form("adult"),
    gender: str = Form("other"),
):
    logger.info("analyze: start")
    name = audio.filename or "audio.wav"
    try:
        data = await audio.read()
    except Exception as e:
        logger.exception("analyze: failed to read upload")
        raise
    logger.info("analyze: read %d bytes from %s", len(data), name)
    if librosa is None:
        try:
            if not name.lower().endswith(".wav"):
                logger.info("analyze: converting non-wav input to wav")
                data = convert_audio_to_wav_if_needed(data, name)
            sr, y = wavfile.read(io.BytesIO(data))
            logger.info("analyze: wavfile.read ok sr=%s len=%s", sr, getattr(y, 'shape', None))
        except Exception as e:
            logger.exception("analyze: wavfile.read failed (post-conversion attempt)")
            raise HTTPException(status_code=400, detail=f"Failed to read audio: {e}")
        report = _analyze_numpy_wav(y, sr)
    else:
        try:
            y, sr = librosa.load(io.BytesIO(data), sr=16000)
            logger.info("analyze: librosa.load ok sr=%s len=%s", sr, len(y))
        except Exception as e:
            logger.exception("analyze: librosa.load failed")
            raise HTTPException(status_code=400, detail=f"Failed to read audio: {e}")
        zc = np.mean(np.abs(np.diff(np.sign(y)))) / 2.0
        energy = np.sqrt(np.mean(y ** 2))
        n = 2048
        hop = 512
        cents = []
        window = np.hanning(n)
        for i in range(max(1, (len(y) - n) // hop + 1)):
            seg = y[i * hop:i * hop + n]
            if len(seg) < n:
                break
            S = np.abs(np.fft.rfft(seg * window))
            freqs = np.fft.rfftfreq(n, d=1.0 / sr)
            denom = np.sum(S) + 1e-9
            cents.append(float(np.sum(freqs * S) / denom))
        S_c = float(np.mean(cents)) if cents else 0.0
        if y.size > sr:
            frames = y.size // sr
            if frames > 0:
                energy_std = float(np.std(y[:frames * sr].reshape(frames, sr).mean(axis=1)))
            else:
                energy_std = float(np.std(y))
        else:
            energy_std = float(np.std(y))
        report = _analyze_numpy_wav((y * 32767).astype(np.int16), sr)
        report["features"].update({"zcr_mean": float(zc), "spectral_centroid_mean": float(S_c), "energy_mean": float(energy), "energy_std": float(energy_std)})

    report["cultural_context"] = {
        "region": region,
        "language": language,
        "age_group": age_group,
        "gender": gender,
    }
    logger.info("analyze: generating PDF")
    pdf_bytes = _make_pdf(report)
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    logger.info("analyze: done")

    payload = {**report, "pdf_report_b64": b64}
    payload = _to_py(payload)
    return JSONResponse(content=jsonable_encoder(payload))
