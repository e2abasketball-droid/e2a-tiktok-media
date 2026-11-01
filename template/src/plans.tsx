import React from 'react';
import {useAbsT, Big, Board, Count, CourtSpec, GOLD, MUTED, NAVY, Plan, Pop, Popup, RED, Scene, Stage, Tag, Track, WHITE, Word, makeT, Arrow, BALL} from './Daily';

const sc = (from: number, to: number, node: React.ReactNode): Scene => ({from, to, node});
const END = (words: Word[]) => words[words.length - 1].end + 1.5;

const Lines: React.FC<{tag?: string; lines: {t: string; size?: number; color?: string; at?: number}[]; foot?: string}> = ({tag, lines, foot}) => (
  <Stage>
    {tag && <Pop><Tag>{tag}</Tag></Pop>}
    {lines.map((l, i) => (
      <Pop key={i} at={l.at ?? 0.12 * (i + 1)}><Big size={l.size ?? 130} color={l.color}>{l.t}</Big></Pop>
    ))}
    {foot && <Pop at={0.7}><Tag color={MUTED} size={34}>{foot}</Tag></Pop>}
  </Stage>
);

// ---------------------------------------------------------------- V1 Miller
export const plan1 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tDrain = T('Reggie Miller drains');
  const tSteal = T('Then the Knicks');
  const tStep = T('He steps back');
  const tTie = T('Tie game');
  const tFt = T('Miller grabs');
  const tSink = T('and sinks two more', 0) ;
  const tRecap = T('In eight point nine');
  const tWin = T('The Pacers win');
  const tVill = T('Miller was already');
  const tQ = T('Has any player');
  const scores: [number, number][] = [[0, 99], [tDrain + 1.0, 102], [tStep + 1.2, 105], [tSink + 0.2, 106], [tSink + 0.9, 107]];
  return {
    sub: 'BASKETBALL STORIES',
    scenes: [
      sc(0, T('May seventh'), (
        <Stage>
          <Pop><Count to={8} start={0.1} dur={0.5} dec={0} size={300} /></Pop>
          <Pop at={0.1}><Tag size={56}>Points</Tag></Pop>
          <Pop at={T('Eight point nine') - 0.0}><Big size={190} color={WHITE}>in 8.9 sec</Big></Pop>
        </Stage>
      )),
      sc(T('May seventh'), T('The Knicks lead'), <Lines tag="May 7, 1995" lines={[{t: 'Game 1'}, {t: 'East Semifinals', size: 100, color: GOLD}]} foot="Madison Square Garden" />),
      sc(T('The Knicks lead'), tRecap, (
        <Stage>
          <Board
            label="Pacers at Knicks · Game 1"
            rows={[
              {name: 'KNICKS', kf: [[0, 105]], color: WHITE},
              {name: 'PACERS', kf: scores, color: GOLD},
            ]}
            clock={[tDrain, tSink + 1.0, 8.9]}
          />
        </Stage>
      )),
      sc(tRecap, tVill, (
        <Stage>
          <Pop><Tag>Final</Tag></Pop>
          <Board rows={[{name: 'KNICKS', kf: [[0, 105]], color: WHITE}, {name: 'PACERS', kf: [[0, 107]], color: GOLD}]} />
          <Pop at={0.4}><Big size={96} color={GOLD}>8 pts · 8.9 sec</Big></Pop>
        </Stage>
      )),
      sc(tVill, tQ, <Lines tag="Miller vs New York" lines={[{t: 'The Garden’s', size: 120}, {t: 'Greatest Villain', size: 120, color: GOLD}]} />),
      sc(tQ, END(w), <Lines lines={[{t: 'Silenced an arena', size: 118}, {t: 'faster?', size: 150, color: GOLD}]} foot="Comment your answer" />),
    ],
    overlays: (
      <>
        <Popup at={tDrain + 0.9} text="+3" />
        <Popup at={tSteal + 0.2} text="STEAL" color={WHITE} />
        <Popup at={tStep + 1.1} text="+3 · TIED" />
        <Popup at={tTie + 1.4} text="MISSED ×2" color={RED} />
        <Popup at={tFt + 0.4} text="+1" />
        <Popup at={tSink + 0.9} text="+1" />
      </>
    ),
  };
};

