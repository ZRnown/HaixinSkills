"""
Step 1: Clean screen recording — crop red bar, jump-cut, keep app-launch segment.

USAGE: Adjust SRC, trim ranges, and crop values for your recording.
  python build_screen_recording.py

OUTPUT: screen_recording_clean.mp4 (1080x1920, 30fps, no audio)
"""
import subprocess, os, json

# ============ CONFIG — adjust for your recording ============
SRC = r"E:\Users\admin\Desktop\7月15日 (3).mp4"    # Original screen recording
OUT = "screen_recording_clean.mp4"                    # Output path

# Crop: remove top red bar (70px), then scale to 1080x1920
# Adjust based on your recording's actual red bar height
CROP_TOP = 70
CROP_H = 1836  # 1906 - 70 = 1836

# Jump cut segments (in seconds, from original recording)
# IMPORTANT: keep 0-N to preserve home screen → tap app → app launch
SEG1 = (0, 23)    # home screen → setup → start animating
SEG2 = (36, 47)   # complete → result
# ============================================================

FFMPEG = r"C:\Users\admin\.manify\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\admin\.manify\bin\ffprobe.exe"

filt = (
    f"crop=1080:{CROP_H}:0:{CROP_TOP},scale=1080:1920,"
    f"split=2[pre][post];"
    f"[pre]trim={SEG1[0]}:{SEG1[1]},setpts=PTS-STARTPTS[seg1];"
    f"[post]trim={SEG2[0]}:{SEG2[1]},setpts=PTS-STARTPTS[seg2];"
    f"[seg1][seg2]concat=n=2:v=1:a=0"
)

cmd = [
    FFMPEG, "-y",
    "-i", SRC,
    "-vf", filt,
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-an",
    "-movflags", "+faststart",
    OUT
]

print(f"Processing screen recording...")
print(f"  Crop: {CROP_TOP}px top red bar → {CROP_H}px → scale 1080x1920")
print(f"  Segments: {SEG1[0]}-{SEG1[1]}s + {SEG2[0]}-{SEG2[1]}s = {SEG1[1]-SEG1[0]+SEG2[1]-SEG2[0]}s")

result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
if result.returncode != 0:
    print("ERROR:", result.stderr[-500:])
else:
    print(f"SUCCESS: {OUT} ({os.path.getsize(OUT)} bytes)")
    r = subprocess.run([FFPROBE, "-v", "quiet", "-show_entries",
        "format=duration:stream=width,height,nb_frames", "-of", "json", OUT],
        capture_output=True, text=True)
    info = json.loads(r.stdout)
    print(f"  Resolution: {info['streams'][0]['width']}x{info['streams'][0]['height']}")
    print(f"  Duration: {info['format']['duration']}s")
    print(f"  Frames: {info['streams'][0]['nb_frames']}")
