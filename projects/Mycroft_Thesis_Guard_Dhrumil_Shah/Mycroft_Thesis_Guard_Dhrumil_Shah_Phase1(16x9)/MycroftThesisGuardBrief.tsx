import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

/**
 * MycroftThesisGuardBrief
 *
 * A self-contained, 4K, three-minute research explainer. Every project fact
 * on screen is either paired with a visible source label or with a captured
 * notebook/report artifact under public-mycroft-brief/mycroft-brief/assets.
 * CLEAR is intentionally labelled as the presenter's review framework, not as
 * a software feature claimed by the supplied Mycroft notebook.
 */

export const MYCROFT_BRIEF_FPS = 24;
export const MYCROFT_BRIEF_TOTAL_FRAMES = 4320; // exactly 03:00 at 24 fps

const C = {
  page: '#FAF9F5',
  card: '#FFFFFF',
  ink: '#3D3929',
  soft: '#73705F',
  ghost: '#AAA593',
  border: '#E5E2D9',
  wash: '#F2F0E9',
  accent: '#D97757',
  accentDeep: '#C6613F',
  accentWash: '#FBE8DE',
  darkWash: '#EEECE5',
} as const;

const SERIF = 'Georgia, "Times New Roman", serif';
const SANS = 'Arial, "Segoe UI", sans-serif';
const MONO = 'Consolas, "Courier New", monospace';
const SAFE = {left: 230, right: 230, top: 150, bottom: 150};

type AudioBeat = {id: string; seconds: number};

// These are measured from the supplied MP3 files. B10b is intentionally not
// in this tight 3:00 cut; its authentic visualization-scope receipt appears
// visually in Scene 9 instead of stretching the delivery to 3:12.
const AUDIO_BEATS: AudioBeat[] = [
  {id: 'B00', seconds: 14.04},
  {id: 'B01', seconds: 11.784},
  {id: 'B02', seconds: 8.952},
  {id: 'B03', seconds: 9.504},
  {id: 'B04', seconds: 11.328},
  {id: 'B05', seconds: 9.648},
  {id: 'B06', seconds: 6.6},
  {id: 'B07', seconds: 14.856},
  {id: 'B08', seconds: 8.88},
  {id: 'B08b', seconds: 16.8},
  {id: 'B09', seconds: 10.56},
  {id: 'B10', seconds: 10.608},
  {id: 'B11', seconds: 9.312},
  {id: 'B12', seconds: 10.464},
  {id: 'B12b', seconds: 11.736},
  {id: 'B13', seconds: 11.496},
];

const toFrames = (seconds: number) => Math.round(seconds * MYCROFT_BRIEF_FPS);

let audioCursor = 0;
const AUDIO_TIMELINE = AUDIO_BEATS.map((beat) => {
  const item = {id: beat.id, from: audioCursor, duration: toFrames(beat.seconds)};
  audioCursor += item.duration;
  return item;
});

const timing = (id: string) => {
  const entry = AUDIO_TIMELINE.find((item) => item.id === id);
  if (!entry) throw new Error(`Missing measured audio timing for ${id}`);
  return entry;
};

const range = (first: string, last: string) => {
  const start = timing(first).from;
  const end = timing(last).from + timing(last).duration;
  return {from: start, duration: end - start};
};

const SCENES = {
  opening: range('B00', 'B00'),
  problem: range('B01', 'B02'),
  data: range('B03', 'B04'),
  method: range('B05', 'B06'),
  results: range('B07', 'B08'),
  limit: range('B08b', 'B08b'),
  agents: range('B09', 'B10'),
  boundary: range('B11', 'B11'),
  loop: range('B12', 'B12'),
  close: {from: timing('B12b').from, duration: MYCROFT_BRIEF_TOTAL_FRAMES - timing('B12b').from},
} as const;

const clamp = (value: number, min = 0, max = 1) => Math.max(min, Math.min(max, value));

const useReveal = (delay: number, stiffness = 120) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return clamp(
    spring({
      frame: Math.max(0, frame - delay),
      fps,
      config: {damping: 22, stiffness, mass: 0.8},
    }),
  );
};

const sceneAsset = (path: string) => staticFile(`mycroft-brief/assets/evidence/${path}`);
const sceneAudio = (id: string) => staticFile(`mycroft-brief/audio/beat-${id}.mp3`);