// ---------------------------------------------------------------- V3 Mills
export const plan3 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tPatty = T('And Patty Mills');
  const tLead = T('The Boomers lead');
  const tFight = T('Slovenia fights back');
  const tFinal = T('The final score');
  const tFirst = T('The first Olympic');
  const tQ = T('Where does this');
  return {
    sub: 'BASKETBALL STORIES',
    scenes: [
      sc(0, T('Tokyo'), (
        <Stage>
          <Pop><Tag>Boomers · Olympic medals</Tag></Pop>
          <Pop at={0.2}><Big size={380} color={GOLD}>0</Big></Pop>
          <Pop at={T('Not once')}><Big size={100}>in 65 years</Big></Pop>
        </Stage>
      )),
      sc(T('Tokyo'), tPatty, <Lines tag="Tokyo 2021" lines={[{t: 'Bronze Medal Game'}, {t: 'Australia v Slovenia', size: 96, color: GOLD}]} foot="Saitama Super Arena" />),
      sc(tPatty, tLead, (
        <Stage>
          <Pop><Tag>Patty Mills</Tag></Pop>
          <div style={{display: 'flex', gap: 70, alignItems: 'flex-end'}}>
            <div style={{textAlign: 'center'}}><Count to={42} start={T('Forty-two') } dur={0.9} size={300} /><Tag size={44}>Points</Tag></div>
            <div style={{textAlign: 'center'}}><Count to={9} start={T('Nine assists')} dur={0.5} size={300} color={WHITE} /><Tag size={44} color={WHITE}>Assists</Tag></div>
          </div>
        </Stage>
      )),
      sc(tLead, tFinal, (
        <Stage>
          <Pop><Tag>Fourth quarter</Tag></Pop>
          <Board
            rows={[
              {name: 'LEAD', kf: [[0, 14]], color: GOLD},
            ]}
          />
          <Pop at={tFight - tLead}><Big size={96} color={WHITE}>Slovenia within 3</Big></Pop>
          <Pop at={T('But every time') - tLead}><Big size={96} color={GOLD}>Mills answers</Big></Pop>
        </Stage>
      )),
      sc(tFinal, tFirst, (
        <Stage>
          <Pop><Tag>Final</Tag></Pop>
          <Board rows={[{name: 'AUSTRALIA', kf: [[0, 107]], color: GOLD}, {name: 'SLOVENIA', kf: [[0, 93]], color: WHITE}]} />
        </Stage>
      )),
      sc(tFirst, tQ, (
        <Stage>
          <Pop><Tag>First Olympic medal</Tag></Pop>
          <svg width={760} height={520} viewBox="0 0 760 520">
            <rect x={30} y={220} width={210} height={300} fill="rgba(255,255,255,0.18)" />
            <rect x={275} y={80} width={210} height={440} fill="rgba(255,255,255,0.28)" />
            <rect x={520} y={300} width={210} height={220} fill={GOLD} />
            <text x={625} y={420} textAnchor="middle" fontFamily="Anton" fontSize={120} fill={NAVY}>3</text>
            <circle cx={625} cy={225} r={52} fill="#B5773A" stroke={GOLD} strokeWidth={8} />
          </svg>
          <Pop at={0.3}><Big size={100}>Boomers history</Big></Pop>
        </Stage>
      )),
      sc(tQ, END(w), <Lines lines={[{t: 'Greatest moment in', size: 96}, {t: 'Australian sport?', size: 120, color: GOLD}]} foot="Comment your answer" />),
    ],
  };
};

// ------------------------------------------------------------- V5 Psychology
const FreeThrow: React.FC<{words: Word[]}> = ({words}) => {
  const T = makeT(words);
  const tE = T('Elbow');
  const tW = T('Wrist');
  const tF = T('Follow-through');
  const cx = 540, cy = 760;
  const chips: [number, string, number, number][] = [[tE, 'ELBOW', -300, -230], [tW, 'WRIST', 300, -170], [tF, 'FOLLOW-THROUGH', 0, 270]];
  return (
    <Stage>
      <svg width={900} height={900} viewBox="0 0 900 900" style={{position: 'absolute', top: 300}}>
        <circle cx={450} cy={450} r={110} fill={BALL} stroke="#7A3B10" strokeWidth={8} />
        <path d="M340 450 H560 M450 340 V560" stroke="#7A3B10" strokeWidth={6} />
      </svg>
      <ChipLayer chips={chips} cx={cx} cy={cy} />
    </Stage>
  );
};
const ChipLayer: React.FC<{chips: [number, string, number, number][]; cx: number; cy: number}> = ({chips, cx, cy}) => {
  const t = useAbsT();
  return (
    <>
      {chips.map(([at, label, dx, dy], i) => {
        if (t < at) return null;
        const k = Math.min(1, (t - at) / 0.3);
        return (
          <div key={i} style={{position: 'absolute', left: cx + dx, top: cy + dy, transform: `translate(-50%,-50%) scale(${0.6 + 0.4 * k})`, opacity: k, background: GOLD, color: NAVY, fontFamily: 'Anton', fontSize: 70, padding: '8px 34px', borderRadius: 40}}>
            {label}
          </div>
        );
      })}
    </>
  );
};

