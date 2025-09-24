'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import Wavesurfer from 'wavesurfer.js';
import { Bar } from 'react-chartjs-2';
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js';
Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const i18n = {
  en: {
    heading: 'CITTAA Voice Analysis Demo',
    tagline: 'AI-Powered Mental Health Screening for India',
    record: 'Record Voice Sample',
    stop: 'Stop Recording',
    upload: 'Upload File',
    analyze: 'Analyze',
    analyzing: 'Analyzing...',
    reRecord: 'Re-record',
    privacy: 'Your voice data is processed securely and not stored',
    duration: 'Speak for 30 seconds to 2 minutes',
    cultural: 'Cultural Context',
    results: 'Results',
    depression: 'Depression Risk',
    stress: 'Stress Level',
    anxiety: 'Anxiety Level',
    recommendations: 'Recommendations',
    length: 'Voice Sample Length',
    generated: 'Generated on',
    demo: 'Demo Scenario'
  },
  hi: {
    heading: 'सिटा वॉयस विश्लेषण डेमो',
    tagline: 'भारत के लिए एआई-आधारित मानसिक स्वास्थ्य स्क्रीनिंग',
    record: 'आवाज़ रिकॉर्ड करें',
    stop: 'रिकॉर्डिंग रोकें',
    upload: 'फ़ाइल अपलोड करें',
    analyze: 'विश्लेषण करें',
    analyzing: 'विश्लेषण हो रहा है...',
    reRecord: 'दोबारा रिकॉर्ड करें',
    privacy: 'आपके वॉयस डेटा को सुरक्षित रूप से प्रोसेस किया जाता है और संग्रहीत नहीं किया जाता',
    duration: '30 सेकंड से 2 मिनट तक बोलें',
    cultural: 'सांस्कृतिक संदर्भ',
    results: 'परिणाम',
    depression: 'अवसाद का जोखिम',
    stress: 'तनाव का स्तर',
    anxiety: 'चिंता का स्तर',
    recommendations: 'सुझाव',
    length: 'वॉयस सैंपल की लंबाई',
    generated: 'उत्पन्न तिथि/समय',
    demo: 'डेमो परिदृश्य'
  }
};

const regions = [
  { value: 'north_india', label: 'North India' },
  { value: 'south_india', label: 'South India' },
  { value: 'west_india', label: 'West India' },
  { value: 'east_india', label: 'East India' }
];
const languages = ['Hindi', 'English', 'Tamil', 'Telugu', 'Bengali', 'Gujarati', 'Marathi'].map(l => ({ value: l.toLowerCase(), label: l }));
const ages = [
  { value: 'student', label: 'Student (8-18)' },
  { value: 'adult', label: 'Adult (19-65)' },
  { value: 'senior', label: 'Senior (65+)' }
];
const genders = ['Male', 'Female', 'Other'].map(g => ({ value: g.toLowerCase(), label: g }));