const SourceTag: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div
    style={{
      position: 'absolute',
      left: SAFE.left,
      bottom: SAFE.bottom - 4,
      maxWidth: 2500,
      padding: '14px 19px',
      border: `2px solid ${C.border}`,
      borderRadius: 12,
      background: 'rgba(250,249,245,0.96)',
      color: C.soft,
      fontFamily: MONO,
      fontSize: 40,
      fontWeight: 700,
      letterSpacing: 0.1,
      zIndex: 30,
    }}
  >
    SOURCE · {children}
  </div>
);

const SceneShell: React.FC<{
  number: string;
  label: string;
  source: React.ReactNode;
  duration: number;
  children: React.ReactNode;
}> = ({number, label, source, duration, children}) => {
  const frame = useCurrentFrame();
  const fade = interpolate(frame, [0, 10, duration - 12, duration], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill style={{background: C.page, overflow: 'hidden', opacity: fade}}>
      <div style={{position: 'absolute', width: 740, height: 740, borderRadius: 740, left: -440, top: -430, background: C.accent, opacity: 0.035}} />
      <div style={{position: 'absolute', width: 800, height: 800, borderRadius: 800, right: -580, bottom: -570, background: C.ink, opacity: 0.025}} />
      <div style={{position: 'absolute', left: SAFE.left, top: 68, color: C.soft, fontFamily: MONO, fontSize: 31, fontWeight: 700, letterSpacing: 2.8}}>
        DHRUMIL SHAH · MYCROFT THESISGUARD
      </div>
      <div style={{position: 'absolute', right: SAFE.right, top: 68, color: C.soft, fontFamily: MONO, fontSize: 31, fontWeight: 700, letterSpacing: 2.8}}>
        {number} / 10
      </div>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: SAFE.top, color: C.soft, fontFamily: MONO, fontSize: 34, fontWeight: 700, letterSpacing: 3.2}}>
        {label.toUpperCase()}
      </div>
      {children}
      <SourceTag>{source}</SourceTag>
    </AbsoluteFill>
  );
};

const Headline: React.FC<{title: string; subtitle?: string; width?: number; top?: number}> = ({title, subtitle, width = 2600, top = 235}) => (
  <div style={{position: 'absolute', left: SAFE.left, top, width, zIndex: 4}}>
    <div style={{fontFamily: SERIF, fontWeight: 700, color: C.ink, fontSize: 132, letterSpacing: '-0.035em', lineHeight: 0.93, whiteSpace: 'pre-line'}}>{title}</div>
    {subtitle ? <div style={{marginTop: 28, fontFamily: SERIF, color: C.soft, fontStyle: 'italic', fontSize: 58, lineHeight: 1.02}}>{subtitle}</div> : null}
  </div>
);

const Card: React.FC<{children: React.ReactNode; style?: React.CSSProperties; accent?: boolean}> = ({children, style, accent = false}) => (
  <div
    style={{
      boxSizing: 'border-box',
      background: accent ? C.accentWash : C.card,
      border: `${accent ? 3 : 2}px solid ${accent ? C.accent : C.border}`,
      borderRadius: 28,
      boxShadow: '0 24px 55px rgba(61,57,41,0.075)',
      ...style,
    }}
  >
    {children}
  </div>
);

const Reveal: React.FC<{delay: number; children: React.ReactNode; y?: number; x?: number; scale?: number}> = ({delay, children, y = 24, x = 0, scale = 0.97}) => {
  const p = useReveal(delay);
  return <div style={{opacity: p, transform: `translate(${(1 - p) * x}px, ${(1 - p) * y}px) scale(${scale + (1 - scale) * p})`}}>{children}</div>;
};

const EvidenceImage: React.FC<{
  file: string;
  caption: string;
  style: React.CSSProperties;
  position?: string;
  zoom?: number;
}> = ({file, caption, style, position = 'center', zoom = 1.02}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <Card style={{position: 'absolute', overflow: 'hidden', ...style}}>
      <Img
        src={sceneAsset(file)}
        style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: position,
          transform: `scale(${zoom + p * 0.025})`,
        }}
      />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, padding: '15px 24px', background: 'rgba(250,249,245,0.95)', borderTop: `2px solid ${C.border}`, fontFamily: MONO, color: C.ink, fontSize: 24, fontWeight: 700}}>
        {caption}
      </div>
    </Card>
  );
};