export const plan5 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tPsy = T('Psychologists call');
  const tLeading = T('One leading');
  const tStakes = T('When the stakes');
  const tBut = T('But a skill');
  const tPaying = T('Paying close');
  const tRes = T('Research by');
  const tHelp = T('So what can help');
  const tBreath = T('One deep breath');
  const tCue = T('One simple cue');
  const tShoot = T('Then shoot');
  const tNo = T('It is no guarantee');
  const tQ = T('What is your');
  return {
    sub: 'MIND GAME',
    scenes: [
      sc(0, tPsy, (
        <Stage>
          <Pop><Tag>Free throw</Tag></Pop>
          <Pop at={0.2}><Big size={250} color={GOLD}>100×</Big></Pop>
          <Pop at={0.5}><Big size={86}>made in practice</Big></Pop>
        </Stage>
      )),
      sc(tPsy, tLeading, <Lines tag="Psychology" lines={[{t: 'Choking', size: 190, color: GOLD}, {t: 'under pressure', size: 100}]} />),
      sc(tLeading, tStakes, <Lines tag="One leading explanation" lines={[{t: 'Explicit', size: 170, color: GOLD}, {t: 'Monitoring', size: 170}]} />),
      sc(tStakes, tBut, <FreeThrow words={w} />),
      sc(tBut, tRes, (
        <Stage>
          <Pop><Big size={84} color={GOLD}>Practised skill</Big></Pop>
          <Pop at={0.2}><Big size={96}>runs on feel</Big></Pop>
          <Pop at={tPaying - tBut}><Big size={84} color={RED}>Every step watched</Big></Pop>
          <Pop at={tPaying - tBut + 0.2}><Big size={96}>can disrupt flow</Big></Pop>
        </Stage>
      )),
      sc(tRes, tHelp, <Lines tag="Sian Beilock & colleagues" lines={[{t: 'Supports the idea', size: 100}, {t: 'Results vary', size: 120, color: GOLD}]} foot="by athlete and task" />),
      sc(tHelp, tNo, (
        <Stage>
          <Pop><Tag>A short routine</Tag></Pop>
          <Pop at={tBreath - tHelp}><Big size={120} color={GOLD}>1 · Breathe</Big></Pop>
          <Pop at={tCue - tHelp}><Big size={120}>2 · One cue</Big></Pop>
          <Pop at={tShoot - tHelp}><Big size={120} color={GOLD}>3 · Shoot</Big></Pop>
        </Stage>
      )),
      sc(tNo, tQ, <Lines tag="No guarantee" lines={[{t: 'Give attention', size: 110}, {t: 'a useful job', size: 130, color: GOLD}]} />),
      sc(tQ, END(w), <Lines lines={[{t: 'Your pre-shot', size: 120}, {t: 'routine?', size: 170, color: GOLD}]} foot="Comment below" />),
    ],
  };
};

// =============================================================== TACTICS
const O = (id: string, kf: [number, number, number][]): Track => ({id, side: 'O', kf});
const X = (id: string, kf: [number, number, number][]): Track => ({id, side: 'X', kf});

