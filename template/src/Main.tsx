import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import words from './words.json';
import {BODY, DISPLAY, GOLD, GOLD_SOFT, MUTED, NAVY, NAVY_2, RED, WHITE} from './theme';

type Word = {text: string; start: number; end: number};

// ---------- helpers ----------
const useEnter = (delay = 0) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping: 14, mass: 0.6}});
};

const Pop: React.FC<{delay?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({
  delay = 0,
  children,
  style,
}) => {
  const s = useEnter(delay);
  return (
    <div
      style={{
        transform: `scale(${interpolate(s, [0, 1], [0.6, 1])}) translateY(${interpolate(s, [0, 1], [40, 0])}px)`,
        opacity: s,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const Big: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({
  children,
  size = 150,
  color = WHITE,
}) => (
  <div
    style={{
      fontFamily: DISPLAY,
      fontSize: size,
      lineHeight: 1.02,
      color,
      textAlign: 'center',
      textTransform: 'uppercase',
      letterSpacing: 2,
    }}
  >
    {children}
  </div>
);

const Label: React.FC<{children: React.ReactNode; color?: string; size?: number}> = ({
  children,
  color = GOLD,
  size = 44,
}) => (
  <div
    style={{
      fontFamily: BODY,
      fontWeight: 800,
      fontSize: size,
      color,
      letterSpacing: 8,
      textTransform: 'uppercase',
      textAlign: 'center',
    }}
  >
    {children}
  </div>
);

const Stage: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill
    style={{
      justifyContent: 'center',
      alignItems: 'center',
      paddingTop: 120,
      paddingBottom: 560,
      gap: 36,
      flexDirection: 'column',
    }}
  >
    {children}
  </AbsoluteFill>
);

// ---------- background & frame ----------
const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 90) * 60;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% ${35 + drift / 20}%, ${NAVY_2} 0%, ${NAVY} 62%)`,
      }}
    >
      <svg width={1080} height={1920} style={{position: 'absolute', opacity: 0.07}}>
        {/* faint court lines */}
        <circle cx={540} cy={960 + drift} r={260} stroke={WHITE} strokeWidth={6} fill="none" />
        <line x1={0} y1={960 + drift} x2={1080} y2={960 + drift} stroke={WHITE} strokeWidth={6} />
        <rect x={290} y={-40 + drift} width={500} height={520} stroke={WHITE} strokeWidth={6} fill="none" />
        <rect x={290} y={1440 + drift} width={500} height={520} stroke={WHITE} strokeWidth={6} fill="none" />
      </svg>
    </AbsoluteFill>
  );
};

const Header: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      top: 150,
      left: 0,
      right: 0,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      gap: 18,
    }}
  >
    <div style={{fontFamily: DISPLAY, fontSize: 52, color: GOLD, letterSpacing: 4}}>E2A</div>
    <div style={{width: 3, height: 34, background: GOLD, opacity: 0.6}} />
    <div style={{fontFamily: BODY, fontWeight: 600, fontSize: 30, color: MUTED, letterSpacing: 6}}>
      BASKETBALL STORIES
    </div>
  </div>
);

// ---------- captions ----------
const chunkWords = (ws: Word[]) => {
  const chunks: Word[][] = [];
  let cur: Word[] = [];
  const chars = (c: Word[]) => c.reduce((n, x) => n + x.text.length + 1, 0);
  ws.forEach((w, i) => {
    if (cur.length && chars(cur) + w.text.length > 20) {
      chunks.push(cur);
      cur = [];
    }
    cur.push(w);
    const next = ws[i + 1];
    const endsSentence = /[.,?!]$/.test(w.text);
    const gap = next ? next.start - w.end > 0.45 : true;
    if (cur.length >= 5 || endsSentence || gap) {
      chunks.push(cur);
      cur = [];
    }
  });
  if (cur.length) chunks.push(cur);
  return chunks;
};

const CHUNKS = chunkWords(words as Word[]);

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const idx = CHUNKS.findIndex((c, i) => {
    const start = c[0].start;
    const nextStart = CHUNKS[i + 1] ? CHUNKS[i + 1][0].start : c[c.length - 1].end + 1.2;
    return t >= start && t < nextStart;
  });
  if (idx < 0) return null;
  const chunk = CHUNKS[idx];
  const local = frame - Math.round(chunk[0].start * fps);
  const s = spring({frame: local, fps, config: {damping: 16, mass: 0.5}});
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        right: 70,
        top: 1330,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '0 22px',
        transform: `scale(${interpolate(s, [0, 1], [0.85, 1])})`,
        opacity: s,
      }}
    >
      {chunk.map((w, i) => {
        const active = t >= w.start && t < w.end + 0.08;
        return (
          <span
            key={i}
            style={{
              fontFamily: DISPLAY,
              fontSize: 92,
              lineHeight: 1.15,
              textTransform: 'uppercase',
              color: active ? GOLD : WHITE,
              textShadow: '0 6px 18px rgba(0,0,0,0.55)',
              WebkitTextStroke: '2px rgba(0,0,0,0.35)',
            }}
          >
            {w.text.replace(/[.,]$/, '')}
          </span>
        );
      })}
    </div>
  );
};

// ---------- reusable graphics ----------
const Clock: React.FC<{value: string; flash?: boolean; color?: string}> = ({value, flash, color = RED}) => {
  const frame = useCurrentFrame();
  const on = flash ? Math.floor(frame / 8) % 2 === 0 : true;
  return (
    <div
      style={{
        fontFamily: DISPLAY,
        fontSize: 230,
        color,
        background: '#05080F',
        border: `6px solid ${GOLD}`,
        borderRadius: 28,
        padding: '6px 54px',
        opacity: on ? 1 : 0.25,
        letterSpacing: 6,
        boxShadow: `0 0 60px ${GOLD_SOFT}`,
      }}
    >
      {value}
    </div>
  );
};

const Scoreboard: React.FC<{
  left: [string, number];
  right: [string, number];
  clock?: string;
  winner?: 'left' | 'right';
}> = ({left, right, clock, winner}) => {
  const team = (name: string, score: number, isWinner: boolean) => (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', width: 380}}>
      <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 52, color: isWinner ? GOLD : WHITE, letterSpacing: 6}}>
        {name}
      </div>
      <div style={{fontFamily: DISPLAY, fontSize: 250, color: isWinner ? GOLD : WHITE, lineHeight: 1}}>{score}</div>
    </div>
  );
  return (
    <div
      style={{
        background: 'rgba(5,8,15,0.85)',
        border: `5px solid ${GOLD}`,
        borderRadius: 36,
        padding: '36px 30px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 10,
      }}
    >
      <div style={{display: 'flex', alignItems: 'center'}}>
        {team(left[0], left[1], winner === 'left')}
        <div style={{fontFamily: DISPLAY, fontSize: 120, color: MUTED}}>–</div>
        {team(right[0], right[1], winner === 'right')}
      </div>
      {clock ? (
        <div style={{fontFamily: DISPLAY, fontSize: 90, color: RED, letterSpacing: 4}}>{clock}</div>
      ) : null}
    </div>
  );
};

// ---------- scenes ----------
const S1Hook: React.FC = () => (
  <Stage>
    <Pop>
      <Clock value="0:03" />
    </Pop>
    <Pop delay={18}>
      <Big size={130}>Played</Big>
    </Pop>
    <Pop delay={40}>
      <Big size={200} color={GOLD}>
        3 times
      </Big>
    </Pop>
  </Stage>
);

const S2Munich: React.FC = () => (
  <Stage>
    <Pop>
      <Label>Olympic final</Label>
    </Pop>
    <Pop delay={6}>
      <Big size={190}>Munich</Big>
    </Pop>
    <Pop delay={14}>
      <Big size={220} color={GOLD}>
        1972
      </Big>
    </Pop>
    <Pop delay={110}>
      <Big size={110}>USA vs USSR</Big>
    </Pop>
  </Stage>
);

const S3Streak: React.FC = () => {
  const frame = useCurrentFrame();
  const n = Math.round(interpolate(frame, [80, 125], [0, 63], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  return (
    <Stage>
      <Pop>
        <Label>Olympic record of the USA</Label>
      </Pop>
      <Pop delay={4}>
        <Big size={300} color={GOLD}>
          {n}–0
        </Big>
      </Pop>
      <Pop delay={90}>
        <Big size={100}>Straight wins</Big>
      </Pop>
    </Stage>
  );
};

const S4Lead: React.FC = () => (
  <Stage>
    <Pop>
      <Label>Free throws: Doug Collins</Label>
    </Pop>
    <Pop delay={8}>
      <Scoreboard left={['USA', 50]} right={['USSR', 49]} clock="0:03" winner="left" />
    </Pop>
  </Stage>
);

const S5Timeout: React.FC = () => (
  <Stage>
    <Pop>
      <Clock value="0:01" />
    </Pop>
    <Pop delay={20}>
      <Big size={170}>Stop!</Big>
    </Pop>
    <Pop delay={95}>
      <Big size={120} color={GOLD}>
        “Timeout?”
      </Big>
    </Pop>
  </Stage>
);

const S6Replay: React.FC = () => (
  <Stage>
    <Pop>
      <Label>Attempt 2</Label>
    </Pop>
    <Pop delay={6}>
      <Clock value="0:03" />
    </Pop>
    <Pop delay={95}>
      <Big size={130} color={GOLD}>
        Horn! USA celebrate
      </Big>
    </Pop>
  </Stage>
);

const S7Again: React.FC = () => (
  <Stage>
    <Pop>
      <Big size={120}>Clock never reset</Big>
    </Pop>
    <Pop delay={88}>
      <Label>Attempt 3</Label>
    </Pop>
    <Pop delay={92}>
      <Clock value="0:03" flash />
    </Pop>
  </Stage>
);

const S8Pass: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [8, 70], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  // quadratic bezier from bottom baseline to top hoop
  const x0 = 540, y0 = 1080, cx = 900, cy = 520, x1 = 540, y1 = 200;
  const bx = (1 - p) ** 2 * x0 + 2 * (1 - p) * p * cx + p ** 2 * x1;
  const by = (1 - p) ** 2 * y0 + 2 * (1 - p) * p * cy + p ** 2 * y1;
  const scored = frame > 112;
  return (
    <AbsoluteFill style={{alignItems: 'center'}}>
      <svg width={1080} height={1300} style={{position: 'absolute', top: 120}}>
        <rect x={190} y={150} width={700} height={980} rx={10} stroke={GOLD} strokeWidth={6} fill="rgba(5,8,15,0.6)" />
        <line x1={190} y1={640} x2={890} y2={640} stroke={GOLD} strokeWidth={4} opacity={0.6} />
        <circle cx={540} cy={640} r={90} stroke={GOLD} strokeWidth={4} fill="none" opacity={0.6} />
        <circle cx={540} cy={200} r={22} stroke={RED} strokeWidth={7} fill="none" />
        <circle cx={540} cy={1080} r={22} stroke={WHITE} strokeWidth={5} fill="none" opacity={0.4} />
        <path
          d={`M ${x0} ${y0} Q ${cx} ${cy} ${x1} ${y1}`}
          stroke={WHITE}
          strokeWidth={5}
          strokeDasharray="18 16"
          fill="none"
          opacity={0.5}
        />
        <circle cx={bx} cy={by} r={28} fill="#E8742C" stroke="#7A3510" strokeWidth={4} />
      </svg>
      <div style={{position: 'absolute', top: 1060, width: '100%'}}>
        {scored ? (
          <Pop>
            <Big size={150} color={GOLD}>
              Belov scores
            </Big>
          </Pop>
        ) : (
          <Pop delay={4}>
            <Label size={48}>Full-court pass</Label>
          </Pop>
        )}
      </div>
    </AbsoluteFill>
  );
};

const S9Final: React.FC = () => (
  <Stage>
    <Pop>
      <Label>Final</Label>
    </Pop>
    <Pop delay={4}>
      <Scoreboard left={['USSR', 51]} right={['USA', 50]} winner="left" />
    </Pop>
    <Pop delay={50}>
      <Big size={120} color={GOLD}>
        Gold: USSR
      </Big>
    </Pop>
  </Stage>
);

const S10Medal: React.FC = () => {
  const stamp = useEnter(40);
  return (
    <Stage>
      <Pop>
        <svg width={420} height={480} viewBox="0 0 420 480">
          <polygon points="120,0 190,0 230,180 160,180" fill="#1E4E9C" />
          <polygon points="300,0 230,0 190,180 260,180" fill="#B3262E" />
          <defs>
            <radialGradient id="silver" cx="40%" cy="35%" r="70%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="55%" stopColor="#C9CED6" />
              <stop offset="100%" stopColor="#8A919C" />
            </radialGradient>
          </defs>
          <circle cx={210} cy={310} r={150} fill="url(#silver)" stroke="#6E7580" strokeWidth={8} />
          <circle cx={210} cy={310} r={112} fill="none" stroke="#9AA1AB" strokeWidth={5} />
          <text x={210} y={335} textAnchor="middle" fontFamily={DISPLAY} fontSize={78} fill="#5B616B">
            1972
          </text>
        </svg>
      </Pop>
      <div
        style={{
          transform: `rotate(-12deg) scale(${interpolate(stamp, [0, 1], [2.2, 1])})`,
          opacity: stamp,
          border: `10px solid ${RED}`,
          borderRadius: 20,
          padding: '4px 40px',
          marginTop: -40,
        }}
      >
        <Big size={150} color={RED}>
          Refused
        </Big>
      </div>
    </Stage>
  );
};

const S11Question: React.FC = () => (
  <Stage>
    <Pop>
      <Big size={140}>Would you</Big>
    </Pop>
    <Pop delay={8}>
      <Big size={140}>have taken</Big>
    </Pop>
    <Pop delay={16}>
      <Big size={170} color={GOLD}>
        the silver?
      </Big>
    </Pop>
    <Pop delay={30}>
      <div style={{fontFamily: BODY, fontWeight: 600, fontSize: 38, color: MUTED, letterSpacing: 4}}>
        @e2a.basketball
      </div>
    </Pop>
  </Stage>
);

const SCENES: [number, number, React.FC][] = [
  [0, 118, S1Hook],
  [118, 318, S2Munich],
  [318, 486, S3Streak],
  [486, 660, S4Lead],
  [660, 813, S5Timeout],
  [813, 988, S6Replay],
  [988, 1152, S7Again],
  [1152, 1311, S8Pass],
  [1311, 1425, S9Final],
  [1425, 1578, S10Medal],
  [1578, 1660, S11Question],
];

export const Main: React.FC = () => {
  const {durationInFrames} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: NAVY}}>
      <Background />
      {SCENES.map(([from, to, Scene], i) => (
        <Sequence key={i} from={from} durationInFrames={to - from}>
          <Scene />
        </Sequence>
      ))}
      <Header />
      <Captions />
      <Audio src={staticFile('vo.mp3')} />
      <Audio
        src={staticFile('music.mp3')}
        loop
        volume={(f) =>
          interpolate(f, [0, 20, durationInFrames - 45, durationInFrames], [0, 0.13, 0.13, 0], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          })
        }
      />
    </AbsoluteFill>
  );
};