const Arrow: React.FC<{delay: number}> = ({delay}) => (
  <Reveal delay={delay} y={0} scale={1}>
    <div style={{fontFamily: SERIF, color: C.soft, fontSize: 82, lineHeight: 1}}>→</div>
  </Reveal>
);

const Stat: React.FC<{value: string; label: string; note?: string; accent?: boolean; delay: number}> = ({value, label, note, accent = false, delay}) => (
  <Reveal delay={delay}>
    <Card accent={accent} style={{padding: '34px 38px', minHeight: 258}}>
      <div style={{fontFamily: MONO, color: accent ? C.accentDeep : C.soft, fontSize: 24, fontWeight: 800, letterSpacing: 2.2}}>{label.toUpperCase()}</div>
      <div style={{marginTop: 18, fontFamily: SERIF, color: C.ink, fontSize: 81, fontWeight: 700, letterSpacing: '-0.025em', lineHeight: 0.9}}>{value}</div>
      {note ? <div style={{marginTop: 17, fontFamily: SANS, color: C.soft, fontSize: 28, lineHeight: 1.15}}>{note}</div> : null}
    </Card>
  </Reveal>
);

const PipelineToken: React.FC<{delay: number; title: string; note?: string; accent?: boolean; wide?: boolean}> = ({delay, title, note, accent = false, wide = false}) => (
  <Reveal delay={delay} y={30}>
    <Card accent={accent} style={{width: wide ? 510 : 420, minHeight: 238, padding: '28px 30px', display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <div style={{fontFamily: SERIF, color: C.ink, fontSize: 56, fontWeight: 700, lineHeight: 0.92}}>{title}</div>
      {note ? <div style={{marginTop: 17, fontFamily: SANS, color: C.soft, fontSize: 26, lineHeight: 1.15}}>{note}</div> : null}
    </Card>
  </Reveal>
);

const OpeningScene: React.FC = () => {
  const title = useReveal(4);
  return (
    <SceneShell number="01" label="Executive summary" source="Implementation Report §1 · Notebook Cell 21" duration={SCENES.opening.duration}>
      <div style={{position: 'absolute', left: SAFE.left, top: 315, opacity: title, transform: `translateY(${(1 - title) * 18}px)`}}>
        <div style={{fontFamily: SERIF, color: C.ink, fontSize: 142, fontWeight: 700, letterSpacing: '-0.04em', lineHeight: 0.9}}>Hi, I’m Dhrumil Shah.</div>
        <div style={{marginTop: 35, maxWidth: 2700, fontFamily: SERIF, color: C.soft, fontSize: 61, fontStyle: 'italic', lineHeight: 1.04}}>A three-minute evidence review of what Mycroft ThesisGuard does, what the run found, and where it stops.</div>
      </div>
      <Reveal delay={28} y={20}>
        <Card style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 690, padding: '42px 52px'}}>
          <div style={{fontFamily: MONO, color: C.soft, fontSize: 25, fontWeight: 800, letterSpacing: 2.5}}>THE REVIEW QUESTION</div>
          <div style={{marginTop: 22, fontFamily: SERIF, color: C.ink, fontSize: 83, fontWeight: 700, letterSpacing: '-0.02em'}}>Is the original thesis still supported by evidence?</div>
        </Card>
      </Reveal>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1120, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <PipelineToken delay={47} title="Claim" note="what was believed" />
        <Arrow delay={61} />
        <PipelineToken delay={67} title="Evidence" note="what can be sourced" />
        <Arrow delay={81} />
        <PipelineToken delay={87} title="Uncertainty" note="what changed or is missing" />
        <Arrow delay={101} />
        <PipelineToken delay={107} title="Human" note="who makes the decision" accent />
      </div>
      <Reveal delay={134} y={0}>
        <div style={{position: 'absolute', left: SAFE.left, top: 1515, fontFamily: MONO, color: C.accentDeep, fontSize: 31, fontWeight: 800, letterSpacing: 2.7}}>EVIDENCE-FIRST REVIEW · NOT PERSONALIZED FINANCIAL ADVICE</div>
      </Reveal>
    </SceneShell>
  );
};

