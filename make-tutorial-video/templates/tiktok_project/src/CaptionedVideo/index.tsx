import { Caption } from "@remotion/captions";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useVideoConfig,
} from "remotion";
import { loadFont } from "../load-font";
import { IntroSubtitlePage } from "./IntroPage";
import { TapIndicator } from "./TapIndicator";

// Total video duration: ~31.8s at 30fps = 953 frames
const TOTAL_DURATION_FRAMES = 1085;

// Tap indicator positions (final canvas coordinates after crop+scale)
// Source was 1080x1906, cropped top 52px → 1080x1854, scaled to 1080x1920 (scale=1.0356)
// finalY = (sourceY - 52) * 1.0356
// Part 2 starts at 8.38s = 251 frames. Screen recording is jump-cut (20s → 11s result). Final time = source + 8.38s.
const TAP_POINTS = [
     // 1. Tap Baby Mapopopo (Trend Act row, source ~3.2s → final ~11.58s = 347)
   { x: 792, y: 561, from: 347, dur: 60, direction: "down" as const },
   // 2. Tap avatar upload slot (source ~7s → final ~15.38s = 461)
   { x: 540, y: 950, from: 461, dur: 60, direction: "down" as const },
   // 3. Tap photo in album (source ~8s → final ~16.38s = 491)
   { x: 644, y: 671, from: 491, dur: 45, direction: "down" as const },
   // 4. Tap Create button (source ~11s → final ~19.38s = 581)
   { x: 540, y: 1750, from: 581, dur: 60, direction: "down" as const },
   // 5. Tap Lip-Sync toggle (source ~23s → final ~31.38s = 941) — top-right, hand from below
   { x: 920, y: 150, from: 941, dur: 50, direction: "up" as const },
   // 6. Tap HD Enhance toggle (source ~24s → final ~32.38s = 971) — top-right, hand from below
   { x: 920, y: 250, from: 971, dur: 50, direction: "up" as const },
];interface IntroPage {
  tokens: Array<{ text: string; fromMs: number; toMs: number }>;
  startMs: number;
  endMs: number;
}

// subtitles.json is a flat array of {text, startMs, endMs}, NOT nested Caption objects
interface FlatWord {
  text: string;
  startMs: number;
  endMs: number;
}

function buildIntroPages(words: FlatWord[]): IntroPage[] {
  const pages: IntroPage[] = [];
  let currentTokens: Array<{ text: string; fromMs: number; toMs: number }> = [];

  const MAX_WORDS = 8;
  const GAP_BREAK_MS = 2000;

  for (const wt of words) {
    // Time gap check
    if (currentTokens.length > 0) {
      const prevEnd = currentTokens[currentTokens.length - 1].toMs;
      if (wt.startMs - prevEnd > GAP_BREAK_MS) {
        pages.push({
          tokens: currentTokens,
          startMs: currentTokens[0].fromMs,
          endMs: currentTokens[currentTokens.length - 1].toMs,
        });
        currentTokens = [];
      }
    }
    currentTokens.push({ text: wt.text, fromMs: wt.startMs, toMs: wt.endMs });
    if (currentTokens.length >= MAX_WORDS) {
      pages.push({
        tokens: currentTokens,
        startMs: currentTokens[0].fromMs,
        endMs: currentTokens[currentTokens.length - 1].toMs,
      });
      currentTokens = [];
    }
  }
  if (currentTokens.length > 0) {
    pages.push({
      tokens: currentTokens,
      startMs: currentTokens[0].fromMs,
      endMs: currentTokens[currentTokens.length - 1].toMs,
    });
  }
  return pages;
}

export const CaptionedVideo: React.FC<{
  src: string;
}> = ({ src }) => {
  const [captions, setCaptions] = useState<FlatWord[]>([]);
  const { fps } = useVideoConfig();

  const subtitlesFile = staticFile("subtitles.json");

  const fetchSubtitles = useCallback(async () => {
    try {
      await loadFont();
      const res = await fetch(subtitlesFile);
      const data = (await res.json()) as FlatWord[];
      setCaptions(data);
    } catch (e) {
      console.error("Failed to fetch subtitles", e);
    }
  }, []);

  useEffect(() => {
    fetchSubtitles();
  }, [fetchSubtitles]);

  const pages = useMemo(() => {
    return buildIntroPages(captions);
  }, [captions]);

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <AbsoluteFill>
        <OffthreadVideo
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
          src={src}
        />
      </AbsoluteFill>

      {/* Word-by-word highlighted English captions (TikTok style) */}
      {pages.map((page, index) => {
        const nextPage = pages[index + 1] ?? null;
        const subtitleStartFrame = Math.round((page.startMs / 1000) * fps);
        const subtitleEndFrame = nextPage
          ? Math.round((nextPage.startMs / 1000) * fps)
          : TOTAL_DURATION_FRAMES;
        const durationInFrames = subtitleEndFrame - subtitleStartFrame;
        if (durationInFrames <= 0) return null;

        return (
          <Sequence
            key={`caption-${index}`}
            from={subtitleStartFrame}
            durationInFrames={durationInFrames}
          >
            <IntroSubtitlePage tokens={page.tokens} pageStartMs={page.startMs} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
