/**
 * TapIndicator.tsx
 * Animated tap indicator: pulsing ring + dot + SVG pointing hand.
 *
 * The hand's FINGERTIP is anchored exactly at (x, y).
 * Rotation happens around the fingertip so it stays on target
 * regardless of direction.
 *
 * Props:
 *   x, y       — target canvas coordinates (1080×1920 space)
 *   direction  — "down" | "up" | "left" | "right"  (default "down")
 *   size       — hand width in px (default 140, height = size × 1.6)
 *   color      — ring/dot/hand color (default #FFD600)
 */

import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

const DIRECTION_ANGLE: Record<string, number> = {
  down: 0,
  left: 90,
  up: 180,
  right: 270,
};

export const TapIndicator: React.FC<{
  readonly x: number;
  readonly y: number;
  readonly color?: string;
  readonly direction?: "down" | "up" | "left" | "right";
  readonly size?: number;
}> = ({ x, y, color = "#FFD600", direction = "down", size = 140 }) => {
  const frame = useCurrentFrame();
  const cycle = 30; // 1-second pulse at 30 fps

  // Pulsing ring
  const pulseProgress = (frame % cycle) / cycle;
  const ringScale = interpolate(pulseProgress, [0, 1], [0.8, 2.2]);
  const ringOpacity = interpolate(pulseProgress, [0, 0.7, 1], [0.8, 0.2, 0]);

  // Solid dot
  const dotScale = 1 + Math.sin(frame * 0.2) * 0.1;

  // Tapping bounce — always along the pointing direction (toward target)
  const bounce = Math.sin(frame * 0.15) * 8;

  const angle = DIRECTION_ANGLE[direction] ?? 0;
  const handHeight = size * 1.6; // viewBox aspect 100:160 = 5:8

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* Pulsing ring */}
      <div
        style={{
          position: "absolute",
          left: `${(x / 1080) * 100}%`,
          top: `${(y / 1920) * 100}%`,
          transform: `translate(-50%, -50%) scale(${ringScale})`,
          width: 100,
          height: 100,
          borderRadius: "50%",
          border: `5px solid ${color}`,
          opacity: ringOpacity,
          boxShadow: `0 0 24px ${color}`,
        }}
      />
      {/* Solid dot */}
      <div
        style={{
          position: "absolute",
          left: `${(x / 1080) * 100}%`,
          top: `${(y / 1920) * 100}%`,
          transform: `translate(-50%, -50%) scale(${dotScale})`,
          width: 40,
          height: 40,
          borderRadius: "50%",
          backgroundColor: color,
          opacity: 0.9,
          boxShadow: `0 0 14px ${color}`,
        }}
      />

    </AbsoluteFill>
  );
};