const ProblemFrameworkScene: React.FC = () => {
  const frame = useCurrentFrame();
  const showFramework = clamp(interpolate(frame, [270, 315], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const clear = [
    ['C', 'Claim'],
    ['L', 'Link evidence'],
    ['E', 'Evaluate change'],
    ['A', 'Assess uncertainty'],
    ['R', 'Reserve decision'],
  ];
  return (
    <SceneShell number="02" label="The problem and the review frame" source="Implementation Report §1 · illustrative drift example · Presenter framework for this film" duration={SCENES.problem.duration}>
      <Headline title="Thesis drift." subtitle="The position stays. The reason quietly moves." width={1950} />
      <EvidenceImage file="report-problem-boundary.png" caption="Report §1 · problem statement and project objective" style={{left: 2220, top: 270, width: 1390, height: 745}} position="left top" zoom={1.08} />
      <div style={{position: 'absolute', left: SAFE.left, top: 800, display: 'flex', alignItems: 'center', gap: 26}}>
        <Reveal delay={50}><Card style={{width: 800, padding: '34px 37px'}}><div style={{fontFamily: MONO, color: C.soft, fontSize: 24, fontWeight: 800, letterSpacing: 2.2}}>ILLUSTRATIVE THESIS EXAMPLE</div><div style={{marginTop: 18, fontFamily: SERIF, fontSize: 58, color: C.ink, fontWeight: 700}}>Growth could continue.</div></Card></Reveal>
        <Arrow delay={85} />
        <Reveal delay={100}><Card accent style={{width: 800, padding: '34px 37px'}}><div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 24, fontWeight: 800, letterSpacing: 2.2}}>FACTS MOVE</div><div style={{marginTop: 18, fontFamily: SERIF, fontSize: 58, color: C.ink, fontWeight: 700}}>The story is rewritten.</div></Card></Reveal>
      </div>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1210, opacity: showFramework, transform: `translateY(${(1 - showFramework) * 22}px)`}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24}}>
          <div style={{fontFamily: SERIF, color: C.ink, fontWeight: 700, fontSize: 75}}>Not a buy-or-sell engine.</div>
          <div style={{fontFamily: MONO, color: C.accentDeep, fontWeight: 800, fontSize: 28, letterSpacing: 2}}>PRESENTER FRAMEWORK · CLEAR</div>
        </div>
        <div style={{display: 'flex', gap: 20}}>
          {clear.map(([letter, word], index) => <Reveal key={letter} delay={315 + index * 16}><Card accent={index === 4} style={{width: 650, minHeight: 245, padding: '25px 28px'}}><div style={{fontFamily: SERIF, fontSize: 84, color: index === 4 ? C.accentDeep : C.ink, fontWeight: 700, lineHeight: 0.8}}>{letter}</div><div style={{marginTop: 18, fontFamily: SANS, color: C.soft, fontSize: 27, fontWeight: 700}}>{word}</div></Card></Reveal>)}
        </div>
      </div>
    </SceneShell>
  );
};

const DataScene: React.FC = () => (
  <SceneShell number="03" label="Validated inputs and causal features" source="Notebook Cells 5, 11, 25 · Implementation Report §3–4" duration={SCENES.data.duration}>
    <Headline title="Check what enters the model." subtitle="Validated data first; features use only what was knowable then." width={2800} />
    <EvidenceImage file="notebook-features.png" caption="Notebook Cell 5 · feature definitions" style={{left: SAFE.left, top: 675, width: 1370, height: 945}} position="left top" zoom={1.1} />
    <div style={{position: 'absolute', left: 1670, right: SAFE.right, top: 675, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24}}>
      <Stat delay={30} label="Clean rows" value="184,138" note="recorded run output" />
      <Stat delay={48} label="Coverage" value="120" note="tickers and companies" />
      <Stat delay={66} label="Target" value="5 days" note="forward direction label" />
      <Stat delay={84} label="Rule" value="0 lookahead" note="future information is excluded" accent />
    </div>
    <Reveal delay={107}>
      <Card style={{position: 'absolute', left: 1670, right: SAFE.right, top: 1300, padding: '31px 38px'}}>
        <div style={{fontFamily: MONO, color: C.soft, fontSize: 24, fontWeight: 800, letterSpacing: 2.1}}>FEATURES SHOWN IN THE NOTEBOOK</div>
        <div style={{marginTop: 22, fontFamily: SERIF, color: C.ink, fontSize: 52, fontWeight: 700, lineHeight: 1.08}}>Returns · volatility · drawdowns · volume · sector-relative movement</div>
      </Card>
    </Reveal>
  </SceneShell>
);

