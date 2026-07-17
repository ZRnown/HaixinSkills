import { spring, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import React from "react";
import { AbsoluteFill } from "remotion";
import { TheBoldFont } from "../load-font";

const fontFamily = TheBoldFont;

const container: React.CSSProperties = {
  justifyContent: "center",
  alignItems: "center",
  top: 650,
  bottom: undefined,
  flexDirection: "column",
  gap: 16,
};

export const BilingualSubtitlePage: React.FC<{
  readonly spanish: string;
  readonly english: string;
}> = ({ spanish, english }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame,
    fps,
    config: {
      damping: 200,
    },
    durationInFrames: 5,
  });

  const capsuleStyle: React.CSSProperties = {
    backgroundColor: "white",
    borderRadius: 80,
    paddingTop: 20,
    paddingBottom: 20,
    paddingLeft: 56,
    paddingRight: 56,
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    boxShadow: "0 6px 20px rgba(0,0,0,0.35)",
    transform: `scale(${interpolate(enter, [0, 1], [0.8, 1])})`,
    opacity: interpolate(enter, [0, 1], [0, 1]),
  };

  const spanishStyle: React.CSSProperties = {
    fontSize: 72,
    color: "#FFD700",
    fontFamily,
    textTransform: "uppercase",
    fontWeight: "bold",
    WebkitTextStroke: "3px black",
    paintOrder: "stroke",
  };

  const englishStyle: React.CSSProperties = {
    fontSize: 60,
    color: "#000000",
    fontFamily,
    textTransform: "uppercase",
    fontWeight: "bold",
  };

  return (
    <AbsoluteFill style={container}>
      <div style={capsuleStyle}>
        <span style={spanishStyle}>{spanish}</span>
      </div>
      <div style={capsuleStyle}>
        <span style={englishStyle}>{english}</span>
      </div>
    </AbsoluteFill>
  );
};
