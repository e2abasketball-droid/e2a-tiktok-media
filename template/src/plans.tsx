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



// ================================================================ 2026-11-03 BATCH (plans 6-10)
export const plan6 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tJune = T('June eleventh'), tSeries = T('The series is'), tRep = T('Reports say'), tPlays = T('He plays forty-four'), tTwentyFive = T('With twenty-five seconds');
  const tThree = T('he hits the three-pointer'), tWin = T('The Bulls win'), tEnd = T('At the end'), tChi = T('Chicago takes'), tQ = T("Was this Jordan's");
  return {
    sub: 'BASKETBALL STORIES',
    scenes: [
      sc(0, tJune, (
        <Stage>
          <Pop><Tag>NBA Finals · 1997</Tag></Pop>
          <Pop at={0.2}><Count to={38} start={1.0} dur={1.2} size={330} /></Pop>
          <Pop at={0.4}><Tag size={56}>Points</Tag></Pop>
        </Stage>
      )),
      sc(tJune, tSeries, <Lines tag="June 11, 1997" lines={[{t: 'Game 5'}, {t: 'NBA Finals', size: 110, color: GOLD}]} foot="Salt Lake City" />),
      sc(tSeries, tRep, (
        <Stage>
          <Board label="Finals series" rows={[{name: 'BULLS', kf: [[0, 2]], color: GOLD}, {name: 'JAZZ', kf: [[0, 2]], color: WHITE}]} />
        </Stage>
      )),
      sc(tRep, tPlays, <Lines tag="Before tip-off" lines={[{t: 'Ill & weak', size: 140}, {t: 'Dehydrated', size: 120, color: GOLD}]} foot="Trainer later: likely food poisoning" />),
      sc(tPlays, tTwentyFive, (
        <Stage>
          <Pop><Big size={170} color={GOLD}>44 MIN</Big></Pop>
          <Pop at={0.5}><Big size={170}>38 PTS</Big></Pop>
          <Pop at={1.3}><Big size={96} color={GOLD}>7 REB · 5 AST</Big></Pop>
        </Stage>
      )),
      sc(tTwentyFive, tWin, <Lines tag="25 seconds left" lines={[{t: 'Jordan', size: 150}, {t: 'Three-pointer', size: 120, color: GOLD}]} foot="Bulls take the lead" />),
      sc(tWin, tEnd, (
        <Stage>
          <Board label="Game 5 · Final" rows={[{name: 'BULLS', kf: [[0, 90]], color: GOLD}, {name: 'JAZZ', kf: [[0, 88]], color: WHITE}]} />
        </Stage>
      )),
      sc(tEnd, tChi, <Lines tag="After the buzzer" lines={[{t: 'Helped off', size: 130}, {t: 'by Pippen', size: 150, color: GOLD}]} />),
      sc(tChi, tQ, <Lines tag="Series" lines={[{t: 'Bulls 3 – 2', size: 150, color: GOLD}]} foot="Title clinched in Game 6" />),
      sc(tQ, END(w), <Lines lines={[{t: 'His greatest', size: 130}, {t: 'performance?', size: 140, color: GOLD}]} foot="Comment your answer" />),
    ],
    overlays: <Popup at={tThree + 0.4} text="+3" />,
  };
};

export const plan8 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tBarc = T('Barcelona'), tLith = T('Lithuania has just'), tDead = T('Then the Grateful'), tArt = T('An artist designs'), tWear = T('The team wears'), tBronze = T('The bronze medal game'), tWins = T('Lithuania wins');
  const tSab = T('Arvydas Sabonis'), tSmall = T('A small nation'), tQ = T('Is this the coolest');
  return {
    sub: 'BASKETBALL STORIES',
    scenes: [
      sc(0, tBarc, <Lines tag="Olympic medal" lines={[{t: 'Wearing', size: 120}, {t: 'tie-dye', size: 230, color: GOLD}]} />),
      sc(tBarc, tLith, <Lines tag="Barcelona" lines={[{t: '1992', size: 280, color: GOLD}, {t: 'Olympic Games', size: 90}]} />),
      sc(tLith, tDead, <Lines tag="Lithuania" lines={[{t: 'Newly', size: 120}, {t: 'independent', size: 120, color: GOLD}]} foot="Very little funding" />),
      sc(tDead, tArt, <Lines tag="Help arrives" lines={[{t: 'Grateful', size: 150, color: GOLD}, {t: 'Dead', size: 200}]} />),
      sc(tArt, tWear, <Lines tag="The shirt" lines={[{t: 'Skeleton', size: 130}, {t: 'slam dunk', size: 150, color: GOLD}]} foot="Lithuania’s colours" />),
      sc(tWear, tBronze, <Lines tag="On the podium" lines={[{t: 'Tie-dye', size: 170, color: GOLD}, {t: 'Bronze', size: 170}]} />),
      sc(tBronze, tSab, (
        <Stage>
          <Board label="Bronze medal game" rows={[{name: 'LITHUANIA', kf: [[0, 0], [tWins + 0.5, 82]], color: GOLD}, {name: 'UNIFIED', kf: [[0, 0], [tWins + 0.5, 78]], color: WHITE}]} />
        </Stage>
      )),
      sc(tSab, tSmall, <Lines tag="In the squad" lines={[{t: 'Arvydas', size: 150}, {t: 'Sabonis', size: 170, color: GOLD}]} />),
      sc(tSmall, tQ, <Lines lines={[{t: 'Small nation', size: 120}, {t: 'Tight budget', size: 120, color: GOLD}, {t: 'Unforgettable', size: 110}]} />),
      sc(tQ, END(w), <Lines lines={[{t: 'Coolest Olympic', size: 120}, {t: 'story?', size: 190, color: GOLD}]} foot="Comment below" />),
    ],
  };
};