const MethodScene: React.FC = () => {
  const models = ['Prior baseline', 'Logistic regression', 'Random forest', 'Extra Trees', 'Hist. gradient boost'];
  return (
    <SceneShell number="04" label="Chronological evaluation" source="Notebook Cells 13, 15, 25 · Implementation Report §3–4" duration={SCENES.method.duration}>
      <Headline title={'Split by time.\nBenchmark the baseline.'} subtitle="Random shuffling would leak the future." width={1800} />
      <EvidenceImage file="notebook-time-split.png" caption="Notebook Cell 13 · create_time_splits()" style={{left: 2100, top: 290, width: 1500, height: 735}} position="left top" zoom={1.16} />
      <Reveal delay={28}>
        <Card style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 870, padding: '34px 38px'}}>
          <div style={{display: 'flex', height: 195, gap: 16}}>
            {[['70%', '127,858', 'TRAIN'], ['15%', '26,880', 'VALIDATE'], ['15%', '27,600', 'HOLDOUT TEST']].map(([share, count, label], index) => <div key={label} style={{flex: index === 0 ? 7 : 2, borderRadius: 18, padding: '22px 25px', background: index === 2 ? C.accentWash : C.darkWash, border: `${index === 2 ? 3 : 2}px solid ${index === 2 ? C.accent : C.border}`}}><div style={{fontFamily: MONO, color: index === 2 ? C.accentDeep : C.soft, fontSize: 23, fontWeight: 800, letterSpacing: 1.8}}>{label}</div><div style={{marginTop: 11, fontFamily: SERIF, color: C.ink, fontSize: 58, lineHeight: 0.88, fontWeight: 700}}>{count}</div><div style={{fontFamily: SANS, color: C.soft, fontSize: 26}}>{share}</div></div>)}
          </div>
          <div style={{marginTop: 22, fontFamily: MONO, color: C.accentDeep, fontSize: 25, fontWeight: 800, letterSpacing: 1.7}}>FIVE-DAY TARGET LABELS ARE PURGED AT EACH PARTITION BOUNDARY</div>
        </Card>
      </Reveal>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1335, display: 'flex', gap: 22}}>
        {models.map((model, index) => <Reveal key={model} delay={115 + index * 13}><Card style={{width: 650, minHeight: 225, padding: '28px 29px'}}><div style={{fontFamily: MONO, color: C.soft, fontSize: 22, fontWeight: 800, letterSpacing: 1.8}}>{index === 0 ? 'BENCHMARK' : `MODEL ${index + 1}`}</div><div style={{marginTop: 18, fontFamily: SERIF, color: C.ink, fontSize: 47, lineHeight: 0.95, fontWeight: 700}}>{model}</div></Card></Reveal>)}
      </div>
    </SceneShell>
  );
};

const ResultsScene: React.FC = () => (
  <SceneShell number="05" label="The worked result" source="Notebook Cell 25 recorded run · Implementation Report §4 outcomes table" duration={SCENES.results.duration}>
    <Headline title={'The honest result\nwas weak.'} subtitle="That is a finding—not a success claim to decorate." width={1700} />
    <EvidenceImage file="report-and-run-outcomes.png" caption="Report §4 outcomes table · Notebook Cell 25 recorded output" style={{left: 2020, top: 275, width: 1580, height: 1240}} position="left top" zoom={1.44} />
    <div style={{position: 'absolute', left: SAFE.left, top: 730, width: 1450, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 25}}>
      <Stat delay={24} label="Selected model" value="Logistic" note="chosen on validation" />
      <Stat delay={45} label="ROC AUC" value="0.5158" note="holdout; 0.50 is random ranking" accent />
      <Stat delay={66} label="Brier score" value="0.2466" note="holdout calibration loss" />
      <Stat delay={87} label="Drift" value="Moderate" note="reported, not hidden" accent />
    </div>
    <Reveal delay={118}>
      <Card accent style={{position: 'absolute', left: SAFE.left, top: 1485, width: 1450, padding: '26px 34px'}}>
        <div style={{fontFamily: SERIF, color: C.ink, fontSize: 49, lineHeight: 1.0, fontWeight: 700}}>Short-horizon price direction was not reliably predictable from this supplied data.</div>
      </Card>
    </Reveal>
  </SceneShell>
);

