"""
Step 2: Build base video — demo + screen recording + 3 audio tracks (FFmpeg).

Structure:
  Part 1 (0 ~ PART1_DURATION): Demo video loop + "Create with XXX" text + Demo TTS + Demo audio @0.7
  Part 2 (PART1_DURATION ~ END): Screen recording + Tutorial TTS (delayed by PART1_DURATION)

USAGE: Adjust the paths and APP_NAME below.
  python build_base.py

OUTPUT: base_video.mp4 + video_duration.txt
"""
import subprocess, json, os

# ============ CONFIG — adjust for your project ============
DEMO_VIDEO = "attachments/Baby_Mapopopo.mp4"       # Demo effect video
SCREEN_RECORD = "screen_recording_clean.mp4"        # Step 1 output
DEMO_TTS = "demo_narration_v2.wav"                  # Demo TTS audio
TUT_TTS = "tutorial_narration_v5.wav"               # Tutorial TTS audio
OUT_VIDEO = "base_video.mp4"

APP_NAME = "DreamFace"                              # Shown as "Create with {APP_NAME}"
# ============================================================

FFMPEG = r"C:\Users\admin\.manify\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\admin\.manify\bin\ffprobe.exe"

def get_duration(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "json", path], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

DEMO_DURATION = get_duration(DEMO_VIDEO)
SCREEN_DURATION = get_duration(SCREEN_RECORD)
DEMO_TTS_DURATION = get_duration(DEMO_TTS)
TUT_TTS_DURATION = get_duration(TUT_TTS)

PART1_DURATION = DEMO_TTS_DURATION + 2.0           # Demo TTS + 2s gap
TOTAL_DURATION = PART1_DURATION + TUT_TTS_DURATION + 0.15
PART2_DURATION = TOTAL_DURATION - PART1_DURATION
DELAY_MS = int(PART1_DURATION * 1000)
TOTAL_FRAMES = int(round(TOTAL_DURATION * 30))

print(f"Part 1 (demo):     {PART1_DURATION:.3f}s")
print(f"Part 2 (tutorial): {PART2_DURATION:.3f}s")
print(f"Total:             {TOTAL_DURATION:.3f}s ({TOTAL_FRAMES} frames)")

# FFmpeg filter_complex
vfilter = (
    f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
    f"drawtext=text='Create with {APP_NAME}':fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
    f"fontcolor=white@0.85:fontsize=56:x=(w-text_w)/2:y=h-text_h-40:"
    f"shadowcolor=black@0.6:shadowx=2:shadowy=2,"
    f"setsar=1,setpts=PTS-STARTPTS,trim=duration={PART1_DURATION:.3f}[demo];"
    f"[1:v]setsar=1,format=yuv420p,setpts=PTS-STARTPTS,trim=duration={PART2_DURATION:.3f}[screen];"
    f"[demo][screen]concat=n=2:v=1:a=0[outv];"
    f"[0:a]aloop=loop=-1:size=451584,atrim=0:{TOTAL_DURATION:.3f},asetpts=PTS-STARTPTS,volume=0.7[demo_a];"
    f"[2:a]atrim=0:{TOTAL_DURATION:.3f},asetpts=PTS-STARTPTS,volume=1.0[demo_tts];"
    f"[3:a]adelay={DELAY_MS}|{DELAY_MS},atrim=0:{TOTAL_DURATION:.3f},asetpts=PTS-STARTPTS,volume=1.0[tut_tts];"
    f"[demo_a][demo_tts][tut_tts]amix=inputs=3:duration=longest:normalize=0[outa];"
)

cmd = [
    FFMPEG, "-y",
    "-stream_loop", "-1", "-i", DEMO_VIDEO,
    "-i", SCREEN_RECORD,
    "-i", DEMO_TTS,
    "-i", TUT_TTS,
    "-filter_complex", vfilter,
    "-map", "[outv]", "-map", "[outa]",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
    "-pix_fmt", "yuv420p", "-r", "30",
    "-c:a", "aac", "-b:a", "192k",
    "-t", f"{TOTAL_DURATION:.3f}",
    OUT_VIDEO
]

print(f"\nBuilding base video...")
r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
if r.returncode != 0:
    print("FFMPEG STDERR (last 3000 chars):")
    print(r.stderr[-3000:])
else:
    print("SUCCESS!")
    with open("video_duration.txt", "w") as f:
        f.write(f"TOTAL_DURATION_S={TOTAL_DURATION:.4f}\n")
        f.write(f"TOTAL_FRAMES={TOTAL_FRAMES}\n")
        f.write(f"PART1_S={PART1_DURATION:.4f}\n")
        f.write(f"PART2_S={PART2_DURATION:.4f}\n")
    print(f"Total frames: {TOTAL_FRAMES}")
    print(f"durationInFrames for Root.tsx: {TOTAL_FRAMES}")
