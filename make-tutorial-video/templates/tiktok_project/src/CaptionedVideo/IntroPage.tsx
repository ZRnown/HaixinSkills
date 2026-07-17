import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { TheBoldFont } from "../load-font";

const fontFamily = TheBoldFont;

const container: React.CSSProperties = {
justifyContent: "flex-end",
alignItems: "center",
top: undefined,
bottom: 130,
};

const FONT_SIZE = 70;
const HIGHLIGHT_COLOR = "#39E508";

export const IntroSubtitlePage: React.FC<{
  readonly tokens: Array<{ text: string; fromMs: number; toMs: number }>;
  readonly pageStartMs: number;
}> = ({ tokens, pageStartMs }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const timeInMs = (frame / fps) * 1000;

  return (
    <AbsoluteFill style={container}>
      <div
        style={{
          fontSize: FONT_SIZE,
          color: "white",
          WebkitTextStroke: "5px black",
          paintOrder: "stroke",
          fontFamily,
          textTransform: "uppercase",
          fontWeight: "bold",
          lineHeight: 1.15,
          maxWidth: width * 0.92,
          textAlign: "center",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "baseline",
          gap: "0.2em",
        }}
      >
        {tokens.map((t, i) => {
          const startRel = t.fromMs - pageStartMs;
          const endRel = t.toMs - pageStartMs;
          const active = startRel <= timeInMs && endRel > timeInMs;

          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                color: active ? HIGHLIGHT_COLOR : "white",
                transform: active ? "scale(1.12)" : "scale(1)",
              }}
            >
              {t.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