const StopScene: React.FC = () => (
  <SceneShell number="06" label="Falsifiability: the system may stop" source="Notebook Cell 21 · ThesisCaptureAgent and BehavioralBiasReviewAgent" duration={SCENES.limit.duration}>
    <Headline title="Do not invent the missing evidence." subtitle="The edge case is part of the method." width={1800} />
    <EvidenceImage file="notebook-agent-classes.png" caption="Notebook Cell 21 · agent classes and returned status fields" style={{left: 2050, top: 610, width: 1540, height: 885}} position="left top" zoom={1.28} />
    <div style={{position: 'absolute', left: SAFE.left, top: 695, width: 1510, display: 'grid', gap: 24}}>
      <Stat delay={26} label="Original thesis" value="Not supplied" note="Thesis Capture returns needs_human_input" accent />
      <Stat delay={57} label="Behavioral bias" value="Not assessed" note="the prototype does not diagnose psychology without evidence" />
      <Stat delay={88} label="Decision state" value="Human review" note="missing source → insufficient evidence, not a verdict" accent />
    </div>
    <Reveal delay={140}>
      <div style={{position: 'absolute', left: SAFE.left, top: 1570, color: C.accentDeep, fontFamily: MONO, fontSize: 34, fontWeight: 900, letterSpacing: 2.8}}>NO SOURCE · NO VERDICT</div>
    </Reveal>
  </SceneShell>
);

const AgentsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const outcome = clamp(interpolate(frame, [230, 265], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const agents = ['Capture thesis', 'Retrieve evidence', 'Detect contradiction', 'Check bias', 'Human gate'];
  return (
    <SceneShell number="07" label="Agent workflow and human gate" source="Notebook Cell 21 · Notebook Cell 25 recorded run · Implementation Report §4" duration={SCENES.agents.duration}>
      <Headline title={'Five agents.\nOne human gate.'} subtitle="Automation organizes evidence; it does not decide." width={1750} />
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 760, display: 'flex', alignItems: 'center', gap: 18}}>
        {agents.map((agent, index) => <React.Fragment key={agent}><PipelineToken delay={30 + index * 20} title={agent} accent={index === 4} wide={index === 4} />{index < agents.length - 1 ? <Arrow delay={44 + index * 20} /> : null}</React.Fragment>)}
      </div>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1270, opacity: outcome, transform: `translateY(${(1 - outcome) * 22}px)`, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 26}}>
        <Stat delay={0} label="Reports" value="120" note="thesis-health reports" />
        <Stat delay={0} label="Trace events" value="600" note="agent trace events" />
        <Stat delay={0} label="Automated decisions" value="0" note="final actions remain human" accent />
      </div>
      <Reveal delay={310}>
        <div style={{position: 'absolute', left: SAFE.left, top: 1685, fontFamily: MONO, color: C.soft, fontSize: 27, letterSpacing: 1.7}}>MAINTAIN · REVISE · WATCHLIST · RETIRE — AVAILABLE ONLY AT THE HUMAN GATE</div>
      </Reveal>
    </SceneShell>
  );
};