export const plan10 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tPsy = T('Psychologists call it'), tVoice = T('It is the inner'), tMeta = T('A 2011 meta-analysis'), tTrain = T('Training mattered too'), tPrac = T('Here is a practical'), tAfter = T('After a miss');
  const tNot = T('Not I always choke'), tChoose = T('Choose a cue'), tEyes = T('Eyes on the rim'), tBal = T('Balance'), tFollow = T('Follow through'), tVary = T('Results do vary'), tMagic = T('It is not magic'), tQ = T('What is your cue');
  return {
    sub: 'MIND GAME',
    scenes: [
      sc(0, tPsy, (
        <Stage>
          <Pop><Tag>After a miss</Tag></Pop>
          <Pop at={0.2}><Big size={230} color={RED}>MISS</Big></Pop>
          <Pop at={0.9}><Big size={96}>What do you say next?</Big></Pop>
        </Stage>
      )),
      sc(tPsy, tVoice, <Lines tag="Psychology" lines={[{t: 'Self-talk', size: 210, color: GOLD}]} />),
      sc(tVoice, tMeta, <Lines tag="Your inner voice" lines={[{t: 'Before', size: 120}, {t: 'During', size: 120, color: GOLD}, {t: 'After', size: 120}]} />),
      sc(tMeta, tTrain, (
        <Stage>
          <Pop><Tag>2011 meta-analysis</Tag></Pop>
          <Pop at={0.2}><Count to={32} start={tMeta + 0.3} dur={1.0} size={300} /></Pop>
          <Pop at={0.4}><Big size={90}>studies pooled</Big></Pop>
          <Pop at={1.6}><Big size={84} color={GOLD}>Moderate positive effect</Big></Pop>
        </Stage>
      )),
      sc(tTrain, tPrac, <Lines tag="Training mattered" lines={[{t: 'Taught to', size: 120}, {t: 'use it = better', size: 120, color: GOLD}]} />),
      sc(tPrac, tAfter, <Lines tag="A practical idea" lines={[{t: 'Next-action', size: 130}, {t: 'cues', size: 180, color: GOLD}]} />),
      sc(tAfter, tChoose, (
        <Stage>
          <Pop><Tag>After a miss</Tag></Pop>
          <Pop at={0.1}><Big size={130} color={GOLD}>Drop the verdict</Big></Pop>
          <Pop at={tNot - tAfter}><Big size={92} color={RED}>“I always choke”</Big></Pop>
        </Stage>
      )),
      sc(tChoose, tVary, (
        <Stage>
          <Pop><Tag>Choose a cue</Tag></Pop>
          <Pop at={tEyes - tChoose}><Big size={104} color={GOLD}>Eyes on the rim</Big></Pop>
          <Pop at={tBal - tChoose}><Big size={104}>Balance</Big></Pop>
          <Pop at={tFollow - tChoose}><Big size={104} color={GOLD}>Follow through</Big></Pop>
        </Stage>
      )),
      sc(tVary, tMagic, <Lines tag="Results vary" lines={[{t: 'Test what', size: 120}, {t: 'works for you', size: 120, color: GOLD}]} />),
      sc(tMagic, tQ, <Lines tag="Not magic" lines={[{t: 'A skill you', size: 120}, {t: 'can practise', size: 130, color: GOLD}]} />),
      sc(tQ, END(w), <Lines lines={[{t: 'Your cue?', size: 190, color: GOLD}]} foot="Comment below" />),
    ],
  };
};

