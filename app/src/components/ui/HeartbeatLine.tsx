/**
 * HeartbeatLine.tsx
 * Donated from express-project-shine — ECG-style animated SVG.
 * Used in the LaptopPulse marketing site HeroSection.
 */
import { useEffect, useRef } from "react";

interface HeartbeatLineProps {
  color?: string;
  height?: number;
  speed?: number;
  className?: string;
}

export function HeartbeatLine({
  color = "#00d4ff",
  height = 60,
  speed = 1,
  className = "",
}: HeartbeatLineProps) {
  const pathRef = useRef<SVGPathElement>(null);
  const dotRef  = useRef<SVGCircleElement>(null);
  const frameRef = useRef<number>(0);
  const tickRef  = useRef<number>(0);

  useEffect(() => {
    const W = 700, MID = height / 2, STEP = 4;
    const POINTS = Math.ceil(W / STEP) + 2;
    const cycle = [
      0,0,0,0,0,0,0,0,
      -4,-7,-4,0,0,0,
      2,-10,30,-12,2,
      0,0,-5,-8,-5,0,
      0,0,0,0,0,0,0,0,
    ];
    const buf: number[] = new Array(POINTS).fill(0);

    function animate() {
      buf.push(cycle[tickRef.current % cycle.length]);
      if (buf.length > POINTS) buf.shift();
      tickRef.current += speed;

      let d = "";
      for (let i = 0; i < buf.length; i++) {
        const x = i * STEP;
        const y = MID + buf[i];
        d += (i === 0 ? "M" : "L") + x.toFixed(1) + "," + y.toFixed(1);
      }
      if (pathRef.current) pathRef.current.setAttribute("d", d);
      if (dotRef.current) {
        const lx = (buf.length - 1) * STEP;
        const ly = MID + buf[buf.length - 1];
        dotRef.current.setAttribute("cx", String(lx));
        dotRef.current.setAttribute("cy", String(ly));
      }
      frameRef.current = requestAnimationFrame(animate);
    }

    frameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frameRef.current);
  }, [height, speed]);

  return (
    <svg
      viewBox={`0 0 700 ${height}`}
      preserveAspectRatio="none"
      className={className}
      style={{ width: "100%", height }}
      aria-hidden="true"
    >
      <path
        ref={pathRef}
        fill="none"
        stroke={color}
        strokeWidth={2}
        style={{ filter: `drop-shadow(0 0 4px ${color})` }}
      />
      <circle
        ref={dotRef}
        r={4}
        fill={color}
        style={{ filter: `drop-shadow(0 0 6px ${color})` }}
      />
    </svg>
  );
}

export default HeartbeatLine;