type AnalyzeResponse = {
  depression_score: number;
  stress_score: number;
  anxiety_score: number;
  recommendations: string[];
  cultural_context: Record<string, string>;
  pdf_report_b64?: string;
  processing_time?: string;
  confidence?: number | undefined;
  confidence_level?: number | undefined;
  features?: any;
};
async function blobToArrayBuffer(blob: Blob) {
  return await blob.arrayBuffer();
}
function encodeWavFromAudioBuffer(audioBuffer: AudioBuffer): Blob {
  const numCh = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const samples = audioBuffer.length;
  const bytesPerSample = 2;
  const blockAlign = numCh * bytesPerSample;
  const dataSize = samples * blockAlign;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);
  const writeString = (offset: number, s: string) => { for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i)); };
  writeString(0, 'RIFF');
  view.setUint32(4, 36 + dataSize, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, numCh, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 8 * bytesPerSample, true);
  writeString(36, 'data');
  view.setUint32(40, dataSize, true);
  let offset = 44;
  const interleaved = new Float32Array(samples * numCh);
  const channelData: Float32Array[] = [];
  for (let ch = 0; ch < numCh; ch++) channelData[ch] = audioBuffer.getChannelData(ch);
  for (let i = 0; i < samples; i++) {
    for (let ch = 0; ch < numCh; ch++) {
      interleaved[i * numCh + ch] = channelData[ch][i];
    }
  }
  for (let i = 0; i < interleaved.length; i++) {
    let s = Math.max(-1, Math.min(1, interleaved[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    offset += 2;
  }
  return new Blob([buffer], { type: 'audio/wav' });
}
async function ensureWav(blob: Blob): Promise<Blob> {
  if (blob.type === 'audio/wav') return blob;
  const ab = await blobToArrayBuffer(blob);
  const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
  const audioBuffer = await ctx.decodeAudioData(ab.slice(0) as ArrayBuffer);
  const wav = encodeWavFromAudioBuffer(audioBuffer);
  await ctx.close();
  return wav;
}


export default function Page() {
  const [lang, setLang] = useState<'en'|'hi'>('en');
  const t = i18n[lang];
  const [region, setRegion] = useState('south_india');
  const [language, setLanguage] = useState('english');
  const [age, setAge] = useState('adult');
  const [gender, setGender] = useState('male');
  const [recording, setRecording] = useState(false);
  const [level, setLevel] = useState(0);
  const [duration, setDuration] = useState(0);
  const [blob, setBlob] = useState<Blob|null>(null);
  const [result, setResult] = useState<AnalyzeResponse|null>(null);
  const [loading, setLoading] = useState(false);
  const [demo, setDemo] = useState<string>('');
  const waveRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<Wavesurfer|null>(null);
  const mediaStreamRef = useRef<MediaStream|null>(null);
  const mediaRecorderRef = useRef<MediaRecorder|null>(null);
  const audioCtxRef = useRef<AudioContext|null>(null);
  const analyserRef = useRef<AnalyserNode|null>(null);
  const rafRef = useRef<number|undefined>(undefined);
  const chunksRef = useRef<BlobPart[]>([]);

  useEffect(() => {
    if (waveRef.current && !wsRef.current) {
      wsRef.current = Wavesurfer.create({
        container: waveRef.current,
        waveColor: '#a9c2ff',
        progressColor: '#2c5aa0',
        cursorColor: '#1f4aa8',
        height: 60,
        barWidth: 2,
        barGap: 1,
      });
    }
  }, []);

  const startRecording = async () => {
    setResult(null);
    setBlob(null);
    setDuration(0);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaStreamRef.current = stream;
    const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorderRef.current = mr;
    chunksRef.current = [];
    mr.ondataavailable = (e) => { if (e.data.size) chunksRef.current.push(e.data); };
    mr.onstop = async () => {
      const b = new Blob(chunksRef.current, { type: 'audio/webm' });
      setBlob(b);
      const url = URL.createObjectURL(b);
      wsRef.current?.load(url);
    };
    mr.start(100);
    setRecording(true);

    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    audioCtxRef.current = ctx;
    const src = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    src.connect(analyser);
    analyserRef.current = analyser;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const tick = () => {
      analyser.getByteTimeDomainData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const v = (dataArray[i] - 128) / 128;
        sum += v * v;
      }
      const rms = Math.sqrt(sum / dataArray.length);
      setLevel(Math.min(1, rms * 4));
      setDuration(d => d + 0.05);
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    mediaStreamRef.current?.getTracks().forEach(t => t.stop());
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    audioCtxRef.current?.close();
    setRecording(false);
  };

  const [health, setHealth] = useState<'ok'|'bad'|'checking'>('checking');
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const res = await fetch(`${backendUrl}/health`, { cache: 'no-store' });
        if (!cancelled && res.ok) setHealth('ok'); else if (!cancelled) setHealth('bad');
      } catch {
        if (!cancelled) setHealth('bad');
      }
    };
    check();
    const id = setInterval(check, 15000);
    return () => { cancelled = true; clearInterval(id); };
  }, [backendUrl]);

  const analyze = async () => {
    if (demo) {
      const presets: Record<string, AnalyzeResponse> = {
        low_risk_student: { depression_score: 15, stress_score: 25, anxiety_score: 20, recommendations: ['Maintain healthy study habits', 'Continue social activities'], cultural_context: { region, language, age_group: age, gender } },
        moderate_stress_professional: { depression_score: 30, stress_score: 65, anxiety_score: 40, recommendations: ['Practice workplace stress management', 'Consider work-life balance'], cultural_context: { region, language, age_group: age, gender } },
        high_anxiety_case: { depression_score: 25, stress_score: 45, anxiety_score: 75, recommendations: ['Seek professional counseling', 'Learn anxiety management techniques'], cultural_context: { region, language, age_group: age, gender } }
      };
      setResult(presets[demo]);
      return;
    }

    if (!blob) return;
    setLoading(true);
    try {
      const fd = new FormData();
      const wavBlob = await ensureWav(blob);
      fd.append('audio', new File([wavBlob], 'recording.wav', { type: 'audio/wav' }));
      fd.append('region', region);
      fd.append('language', language);
      fd.append('age_group', age);
      fd.append('gender', gender);

      const res = await fetch(`${backendUrl}/analyze`, { method: 'POST', body: fd });
      if (!res.ok) {
        let text = '';
        try { text = await res.text(); } catch {}
        throw new Error(text || `HTTP ${res.status}`);
      }
      const json: AnalyzeResponse = await res.json();
      setResult(json);

      if (json.pdf_report_b64) {
        const a = document.createElement('a');
        a.href = `data:application/pdf;base64,${json.pdf_report_b64}`;
        a.download = 'CITTAA_Vocalysis_Report.pdf';
        a.textContent = 'Download PDF';
      }
    } catch (e: any) {
      console.error(e);
      alert(`Analysis failed: ${e?.message || e || 'Unknown error'}. Please use a true WAV (16kHz mono), or try a Demo Scenario.`);
    } finally {
      setLoading(false);
    }
  };

  const probData = useMemo(() => {
    if (!result) return null;
    const d = [result.depression_score ?? 0, result.stress_score ?? 0, result.anxiety_score ?? 0];
    return {
      labels: [t.depression, t.stress, t.anxiety],
      datasets: [{ label: 'Score /100', data: d, backgroundColor: ['#a3bffd', '#ffe08a', '#ff9aa2'] }]
    };
  }, [result, lang]);

  return (
    <div className="container">
      <div className="header">
        <img className="logo" src="/logo.svg" alt="CITTAA" />
        <div>
          <div className="title">{t.heading}</div>
          <div className="subtitle">{t.tagline}</div>
        </div>
        <div style={{ marginLeft: 'auto' }} className="langToggle">
          <button onClick={() => setLang('en')} style={{ background: lang==='en' ? '#eaf0ff' : 'white' }}>EN</button>
          <button onClick={() => setLang('hi')} style={{ background: lang==='hi' ? '#eaf0ff' : 'white' }}>हिंदी</button>
        </div>
      </div>

      <div className="banner" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div className="badge">Healthcare-grade UI</div>
        <div className="badge" style={{ background: health==='ok' ? '#d4edda' : health==='checking' ? '#fff3cd' : '#f8d7da', color: health==='ok' ? '#155724' : health==='checking' ? '#856404' : '#721c24' }}>
          {health === 'ok' ? 'Backend: Online' : health === 'checking' ? 'Checking backend…' : 'Backend: Unreachable'}
        </div>
        {health === 'bad' && <button className="button small" onClick={()=>location.reload()}>Retry</button>}
        <div className="small">{t.privacy} • {t.duration}</div>
      </div>

      <div className="card">
        <div className="controls" style={{ marginBottom: 12 }}>
          <select value={region} onChange={e=>setRegion(e.target.value)}>
            {regions.map(r=> <option key={r.value} value={r.value}>{r.label}</option>)}
          </select>
          <select value={language} onChange={e=>setLanguage(e.target.value)}>
            {languages.map(l=> <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>
          <select value={age} onChange={e=>setAge(e.target.value)}>
            {ages.map(a=> <option key={a.value} value={a.value}>{a.label}</option>)}
          </select>
          <select value={gender} onChange={e=>setGender(e.target.value)}>
            {genders.map(g=> <option key={g.value} value={g.value}>{g.label}</option>)}
          </select>
        </div>

        <div className="wave" ref={waveRef} />
        <div className="level" style={{ width: `${Math.round(level*100)}%`, transition: 'width .05s ease' }} />
        <div className="small">{t.length}: {duration.toFixed(1)}s</div>

        <div className="actions" style={{ marginTop: 12 }}>
          {!recording ? (
            <button className="button" onClick={startRecording}>{t.record}</button>
          ) : (
            <button className="button warning" onClick={stopRecording}>{t.stop}</button>
          )}
          <label className="button secondary">
            {t.upload}
            <input hidden type="file" accept="audio/wav,.wav" onChange={async e=>{
              const f = e.target.files?.[0];
              if (!f) return;
              try {
                const wavBlob = await ensureWav(f);
                setBlob(wavBlob);
                const url = URL.createObjectURL(wavBlob);
                wsRef.current?.load(url);
              } catch (err) {
                console.error(err);
                alert('Could not read/convert the selected audio. Please upload a true WAV (16kHz mono), or try recording.');
              }
            }}/>
          </label>

          <select value={demo} onChange={e=>setDemo(e.target.value)}>
            <option value="">{t.demo}</option>
            <option value="low_risk_student">Low Risk Student</option>
            <option value="moderate_stress_professional">Moderate Stress Professional</option>
            <option value="high_anxiety_case">High Anxiety Case</option>
          </select>

          <button className="button" onClick={analyze} disabled={loading || (!blob && !demo)}>
            {loading ? t.analyzing : t.analyze}
          </button>
        </div>
      </div>

      {result && (
        <div className="grid" style={{ marginTop: 16 }}>
          <div className="card">
            <div style={{ fontWeight: 800, marginBottom: 8 }}>{t.results}</div>
            <div className="grid-3">
              <div className={`score ${result.depression_score>66?'h':result.depression_score>33?'m':'l'}`}>
                <div className="small">{t.depression}</div>
                <div style={{ fontSize: 24, fontWeight: 800 }}>{Math.round(result.depression_score)} / 100</div>
              </div>
              <div className={`score ${result.stress_score>66?'h':result.stress_score>33?'m':'l'}`}>
                <div className="small">{t.stress}</div>
                <div style={{ fontSize: 24, fontWeight: 800 }}>{Math.round(result.stress_score)} / 100</div>
              </div>
              <div className={`score ${result.anxiety_score>66?'h':result.anxiety_score>33?'m':'l'}`}>
                <div className="small">{t.anxiety}</div>
                <div style={{ fontSize: 24, fontWeight: 800 }}>{Math.round(result.anxiety_score)} / 100</div>
              </div>
            </div>
            {probData && (
              <div style={{ marginTop: 12 }}>
                <Bar data={probData} options={{ plugins: { legend: { display: false }}, scales: { y: { max: 100 }}}} />
              </div>
            )}
          </div>
          <div className="card">
            <div style={{ fontWeight: 800, marginBottom: 8 }}>{t.recommendations}</div>
            <ul>
              {(result.recommendations||[]).map((r,i)=> <li key={i}>{r}</li>)}
            </ul>
            {result.pdf_report_b64 && (
              <a
                href={`data:application/pdf;base64,${result.pdf_report_b64}`}
                download="CITTAA_Vocalysis_Report.pdf"
                className="button"
                style={{ display:'inline-block', marginTop: 10 }}
              >
                Download PDF
              </a>
            )}
          </div>
        </div>
      )}

      <div className="footer">
        © {new Date().getFullYear()} CITTAA Health Services • Premium medical interface • Hindi/English
      </div>
    </div>
  );
}