export const plan2 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tFirst = T('Now the first screen');
  const tRoll = T('This is a normal');
  const tFour = T('But watch four');
  const tBlock = T("Now the roller's man");
  const tTwo = T('Two defenders');
  const tPass = T('One passes');
  const tAns = T('The defence has answers');
  const tHelp = T('or send');
  const tKey = T('The key is simple');
  const end = END(w);
  const a = tFirst, b = tFour;
  const tracks: Track[] = [
    O('O1', [[0, 25, 31], [a + 0.2, 25, 31], [a + 1.6, 33, 28.5], [tPass - 0.3, 34, 24]]),
    O('O5', [[0, 31, 26], [a, 31, 26], [a + 0.8, 27.5, 28.4], [tRoll, 27.5, 28.4], [tRoll + 1.6, 27, 18], [tBlock + 0.8, 26, 10.5], [tPass + 1.0, 26, 10.5], [tPass + 1.8, 25.2, 6.2], [tAns, 25.2, 6.2], [tAns + 0.7, 26, 10]]),
    O('O4', [[0, 15, 17.5], [b, 15, 17.5], [b + 1.2, 28.2, 19.2]]),
    O('O2', [[0, 45, 24]]),
    O('O3', [[0, 5, 24]]),
    X('X1', [[0, 25, 27.6], [a + 0.8, 25, 27.6], [a + 1.1, 26, 30.8], [a + 1.8, 31.8, 27.8], [tBlock, 32.5, 27]]),
    X('X5', [[0, 31, 22.6], [a + 1.0, 31, 22.6], [a + 1.7, 29.5, 25.8], [tRoll + 1.4, 29.5, 25.8], [b + 1.4, 28.4, 22.8], [b + 2.0, 29.2, 22.4], [tAns, 29.2, 22.4], [tAns + 1.2, 28.5, 19.5]]),
    X('X4', [[0, 18, 19.5], [b, 18, 19.5], [b + 1.4, 25.5, 19], [tAns, 25.5, 19], [tAns + 1.2, 26.8, 13.2]]),
    X('X2', [[0, 42, 22]]),
    X('X3', [[0, 8, 22], [tHelp, 8, 22], [tHelp + 1.3, 19, 13.5]]),
  ];
  const ball: [number, number, number][] = [
    [0, 25, 31], [a + 0.2, 25, 31], [a + 1.6, 33, 28.5], [tPass - 0.3, 34, 24], [tPass + 0.7, 26, 10.5],
    [tPass + 1.0, 26, 10.5], [tPass + 1.8, 25.2, 6.2], [tAns, 25.2, 6.2], [tAns + 0.7, 26, 10],
  ];
  const arrows: Arrow[] = [
    {t: a + 0.3, until: tRoll + 0.2, pts: [[31, 26], [27.8, 28.2]], kind: 'screen'},
    {t: a + 1.0, until: tFour, pts: [[25, 31], [31, 30], [33.5, 26]], kind: 'move'},
    {t: tRoll + 0.6, until: tBlock + 1.2, pts: [[27.5, 28.4], [27, 18], [26, 11]], kind: 'move'},
    {t: tFour + 0.1, until: tPass, pts: [[15, 17.5], [27.5, 19.2]], kind: 'screen'},
    {t: tPass, until: tPass + 1.0, pts: [[34, 24], [27, 11.5]], kind: 'pass'},
    {t: tPass + 1.1, until: tAns, pts: [[26, 10.5], [25.2, 7]], kind: 'shot'},
  ];
  const rings = [
    {t: 0.5, until: tFirst, at: 'O1', text: 'BALL'},
    {t: tFirst + 0.2, until: tRoll, at: 'O5', text: 'SCREEN #1'},
    {t: tFour + 0.6, until: tTwo, at: 'O4', text: 'SCREEN #2 · BACK SCREEN'},
    {t: tBlock, until: tPass, at: 'X5', text: 'X5 BLOCKED', color: '#FFFFFF', dy: -5.6},
    {t: tTwo, until: tPass, at: 'X1', text: 'X1 TRAPPED', color: '#FFFFFF', dy: 5.2},
    {t: tAns + 0.4, until: tHelp, at: 'X4', text: 'SWITCH', color: '#FFFFFF'},
    {t: tHelp + 0.4, until: tKey, at: 'X3', text: 'EARLY HELP', color: '#FFFFFF'},
  ];
  return {
    sub: 'TACTICS BOARD',
    scenes: [],
    court: {
      title: 'SPAIN PICK & ROLL',
      tracks, ball, arrows, rings, zones: [],
      steps: [
        [0, 'Why is it so hard to defend?'],
        [T('Start with the setup'), 'Setup: O1 ball · O5 screener'],
        [tFirst, 'Screen 1: O5 screens X1'],
        [tRoll, 'O5 rolls to the rim'],
        [tFour, 'Screen 2: O4 back-screens X5'],
        [tBlock, 'Roller is open'],
        [tPass, 'Pass and finish'],
        [tAns, 'Counter 1: switch the back screen'],
        [tHelp, 'Counter 2: early weak-side help'],
        [tKey, 'Screen the screener’s defender'],
      ],
    } as CourtSpec,
  };
};

