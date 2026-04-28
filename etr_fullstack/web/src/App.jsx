import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Activity, Radio, Shield, Timer } from "lucide-react";

const GOLD = "#D4AF37";
const API_URL = "http://localhost:8000/predict";
const POLL_INTERVAL_MS = 5000;
const HUD_BORDER = "1px solid rgba(212,175,55,0.35)";
const HUD_GLOW = "0 0 10px rgba(212, 175, 55, 0.3)";

const COLOR_GLOW_MAP = {
  red: "#ff4d4d",
  blue: "#5dade2",
  green: "#48c774",
  yellow: "#f4d35e",
  purple: "#bb86fc",
  orange: "#ff9f43",
  white: "#ffffff",
  black: "#7f8c8d",
  default: GOLD,
};

function Header() {
  return (
    <header className="flex items-center justify-between border-b px-6 py-4" style={{ borderBottom: HUD_BORDER, boxShadow: HUD_GLOW }}>
      <div className="flex min-w-[100px] flex-col items-center gap-2">
        <img src="/iste%20logo.png" alt="ISTE" className="h-12 w-12 object-contain" style={{ filter: "drop-shadow(0 0 10px rgba(212,175,55,0.5))" }} />
        <span className="text-[10px] tracking-[0.3em]" style={{ color: "rgba(212,175,55,0.8)" }}>
          ISTE BITS
        </span>
      </div>
      <div className="px-4 text-center">
        <h1 className="whitespace-nowrap text-4xl font-bold uppercase tracking-widest md:text-6xl" style={{ color: "#f5f5f5", textShadow: "0 0 16px rgba(212,175,55,0.45), 0 0 46px rgba(212,175,55,0.2)" }}>
          ESCAPE THE ROOM
        </h1>
      </div>
      <div className="flex min-w-[100px] flex-col items-center gap-2">
        <img src="/trevini%20logo.png" alt="Triveni" className="h-12 w-12 object-contain" style={{ filter: "drop-shadow(0 0 10px rgba(212,175,55,0.5))" }} />
        <span className="text-[10px] tracking-[0.24em]" style={{ color: "rgba(212,175,55,0.8)" }}>
          Triveni '26
        </span>
      </div>
    </header>
  );
}

function TelemetryCard({ icon: Icon, label, value }) {
  return (
    <div className="flex min-w-[160px] items-center gap-3 rounded-md bg-black/30 px-3 py-2 backdrop-blur-md" style={{ border: HUD_BORDER, boxShadow: HUD_GLOW }}>
      <Icon size={15} style={{ color: GOLD }} />
      <div>
        <p className="text-[10px] tracking-[0.25em] text-zinc-400">{label}</p>
        <p className="text-sm tracking-[0.18em]" style={{ color: GOLD }}>{value}</p>
      </div>
    </div>
  );
}

function TarsTerminal({ logs }) {
  return (
    <aside className="h-full min-h-0 rounded-lg bg-zinc-950/35 p-4 backdrop-blur-xl" style={{ border: HUD_BORDER, boxShadow: HUD_GLOW }}>
      <h2 className="mb-3 border-b pb-2 text-xs tracking-[0.35em]" style={{ borderBottom: HUD_BORDER, color: GOLD }}>TARS TERMINAL</h2>
      <div className="flex h-[calc(100%-2rem)] flex-col gap-2 overflow-y-auto pr-1">
        {logs.map((log) => (
          <p key={log.id} className="text-[11px] tracking-[0.1em] text-zinc-300">{log.text}</p>
        ))}
      </div>
    </aside>
  );
}