export const plan7 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tSet = T('Here is the setup'), tBall = T('One has the ball'), tFive = T('Five waits'), tTwo = T('Two spreads'), tP1 = T('One passes to two');
  const tCut = T('Now the cut'), tRun = T('One runs right'), tBlock = T('Five blocks'), tStuck = T('The defender is stuck'), tRead = T('Two reads it');
  const tAns = T('The defence has an answer'), tSw = T('X five can step'), tLeft = T('Then X one is'), tSeal = T('And five turns'), tKey = T('The key is simple');
  const tracks: Track[] = [
    O('O1', [[0, 25, 33], [tRun, 25, 33], [tRun + 1.5, 29, 26], [tBlock, 28.2, 20.5], [tRead + 0.4, 26, 11], [tRead + 1.2, 25.5, 6.5], [tRead + 1.6, 25.5, 6.5], [tAns + 0.2, 25.5, 6.5], [tAns + 1.0, 26.5, 10]]),
    O('O2', [[0, 41, 24]]),
    O('O3', [[0, 9, 26]]),
    O('O4', [[0, 8, 12]]),
    O('O5', [[0, 31, 19], [tSeal - 0.2, 31, 19], [tSeal + 1.0, 29.5, 12.5]]),
    X('X1', [[0, 25, 30.5], [tRun, 25, 30.5], [tRun + 1.0, 25.5, 30], [tRun + 2.5, 28.6, 25], [tBlock + 0.8, 31.4, 21.8], [tLeft, 31.4, 21.8], [tSeal + 0.2, 32.6, 17.4], [tSeal + 1.0, 31.5, 14.2]]),
    X('X2', [[0, 42, 22]]),
    X('X3', [[0, 9, 23]]),
    X('X4', [[0, 9, 14]]),
    X('X5', [[0, 31, 15.5], [tSw, 31, 15.5], [tSw + 1.1, 27.5, 12.5]]),
  ];
  const ball: [number, number, number][] = [
    [0, 25, 33], [tP1, 25, 33], [tP1 + 0.6, 41, 24], [tRead, 41, 24], [tRead + 1.2, 25.5, 8], [tAns, 25.5, 6.5], [tAns + 0.5, 41, 24], [tSeal + 0.7, 41, 24], [tSeal + 1.3, 29.5, 12.5],
  ];
  const arrows: Arrow[] = [
    {t: tP1, until: tP1 + 1.4, pts: [[25, 33], [40, 24.5]], kind: 'pass'},
    {t: tRun, until: tRead + 0.4, pts: [[25, 33], [29, 26], [28.2, 20.5], [25.5, 8]], kind: 'move'},
    {t: tBlock, until: tRead, pts: [[32.5, 20.5], [30, 23]], kind: 'screen'},
    {t: tRead, until: tRead + 1.4, pts: [[41, 24], [26.5, 9]], kind: 'pass'},
    {t: tSeal + 0.9, until: tSeal + 2.2, pts: [[41, 24], [30.5, 13]], kind: 'pass'},
  ];
  const rings = [
    {t: 0.4, until: tFive, at: 'O1', text: 'BALL'},
    {t: tFive, until: tTwo, at: 'O5', text: 'HIGH POST'},
    {t: tBlock, until: tRead, at: 'X1', text: 'STUCK', color: '#FFFFFF', dy: 5.4},
    {t: tRead + 0.8, until: tAns, at: 'O1', text: 'LAYUP'},
    {t: tSw + 0.6, until: tSeal, at: 'X5', text: 'SWITCH', color: '#FFFFFF'},
    {t: tSeal + 0.8, until: tKey, at: 'O5', text: 'SEALS X1'},
  ];
  return {
    sub: 'TACTICS BOARD',
    scenes: [],
    court: {
      title: 'UCLA CUT',
      tracks, ball, arrows, rings, zones: [],
      steps: [
        [0, 'Why is this cut so hard to guard?'],
        [tSet, 'Setup: O1 ball · O5 high post · O2 wing'],
        [tP1, 'O1 passes to O2'],
        [tCut, 'Now the cut'],
        [tRun, 'O1 cuts off O5’s shoulder'],
        [tBlock, 'O5 blocks X1’s path'],
        [tRead, 'O2 passes to the cutter: layup'],
        [tAns, 'Counter: X5 switches the cut'],
        [tSeal, 'O5 seals the smaller X1 · entry pass'],
        [tKey, 'Pass, then cut off the post'],
      ],
    } as CourtSpec,
  };
};