export const plan4 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tSet = T('Here is the setup');
  const tRun = T('The offence runs');
  const tOne = T('Player one comes');
  const tDef = T('Now the defence');
  const tX1 = T('X one fights');
  const tX5 = T('But X five');
  const tGoal = T('The goal is simple');
  const tGuard = T('The guard cannot');
  const tPrice = T('But the price');
  const tPull = T('Now the ball handler');
  const tPop = T('and if five');
  const tWorks = T('Drop coverage works');
  const tAg = T('Against a great');
  const tracks: Track[] = [
    O('O1', [[0, 25, 31], [tRun + 0.5, 25, 31], [tOne + 0.6, 32, 28.5], [tOne + 2.2, 33.5, 24.5]]),
    O('O5', [[0, 29, 26], [tRun, 29, 26], [tRun + 0.9, 27.5, 28.4], [tX5 - 0.2, 27.5, 28.4], [tX5 + 1.6, 28.5, 23.5], [tGuard, 28.8, 22.5], [tPop, 28.8, 22.5], [tPop + 1.4, 38, 29.5]]),
    O('O4', [[0, 14, 18]]),
    O('O2', [[0, 45, 24]]),
    O('O3', [[0, 5, 24]]),
    X('X1', [[0, 25, 27.6], [tRun + 0.9, 25, 27.6], [tX1 - 0.1, 25, 27.6], [tX1 + 0.5, 26.5, 31.8], [tX1 + 1.5, 32, 31.2], [tX1 + 2.4, 34.5, 27.2]]),
    X('X5', [[0, 29, 23.0], [tX5 - 0.3, 29, 23.0], [tX5 + 0.9, 27.4, 19.5], [tPop + 1.6, 27.4, 19.5], [tPop + 2.3, 27.4, 19.5]]),
    X('X4', [[0, 17, 19]]),
    X('X2', [[0, 42, 22]]),
    X('X3', [[0, 8, 22]]),
  ];
  const ball: [number, number, number][] = [
    [0, 25, 31], [tRun + 0.5, 25, 31], [tOne + 0.6, 32, 28.5], [tOne + 2.2, 33.5, 24.5],
    [tPop + 0.2, 33.5, 24.5], [tPop + 1.6, 38, 29.5],
  ];
  const arrows: Arrow[] = [
    {t: tRun + 0.3, until: tOne + 1.0, pts: [[29, 26], [27.8, 28.2]], kind: 'screen'},
    {t: tOne + 0.4, until: tDef, pts: [[25, 31], [31, 30], [33.5, 25.5]], kind: 'move'},
    {t: tX1 + 0.2, until: tGoal, pts: [[25, 27.6], [26, 32], [32, 31.4], [34.5, 28]], kind: 'chase'},
    {t: tX5 + 0.2, until: tGoal, pts: [[29, 23], [27.4, 19.8]], kind: 'chase'},
    {t: tPull, until: tPull + 2.2, pts: [[33.5, 24.5], [26.2, 7]], kind: 'shot'},
    {t: tPop + 0.8, until: tWorks, pts: [[28.8, 22.5], [37, 29]], kind: 'move'},
    {t: tPop + 1.6, until: tWorks, pts: [[33.5, 24.5], [37.5, 29]], kind: 'pass'},
  ];
  return {
    sub: 'TACTICS BOARD',
    scenes: [],
    court: {
      title: 'DROP COVERAGE',
      tracks, ball, arrows,
      rings: [
        {t: 0.5, until: tSet, at: 'X5', text: 'THE BIG'},
        {t: tRun + 0.4, until: tOne + 0.8, at: 'O5', text: 'BALL SCREEN'},
        {t: tX1 + 0.5, until: tX5 - 0.2, at: 'X1', text: 'OVER THE TOP', color: '#FFFFFF'},
        {t: tX5 + 1.2, until: tGoal + 1.5, at: 'X5', text: 'X5 DROPS', color: '#FFFFFF'},
        {t: tPull + 0.2, until: tPull + 2.4, at: 'O1', text: 'OPEN PULL-UP'},
        {t: tPop + 1.8, until: tWorks + 0.5, at: 'X5', text: 'OUT OF POSITION', color: '#FFFFFF'},
      ],
      zones: [{t: tGoal + 0.3, until: tPrice, cx: 25, cy: 9, rx: 9, ry: 7, text: 'RIM PROTECTED'}],
      steps: [
        [0, 'Defend the pick and roll without leaving the paint'],
        [tSet, 'Setup: ball screen from O5'],
        [tOne, 'O1 uses the screen'],
        [tDef, 'X1 fights over the top'],
        [tX5, 'X5 drops back toward the free-throw line'],
        [tGoal, 'Protects the rim · takes away the roll'],
        [tPrice, 'The price: space for the mid-range'],
        [tPop, 'If the big pops: he is out of position'],
        [tWorks, 'Best against weaker shooters'],
        [tAg, 'Drop or switch vs a great shooter?'],
      ],
    } as CourtSpec,
  };
};

export const PLANS: Record<number, (w: Word[]) => Plan> = {1: plan1, 2: plan2, 3: plan3, 4: plan4, 5: plan5};
export const DUR = (w: Word[]) => Math.ceil(END(w) * 30);
