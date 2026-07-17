"""
Step 4: Build subtitles.json from two whisper transcripts.

Part 1 (Demo TTS):   real timestamps, offset = 0
Part 2 (Tutorial TTS): real timestamps, offset = PART1_DURATION_MS

USAGE:
  python build_subtitles.py --demo demo_tts_transcript.json --tutorial tts_transcript.json --offset 8380 --out subtitles.json

OUTPUT: Remotion-format subtitles.json
  [{text, startMs, endMs, tokens: [{text, fromMs, toMs}]}, ...]
"""
import json, argparse


def build_caption(word, start_ms, end_ms):
    return {
        "text": word,
        "startMs": start_ms,
        "endMs": end_ms,
        "tokens": [{"text": word, "fromMs": start_ms, "toMs": end_ms}]
    }


def build_subtitles(demo_path, tutorial_path, part2_offset_ms, out_path):
    with open(demo_path, "r", encoding="utf-8") as f:
        demo_data = json.load(f)
    with open(tutorial_path, "r", encoding="utf-8") as f:
        tutorial_data = json.load(f)

    all_captions = []

    # Part 1: Demo TTS (real timestamps, offset=0)
    print("=== Part 1: Demo TTS (real timestamps) ===")
    for w in demo_data["words"]:
        start_ms = int(w["start"] * 1000)
        end_ms = int(w["end"] * 1000)
        all_captions.append(build_caption(w["word"], start_ms, end_ms))
        print(f"  {start_ms}ms - {end_ms}ms  {w['word']}")
    print(f"  {len(demo_data['words'])} words")

    # Part 2: Tutorial TTS (real timestamps, offset by Part1 duration)
    print(f"\n=== Part 2: Tutorial TTS (offset {part2_offset_ms}ms) ===")
    for w in tutorial_data["words"]:
        start_ms = int(w["start"] * 1000) + part2_offset_ms
        end_ms = int(w["end"] * 1000) + part2_offset_ms
        all_captions.append(build_caption(w["word"], start_ms, end_ms))
        print(f"  {start_ms}ms - {end_ms}ms  {w['word']}")
    print(f"  {len(tutorial_data['words'])} words")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_captions, f, ensure_ascii=False, indent=2)

    print(f"\nTotal captions: {len(all_captions)}")
    print(f"First: {all_captions[0]['text']} @ {all_captions[0]['startMs']}-{all_captions[0]['endMs']}ms")
    print(f"Last:  {all_captions[-1]['text']} @ {all_captions[-1]['startMs']}-{all_captions[-1]['endMs']}ms")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build subtitles.json from whisper transcripts")
    parser.add_argument("--demo", required=True, help="Demo TTS transcript JSON")
    parser.add_argument("--tutorial", required=True, help="Tutorial TTS transcript JSON")
    parser.add_argument("--offset", type=int, required=True,
                        help="Part2 offset in ms (= int(PART1_DURATION * 1000))")
    parser.add_argument("--out", required=True, help="Output subtitles.json path")
    args = parser.parse_args()
    build_subtitles(args.demo, args.tutorial, args.offset, args.out)