const EvidenceBoundaryScene: React.FC = () => (
  <SceneShell number="08" label="Evidence boundary" source="Notebook Cell 21 · Implementation Report §§2, 5" duration={SCENES.boundary.duration}>
    <Headline title="No source, no verdict." subtitle="Market data is not a substitute for a thesis or decision history." width={2500} />
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 760, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 38}}>
      <Reveal delay={26}><Card style={{minHeight: 700, padding: '42px 48px'}}><div style={{fontFamily: MONO, color: C.soft, fontSize: 27, fontWeight: 900, letterSpacing: 2.7}}>AVAILABLE</div><div style={{marginTop: 32, fontFamily: SERIF, color: C.ink, fontSize: 66, fontWeight: 700}}>Market evidence</div>{['prices and volume', 'engineered features', 'model scores and drift'].map((line, index) => <div key={line} style={{marginTop: 34, fontFamily: SANS, color: C.ink, fontSize: 38}}>✓ {line}</div>)}</Card></Reveal>
      <Reveal delay={49}><Card accent style={{minHeight: 700, padding: '42px 48px'}}><div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 27, fontWeight: 900, letterSpacing: 2.7}}>NOT SUPPLIED</div><div style={{marginTop: 32, fontFamily: SERIF, color: C.ink, fontSize: 66, fontWeight: 700}}>Decision evidence</div>{['original investment thesis', 'filings / news / calls', 'prior decision history'].map((line) => <div key={line} style={{marginTop: 34, fontFamily: SANS, color: C.ink, fontSize: 38}}>— {line}</div>)}</Card></Reveal>
    </div>
    <Reveal delay={88}>
      <Card accent style={{position: 'absolute', left: 890, right: 890, top: 1580, padding: '28px 38px', textAlign: 'center'}}><div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 26, fontWeight: 900, letterSpacing: 2.4}}>RETURNED STATUS</div><div style={{marginTop: 16, fontFamily: SERIF, color: C.ink, fontSize: 53, fontWeight: 700}}>insufficient evidence → human_review_required</div></Card>
    </Reveal>
  </SceneShell>
);

const LoopScene: React.FC = () => {
  const stages = ['Validate', 'Engineer', 'Split by time', 'Evaluate', 'Monitor drift', 'Human review'];
  return (
  <SceneShell number="09" label="The auditable loop" source="Notebook Cells 13, 25, 50, 69 · Implementation Report §4" duration={SCENES.loop.duration}>
      <Headline title="Every stage leaves a record." subtitle="The end-to-end loop is a chain of artifacts a reviewer can inspect." width={2900} />
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 780, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        {stages.map((stage, index) => <React.Fragment key={stage}><PipelineToken delay={24 + index * 20} title={stage} accent={index === stages.length - 1} />{index < stages.length - 1 ? <Arrow delay={36 + index * 20} /> : null}</React.Fragment>)}
      </div>
      <EvidenceImage file="notebook-visualization-scope.png" caption="Notebook Cell 50 · recorded list of nine generated figure files" style={{left: SAFE.left, top: 1325, width: 1710, height: 440}} position="left top" zoom={1.13} />
      <Reveal delay={135}><Card accent style={{position: 'absolute', left: 2010, right: SAFE.right, top: 1325, minHeight: 440, padding: '34px 39px'}}><div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 25, fontWeight: 900, letterSpacing: 2}}>VISUALIZATION EVIDENCE</div><div style={{marginTop: 26, fontFamily: SERIF, color: C.ink, fontSize: 55, lineHeight: 0.98, fontWeight: 700}}>Nine figure filenames were recorded.</div><div style={{marginTop: 22, fontFamily: SANS, color: C.soft, fontSize: 29, lineHeight: 1.22}}>The actual plot files were not supplied, so this film shows the authentic creation record—not invented charts.</div></Card></Reveal>
    </SceneShell>
  );
};