export const plan9 = (w: Word[]): Plan => {
  const T = makeT(w);
  const tSet = T('Here is the setup'), tScr = T('Five comes to set'), tDef = T('Now the defence'), tArr = T('When the screen arrives'), tTk1 = T('X one takes five'), tTk5 = T('X five takes one');
  const tChase = T('No chasing'), tBen = T('The benefit is clear'), tPrice = T('But look at the price'), tNow = T('Five now has'), tRoll = T('He rolls'), tPass = T('One throws the pass'), tMis = T('That mismatch');
  const tAns = T('The defence answers'), tKey = T('Switching works best');
  const tracks: Track[] = [
    O('O1', [[0, 25, 31], [tArr, 25, 31], [tArr + 1.2, 33, 28.5]]),
    O('O5', [[0, 31, 26], [tScr, 31, 26], [tScr + 0.9, 27.5, 28.4], [tRoll, 27.5, 28.4], [tRoll + 1.4, 27, 17], [tRoll + 2.2, 26.5, 10.5]]),
    O('O2', [[0, 45, 24]]),
    O('O3', [[0, 5, 24]]),
    O('O4', [[0, 15, 17.5]]),
    X('X1', [[0, 25, 27.6], [tArr, 25, 27.6], [tArr + 0.9, 26.4, 27.2], [tRoll, 26.4, 27.2], [tRoll + 1.4, 28.5, 19], [tRoll + 2.2, 28.4, 13.2]]),
    X('X5', [[0, 31, 22.6], [tArr, 31, 22.6], [tArr + 1.0, 32.6, 25.4]]),
    X('X2', [[0, 42, 22]]),
    X('X3', [[0, 8, 22]]),
    X('X4', [[0, 18, 19.5], [tAns, 18, 19.5], [tAns + 1.2, 24, 14.5]]),
  ];
  const ball: [number, number, number][] = [
    [0, 25, 31], [tArr, 25, 31], [tArr + 1.2, 33, 28.5], [tPass, 33, 28.5], [tPass + 1.0, 26.5, 10.5],
  ];
  const arrows: Arrow[] = [
    {t: tScr + 0.4, until: tArr, pts: [[31, 26], [27.8, 28.2]], kind: 'screen'},
    {t: tArr + 0.1, until: tChase + 1, pts: [[25, 27.6], [27, 28]], kind: 'chase'},
    {t: tArr + 0.1, until: tChase + 1, pts: [[31, 22.6], [32.6, 25.4]], kind: 'chase'},
    {t: tRoll + 0.2, until: tPass, pts: [[27.5, 28.4], [27, 17], [26.5, 11]], kind: 'move'},
    {t: tPass, until: tPass + 1.1, pts: [[33, 28.5], [27, 11.5]], kind: 'pass'},
  ];
  const rings = [
    {t: 0.4, until: tSet, at: 'O1', text: 'BALL'},
    {t: tScr + 0.3, until: tDef, at: 'O5', text: 'BALL SCREEN'},
    {t: tTk1, until: tTk5, at: 'X1', text: 'X1 TAKES O5', color: '#FFFFFF'},
    {t: tTk5, until: tBen, at: 'X5', text: 'X5 TAKES O1', color: '#FFFFFF', dy: 5.4},
    {t: tNow, until: tPass + 1.2, at: 'X1', text: 'MISMATCH', color: '#FFFFFF', dy: -5.6},
    {t: tAns + 0.5, until: tKey, at: 'X4', text: 'EARLY HELP', color: '#FFFFFF'},
  ];
  return {
    sub: 'TACTICS BOARD',
    scenes: [],
    court: {
      title: 'SWITCH EVERYTHING',
      tracks, ball, arrows, rings, zones: [],
      steps: [
        [0, 'Defend every screen by swapping'],
        [tSet, 'Setup: O1 ball · O5 ball screen'],
        [tArr, 'Screen arrives: X1 and X5 swap'],
        [tChase, 'No chasing · no fighting over'],
        [tBen, 'Nobody gets lost'],
        [tPrice, 'The price: a mismatch'],
        [tRoll, 'O5 rolls and seals the smaller X1'],
        [tPass, 'Pass over the top'],
        [tAns, 'Counter: send early weak-side help'],
        [tKey, 'Works best when all five can guard anyone'],
      ],
    } as CourtSpec,
  };
};

export const PLANS: Record<number, (w: Word[]) => Plan> = {1: plan1, 2: plan2, 3: plan3, 4: plan4, 5: plan5, 6: plan6, 7: plan7, 8: plan8, 9: plan9, 10: plan10};
export const DUR = (w: Word[]) => Math.ceil(END(w) * 30);