function WormholeScanner({ onDetection, onLog, onCameraState, onCountdownChange }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const pollingRef = useRef(null);
  const inFlightRef = useRef(false);
  const countdownRef = useRef(POLL_INTERVAL_MS / 1000);

  const extractDetectedColor = (payload) => {
    const candidates = [
      payload?.color,
      payload?.detected_color,
      payload?.prediction?.color,
      payload?.result?.color,
      payload?.detections?.[0]?.color,
      payload?.detections?.[0]?.class,
      payload?.label,
    ];
    const match = candidates.find((entry) => typeof entry === "string" && entry.trim().length > 0);
    return match ? match.trim().toLowerCase() : "";
  };

  const captureAndPredict = useCallback(async () => {
    if (inFlightRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;

    inFlightRef.current = true;
    canvas.width = video.videoWidth || 480;
    canvas.height = video.videoHeight || 360;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.86));
    if (!blob) {
      inFlightRef.current = false;
      return;
    }

    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");

    try {
      const response = await fetch(API_URL, { method: "POST", body: formData });
      if (!response.ok) throw new Error("fault");
      const payload = await response.json();
      const detected = extractDetectedColor(payload);
      if (detected) {
        onDetection(detected);
        onLog(`[TARS]: Color signature acquired: ${detected.toUpperCase()}.`);
      } else {
        onLog("[STATUS]: Scanning for signatures...");
      }
    } catch {
      onLog("[STATUS]: SYSTEM FAULT");
      onCameraState("fault");
    } finally {
      inFlightRef.current = false;
    }
  }, [onDetection, onLog, onCameraState]);

  useEffect(() => {
    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        onCameraState("online");
        onLog("[TARS]: Optical feed online.");
        onCountdownChange(POLL_INTERVAL_MS / 1000);
        onLog(`[STATUS]: Recalibrating sensors... ${POLL_INTERVAL_MS / 1000}s`);
        pollingRef.current = setInterval(() => {
          countdownRef.current -= 1;
          const next = countdownRef.current;
          if (next <= 0) {
            captureAndPredict();
            countdownRef.current = POLL_INTERVAL_MS / 1000;
            onCountdownChange(POLL_INTERVAL_MS / 1000);
            return;
          }
          onCountdownChange(next);
          onLog(`[STATUS]: Recalibrating sensors... ${next}s`);
        }, 1000);
      } catch {
        onCameraState("offline");
        onLog("[STATUS]: CAMERA OFFLINE");
      }
    };

    start();
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach((track) => track.stop());
    };
  }, [captureAndPredict, onCameraState, onCountdownChange, onLog]);

  return (
    <div className="relative h-full w-full">
      <div className="absolute inset-[-8px] rounded-full" style={{ background: "conic-gradient(from 0deg, rgba(212,175,55,0.85), transparent 26%, rgba(212,175,55,0.7), transparent 70%, rgba(212,175,55,0.9))", filter: "blur(1.6px)", animation: "spin 6s linear infinite" }} />
      <motion.div
        className="absolute inset-0 rounded-full border"
        animate={{ opacity: [0.35, 1, 0.35] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        style={{ border: HUD_BORDER, boxShadow: HUD_GLOW }}
      />
      <video ref={videoRef} muted autoPlay playsInline className="h-full w-full rounded-full object-cover" />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}

export default function App() {
  const logIdRef = useRef(0);
  const [cameraState, setCameraState] = useState("init");
  const [detectedColor, setDetectedColor] = useState("");
  const [countdown, setCountdown] = useState(POLL_INTERVAL_MS / 1000);
  const [logs, setLogs] = useState([{ id: 0, text: "[TARS]: System initialized. Awaiting optical lock." }]);

  const pushLog = useCallback((text) => {
    logIdRef.current += 1;
    setLogs((prev) => [...prev.slice(-12), { id: logIdRef.current, text }]);
  }, []);

  const glowColor = useMemo(() => COLOR_GLOW_MAP[detectedColor] || COLOR_GLOW_MAP.default, [detectedColor]);
  const isRevealActive = Boolean(detectedColor);

  return (
    <div className="h-screen overflow-hidden text-zinc-200">
      <div className="relative h-full overflow-hidden">
        <div className="pointer-events-none absolute inset-0 z-0" style={{ background: "radial-gradient(circle at 50% 56%, #0a0a12 0%, #000000 100%)" }} />
        <div className="pointer-events-none absolute inset-0 z-0 opacity-50 [background-image:radial-gradient(rgba(255,255,255,0.12)_0.8px,transparent_0.8px)] [background-size:3px_3px]" />

        <div className="relative z-10 mx-auto flex h-full max-w-[1480px] flex-col px-6 py-4">
          <Header />
          <main className={`mt-4 flex min-h-0 flex-1 gap-5 overflow-hidden transition-opacity duration-200 ${isRevealActive ? "opacity-0 pointer-events-none" : "opacity-100"}`}>
            <section className="w-[220px] rounded-lg bg-black/25 p-4 backdrop-blur-md" style={{ border: HUD_BORDER, boxShadow: HUD_GLOW }}>
              <h3 className="mb-3 text-xs tracking-[0.3em]" style={{ color: GOLD }}>FLIGHT DATA</h3>
              <p className="text-xs text-zinc-400">CAMERA: {cameraState.toUpperCase()}</p>
              <p className="mt-2 text-xs text-zinc-400">WORMHOLE STABILITY: 97%</p>
              <p className="mt-2 text-xs text-zinc-400">EVENT HORIZON: LOCKED</p>
            </section>

            <section className="flex min-w-0 flex-1 flex-col items-center justify-between gap-4 overflow-hidden">
              <div className="relative h-[min(46vh,430px)] w-[min(46vh,430px)] min-h-[250px] min-w-[250px]">
                <WormholeScanner onDetection={setDetectedColor} onLog={pushLog} onCameraState={setCameraState} onCountdownChange={setCountdown} />
              </div>
              <div
                className="rounded-md px-5 py-2 text-center"
                style={{
                  border: HUD_BORDER,
                  background: "rgba(0,0,0,0.35)",
                  boxShadow: HUD_GLOW,
                }}
              >
                <p className="text-[10px] tracking-[0.25em] text-zinc-400">PROBING SINGULARITY:</p>
                <motion.p
                  key={countdown}
                  initial={{ scale: 0.95, opacity: 0.75 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{
                    duration: countdown <= 1 ? 0.2 : countdown <= 2 ? 0.35 : 0.7,
                    repeat: Infinity,
                    repeatType: "reverse",
                  }}
                  className="text-2xl font-bold tracking-[0.22em]"
                  style={{
                    color: GOLD,
                    fontFamily: "'Share Tech Mono', monospace",
                    textShadow: "0 0 10px rgba(212,175,55,0.55)",
                  }}
                >
                  [{countdown}s]
                </motion.p>
              </div>
              <div className="flex flex-wrap items-center justify-center gap-3 pb-1">
                <TelemetryCard icon={Activity} label="VELOCITY" value="65 km/s" />
                <TelemetryCard icon={Shield} label="TIME DILATION" value="1.3x" />
                <TelemetryCard icon={Radio} label="SIGNAL" value="82 dBm" />
                <TelemetryCard icon={Timer} label="CORE STABILITY" value="98%" />
              </div>
            </section>

            <section className="w-[320px] min-h-0 min-w-0">
              <TarsTerminal logs={logs} />
            </section>
          </main>
        </div>

        <AnimatePresence>
          {detectedColor ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 z-50 flex flex-col items-center justify-center gap-10 bg-black/45 backdrop-blur-xl">
              <motion.div
                initial={{ opacity: 0, y: 8, filter: "blur(22px)" }}
                animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="text-center"
              >
                <motion.p
                  className="text-9xl font-black uppercase tracking-[0.24em]"
                  initial={{ letterSpacing: "0.38em", textShadow: "0 0 2px transparent" }}
                  animate={{ letterSpacing: "0.24em", textShadow: [`0 0 6px ${glowColor}`, `0 0 22px ${glowColor}, 0 0 62px ${glowColor}`] }}
                  transition={{ duration: 0.55, ease: "easeOut" }}
                  style={{ color: glowColor }}
                >
                  {detectedColor}
                </motion.p>
              </motion.div>
              <button type="button" onClick={() => setDetectedColor("")} className="rounded-md px-5 py-2 text-xs tracking-[0.3em] transition hover:scale-[1.02]" style={{ border: HUD_BORDER, color: GOLD, boxShadow: HUD_GLOW }}>
                RE-INITIALIZE SCANNER
              </button>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  );
}