const YourTurnCloseScene: React.FC = () => {
  const frame = useCurrentFrame();
  const turnEnd = timing('B12b').duration;
  const cardOpacity = clamp(interpolate(frame, [0, 24, turnEnd - 25, turnEnd + 12], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const outroOpacity = clamp(interpolate(frame, [turnEnd - 4, turnEnd + 28], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const rows = [
    ['1', 'Claim', 'What must be true?'],
    ['2', 'Linked sources', 'Where did each fact come from?'],
    ['3', 'Disconfirmer', 'What would change your mind?'],
    ['4', 'Date evidence', 'When was each source checked?'],
    ['5', 'Uncertainty', 'What is missing or drifting?'],
    ['6', 'Human review', 'Who owns the final decision?'],
  ];
  return (
    <SceneShell number="10" label="Your turn and close" source="Presenter CLEAR scaffold · Notebook Cell 21 · Cell 25 financial boundary" duration={SCENES.close.duration}>
      <div style={{opacity: cardOpacity}}>
        <Headline title="Run the review yourself." subtitle="A reusable scaffold—not a vague prompt." width={2500} />
        <Card style={{position: 'absolute', left: 710, right: 710, top: 690, padding: '34px 46px'}}>
          {rows.map(([n, name, prompt], index) => <Reveal key={n} delay={24 + index * 17} y={12}><div style={{display: 'flex', alignItems: 'center', gap: 25, marginTop: index === 0 ? 0 : 27, paddingBottom: 22, borderBottom: index === rows.length - 1 ? 'none' : `2px solid ${C.border}`}}><div style={{width: 48, height: 48, borderRadius: 48, background: index === rows.length - 1 ? C.accent : C.wash, color: index === rows.length - 1 ? C.card : C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: MONO, fontSize: 23, fontWeight: 900}}>{n}</div><div style={{width: 470, fontFamily: SERIF, color: C.ink, fontSize: 48, fontWeight: 700}}>{name}</div><div style={{flex: 1, fontFamily: SANS, color: C.soft, fontSize: 30}}>{prompt}</div></div></Reveal>)}
        </Card>
        <Reveal delay={118}><div style={{position: 'absolute', left: 710, right: 710, top: 1575, textAlign: 'center', fontFamily: MONO, color: C.accentDeep, fontSize: 30, fontWeight: 900, letterSpacing: 2.4}}>IF THE CLAIM OR SOURCE IS MISSING: RECORD INSUFFICIENT EVIDENCE.</div></Reveal>
      </div>
      <div style={{position: 'absolute', inset: 0, opacity: outroOpacity, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', textAlign: 'center'}}>
        <div style={{fontFamily: SERIF, color: C.ink, fontSize: 150, fontWeight: 700, letterSpacing: '-0.045em', lineHeight: 0.9}}>Mycroft ThesisGuard<span style={{color: C.accentDeep}}>.</span></div>
        <div style={{marginTop: 44, maxWidth: 2500, fontFamily: SERIF, color: C.soft, fontSize: 65, fontStyle: 'italic', lineHeight: 1.02}}>Evidence first. Uncertainty visible. Judgment human.</div>
        <div style={{marginTop: 95, padding: '21px 30px', border: `2px solid ${C.border}`, borderRadius: 15, background: C.card, fontFamily: SANS, color: C.soft, fontSize: 29}}>Educational research and model output; not personalized financial advice or an investment recommendation.</div>
        <div style={{marginTop: 34, fontFamily: MONO, color: C.accentDeep, fontSize: 27, fontWeight: 900, letterSpacing: 2.3}}>DHRUMIL SHAH · 2026</div>
      </div>
    </SceneShell>
  );
};

export const MycroftThesisGuardBrief: React.FC = () => (
  <AbsoluteFill style={{background: C.page}}>
    {AUDIO_TIMELINE.map((beat) => <Sequence key={beat.id} from={beat.from}><Audio src={sceneAudio(beat.id)} /></Sequence>)}
    <Sequence from={SCENES.opening.from} durationInFrames={SCENES.opening.duration}><OpeningScene /></Sequence>
    <Sequence from={SCENES.problem.from} durationInFrames={SCENES.problem.duration}><ProblemFrameworkScene /></Sequence>
    <Sequence from={SCENES.data.from} durationInFrames={SCENES.data.duration}><DataScene /></Sequence>
    <Sequence from={SCENES.method.from} durationInFrames={SCENES.method.duration}><MethodScene /></Sequence>
    <Sequence from={SCENES.results.from} durationInFrames={SCENES.results.duration}><ResultsScene /></Sequence>
    <Sequence from={SCENES.limit.from} durationInFrames={SCENES.limit.duration}><StopScene /></Sequence>
    <Sequence from={SCENES.agents.from} durationInFrames={SCENES.agents.duration}><AgentsScene /></Sequence>
    <Sequence from={SCENES.boundary.from} durationInFrames={SCENES.boundary.duration}><EvidenceBoundaryScene /></Sequence>
    <Sequence from={SCENES.loop.from} durationInFrames={SCENES.loop.duration}><LoopScene /></Sequence>
    <Sequence from={SCENES.close.from} durationInFrames={SCENES.close.duration}><YourTurnCloseScene /></Sequence>
  </AbsoluteFill>
);
