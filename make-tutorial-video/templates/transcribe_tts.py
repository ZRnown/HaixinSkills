"""
Step 3: Transcribe TTS audio with faster-whisper to get REAL word-level timestamps.

USAGE:
  python transcribe_tts.py --audio demo_narration_v2.wav --out demo_tts_transcript.json
  python transcribe_tts.py --audio tutorial_narration_v5.wav --out tts_transcript.json

OUTPUT: JSON {language, duration, words: [{word, start, end, probability}]}

IMPORTANT: Never use char-count estimation for subtitle timestamps.
TTS speech is uneven with pauses — only real transcription gives accurate sync.
"""
import json, os, sys, argparse

# Proxy for model download (if needed)
os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")

from faster_whisper import WhisperModel


def transcribe(audio_path, out_path, language="en"):
    print(f"Loading faster-whisper (medium)...")
    model = WhisperModel("medium", device="cpu", compute_type="int8")

    print(f"Transcribing {audio_path}...")
    segments, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=5,
        word_timestamps=True,
    )

    words = []
    for seg in segments:
        print(f"  Segment [{seg.start:.2f}s - {seg.end:.2f}s]: {seg.text}")
        for w in seg.words:
            words.append({
                "word": w.word.strip(),
                "start": w.start,
                "end": w.end,
                "probability": w.probability
            })

    print(f"\nTranscribed {len(words)} words:")
    for w in words:
        print(f"  {w['start']:.3f}s - {w['end']:.3f}s  ({w['probability']:.2f})  {w['word']}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"language": info.language, "duration": info.duration, "words": words},
                  f, ensure_ascii=False, indent=2)
    print(f"\nSaved transcript: {out_path}")
    print(f"Audio duration: {info.duration:.3f}s")

    # Warning: check for common misrecognitions
    print("\n⚠️  Check for misrecognized proper nouns (e.g. Mapopopo, DreamFace)")
    print("   Fix word text in the JSON (keep timestamps) if needed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe TTS with faster-whisper")
    parser.add_argument("--audio", required=True, help="Path to TTS audio file")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    args = parser.parse_args()
    transcribe(args.audio, args.out, args.language)
