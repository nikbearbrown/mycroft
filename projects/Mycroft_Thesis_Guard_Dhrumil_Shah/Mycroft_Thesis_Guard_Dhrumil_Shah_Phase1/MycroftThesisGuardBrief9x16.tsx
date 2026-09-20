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
 * MycroftThesisGuardBrief9x16
 *
 * Native 2160x3840 (9:16) recomposition of MycroftThesisGuardBrief. Same
 * narration, same audio timing, same evidence assets, same 10-scene story —
 * every layout is redrawn for a portrait canvas (stacked instead of
 * side-by-side) rather than resized/cropped from the 16:9 master.
 */

export const MYCROFT_BRIEF_9X16_FPS = 24;
export const MYCROFT_BRIEF_9X16_TOTAL_FRAMES = 4320; // exactly 03:00 at 24 fps — identical to the 16:9 master

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
const SAFE = {left: 120, right: 120, top: 170, bottom: 170};

type AudioBeat = {id: string; seconds: number};

// Measured from the same supplied MP3 files as the 16:9 master. Unchanged —
// this is what keeps narration and duration identical across both cuts.
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

const toFrames = (seconds: number) => Math.round(seconds * MYCROFT_BRIEF_9X16_FPS);

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
  close: {from: timing('B12b').from, duration: MYCROFT_BRIEF_9X16_TOTAL_FRAMES - timing('B12b').from},
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

// Same public-dir namespace as the 16:9 master — the audio and evidence
// images are reused, not duplicated.
const sceneAsset = (path: string) => staticFile(`mycroft-brief/assets/evidence/${path}`);
const sceneAudio = (id: string) => staticFile(`mycroft-brief/audio/beat-${id}.mp3`);

const SourceTag: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div
    style={{
      position: 'absolute',
      left: SAFE.left,
      right: SAFE.right,
      bottom: SAFE.bottom - 6,
      padding: '18px 24px',
      border: `2px solid ${C.border}`,
      borderRadius: 14,
      background: 'rgba(250,249,245,0.96)',
      color: C.soft,
      fontFamily: MONO,
      fontSize: 27,
      fontWeight: 700,
      letterSpacing: 0.1,
      lineHeight: 1.3,
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
      <div style={{position: 'absolute', width: 560, height: 560, borderRadius: 560, left: -320, top: -300, background: C.accent, opacity: 0.035}} />
      <div style={{position: 'absolute', width: 600, height: 600, borderRadius: 600, right: -380, bottom: -360, background: C.ink, opacity: 0.025}} />
      <div style={{position: 'absolute', left: SAFE.left, top: 80, color: C.soft, fontFamily: MONO, fontSize: 25, fontWeight: 700, letterSpacing: 2}}>
        DHRUMIL SHAH
      </div>
      <div style={{position: 'absolute', right: SAFE.right, top: 80, color: C.soft, fontFamily: MONO, fontSize: 25, fontWeight: 700, letterSpacing: 2}}>
        {number} / 10
      </div>
      <div style={{position: 'absolute', left: SAFE.left, top: 120, color: C.ghost, fontFamily: MONO, fontSize: 20, fontWeight: 700, letterSpacing: 2.6}}>
        MYCROFT THESISGUARD
      </div>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: SAFE.top, color: C.soft, fontFamily: MONO, fontSize: 27, fontWeight: 700, letterSpacing: 2.6}}>
        {label.toUpperCase()}
      </div>
      {children}
      <SourceTag>{source}</SourceTag>
    </AbsoluteFill>
  );
};

const Headline: React.FC<{title: string; subtitle?: string; top?: number}> = ({title, subtitle, top = 280}) => (
  <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top, zIndex: 4}}>
    <div style={{fontFamily: SERIF, fontWeight: 700, color: C.ink, fontSize: 104, letterSpacing: '-0.03em', lineHeight: 0.98, whiteSpace: 'pre-line'}}>{title}</div>
    {subtitle ? <div style={{marginTop: 28, fontFamily: SERIF, color: C.soft, fontStyle: 'italic', fontSize: 44, lineHeight: 1.18}}>{subtitle}</div> : null}
  </div>
);

const Card: React.FC<{children: React.ReactNode; style?: React.CSSProperties; accent?: boolean}> = ({children, style, accent = false}) => (
  <div
    style={{
      boxSizing: 'border-box',
      background: accent ? C.accentWash : C.card,
      border: `${accent ? 3 : 2}px solid ${accent ? C.accent : C.border}`,
      borderRadius: 26,
      boxShadow: '0 22px 50px rgba(61,57,41,0.075)',
      ...style,
    }}
  >
    {children}
  </div>
);

const Reveal: React.FC<{delay: number; children: React.ReactNode; y?: number; x?: number; scale?: number}> = ({delay, children, y = 22, x = 0, scale = 0.97}) => {
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
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, padding: '16px 26px', background: 'rgba(250,249,245,0.95)', borderTop: `2px solid ${C.border}`, fontFamily: MONO, color: C.ink, fontSize: 25, fontWeight: 700}}>
        {caption}
      </div>
    </Card>
  );
};

// Down-chevron connector for vertical chains (replaces the 16:9 horizontal →).
const VArrow: React.FC<{delay: number}> = ({delay}) => (
  <Reveal delay={delay} y={0} scale={1}>
    <div style={{fontFamily: SERIF, color: C.soft, fontSize: 60, lineHeight: 1, textAlign: 'center'}}>↓</div>
  </Reveal>
);

const Stat: React.FC<{value: string; label: string; note?: string; accent?: boolean; delay: number}> = ({value, label, note, accent = false, delay}) => (
  <Reveal delay={delay}>
    <Card accent={accent} style={{padding: '38px 40px', minHeight: 270}}>
      <div style={{fontFamily: MONO, color: accent ? C.accentDeep : C.soft, fontSize: 23, fontWeight: 800, letterSpacing: 2}}>{label.toUpperCase()}</div>
      <div style={{marginTop: 20, fontFamily: SERIF, color: C.ink, fontSize: 82, fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 0.92}}>{value}</div>
      {note ? <div style={{marginTop: 16, fontFamily: SANS, color: C.soft, fontSize: 27, lineHeight: 1.2}}>{note}</div> : null}
    </Card>
  </Reveal>
);

const ChainToken: React.FC<{delay: number; title: string; note?: string; accent?: boolean}> = ({delay, title, note, accent = false}) => (
  <Reveal delay={delay} y={26}>
    <Card accent={accent} style={{padding: '40px 44px', minHeight: 226, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <div style={{fontFamily: SERIF, color: C.ink, fontSize: 68, fontWeight: 700, lineHeight: 0.95}}>{title}</div>
      {note ? <div style={{marginTop: 14, fontFamily: SANS, color: C.soft, fontSize: 30, lineHeight: 1.2}}>{note}</div> : null}
    </Card>
  </Reveal>
);

const OpeningScene: React.FC = () => {
  const title = useReveal(4);
  return (
    <SceneShell number="01" label="Executive summary" source="Implementation Report §1 · Notebook Cell 21" duration={SCENES.opening.duration}>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 290, opacity: title, transform: `translateY(${(1 - title) * 18}px)`}}>
        <div style={{fontFamily: SERIF, color: C.ink, fontSize: 116, fontWeight: 700, letterSpacing: '-0.035em', lineHeight: 0.95}}>Hi, I’m Dhrumil Shah.</div>
        <div style={{marginTop: 32, fontFamily: SERIF, color: C.soft, fontSize: 46, fontStyle: 'italic', lineHeight: 1.22}}>A three-minute evidence review of what Mycroft ThesisGuard does, what the run found, and where it stops.</div>
      </div>
      <Reveal delay={28} y={20}>
        <Card style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 870, padding: '44px 48px'}}>
          <div style={{fontFamily: MONO, color: C.soft, fontSize: 24, fontWeight: 800, letterSpacing: 2.2}}>THE REVIEW QUESTION</div>
          <div style={{marginTop: 22, fontFamily: SERIF, color: C.ink, fontSize: 68, fontWeight: 700, letterSpacing: '-0.015em', lineHeight: 1.1}}>Is the original thesis still supported by evidence?</div>
        </Card>
      </Reveal>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1400, display: 'flex', flexDirection: 'column', alignItems: 'stretch', gap: 48}}>
        <ChainToken delay={47} title="Claim" note="what was believed" />
        <VArrow delay={61} />
        <ChainToken delay={67} title="Evidence" note="what can be sourced" />
        <VArrow delay={81} />
        <ChainToken delay={87} title="Uncertainty" note="what changed or is missing" />
        <VArrow delay={101} />
        <ChainToken delay={107} title="Human" note="who makes the decision" accent />
      </div>
      <Reveal delay={134} y={0}>
        <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 3400, textAlign: 'center', fontFamily: MONO, color: C.accentDeep, fontSize: 28, fontWeight: 800, letterSpacing: 2}}>EVIDENCE-FIRST REVIEW · NOT PERSONALIZED FINANCIAL ADVICE</div>
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
      <Headline title="Thesis drift." subtitle="The position stays. The reason quietly moves." top={280} />
      <EvidenceImage file="report-problem-boundary.png" caption="Report §1 · problem statement and project objective" style={{left: SAFE.left, right: SAFE.right, top: 780, height: 820}} position="left top" zoom={1.08} />
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1720, display: 'flex', flexDirection: 'column', alignItems: 'stretch', gap: 36}}>
        <Reveal delay={50}><Card style={{padding: '42px 46px'}}><div style={{fontFamily: MONO, color: C.soft, fontSize: 24, fontWeight: 800, letterSpacing: 2}}>ILLUSTRATIVE THESIS EXAMPLE</div><div style={{marginTop: 20, fontFamily: SERIF, fontSize: 62, color: C.ink, fontWeight: 700}}>Growth could continue.</div></Card></Reveal>
        <VArrow delay={85} />
        <Reveal delay={100}><Card accent style={{padding: '42px 46px'}}><div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 24, fontWeight: 800, letterSpacing: 2}}>FACTS MOVE</div><div style={{marginTop: 20, fontFamily: SERIF, fontSize: 62, color: C.ink, fontWeight: 700}}>The story is rewritten.</div></Card></Reveal>
      </div>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2660, opacity: showFramework, transform: `translateY(${(1 - showFramework) * 22}px)`}}>
        <div style={{marginBottom: 14, fontFamily: MONO, color: C.accentDeep, fontWeight: 800, fontSize: 24, letterSpacing: 1.8}}>PRESENTER FRAMEWORK · CLEAR</div>
        <div style={{marginBottom: 26, fontFamily: SERIF, color: C.ink, fontWeight: 700, fontSize: 64}}>Not a buy-or-sell engine.</div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20}}>
          {clear.map(([letter, word], index) => (
            <Reveal key={letter} delay={315 + index * 16}>
              <Card accent={index === 4} style={{minHeight: 250, padding: '30px 26px'}}>
                <div style={{fontFamily: SERIF, fontSize: 76, color: index === 4 ? C.accentDeep : C.ink, fontWeight: 700, lineHeight: 0.85}}>{letter}</div>
                <div style={{marginTop: 16, fontFamily: SANS, color: C.soft, fontSize: 26, fontWeight: 700, lineHeight: 1.18}}>{word}</div>
              </Card>
            </Reveal>
          ))}
        </div>
      </div>
    </SceneShell>
  );
};

const DataScene: React.FC = () => (
  <SceneShell number="03" label="Validated inputs and causal features" source="Notebook Cells 5, 11, 25 · Implementation Report §3–4" duration={SCENES.data.duration}>
    <Headline title="Check what enters the model." subtitle="Validated data first; features use only what was knowable then." top={280} />
    <EvidenceImage file="notebook-features.png" caption="Notebook Cell 5 · feature definitions" style={{left: SAFE.left, right: SAFE.right, top: 820, height: 900}} position="left top" zoom={1.1} />
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1860, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 22}}>
      <Stat delay={30} label="Clean rows" value="184,138" note="recorded run output" />
      <Stat delay={48} label="Coverage" value="120" note="tickers and companies" />
      <Stat delay={66} label="Target" value="5 days" note="forward direction label" />
      <Stat delay={84} label="Rule" value="0 lookahead" note="future info excluded" accent />
    </div>
    <Reveal delay={107}>
      <Card style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2640, padding: '42px 48px'}}>
        <div style={{fontFamily: MONO, color: C.soft, fontSize: 24, fontWeight: 800, letterSpacing: 2}}>FEATURES SHOWN IN THE NOTEBOOK</div>
        <div style={{marginTop: 22, fontFamily: SERIF, color: C.ink, fontSize: 54, fontWeight: 700, lineHeight: 1.18}}>Returns · volatility · drawdowns · volume · sector-relative movement</div>
      </Card>
    </Reveal>
  </SceneShell>
);

const MethodScene: React.FC = () => {
  const models = ['Prior baseline', 'Logistic regression', 'Random forest', 'Extra Trees', 'Hist. gradient boost'];
  return (
    <SceneShell number="04" label="Chronological evaluation" source="Notebook Cells 13, 15, 25 · Implementation Report §3–4" duration={SCENES.method.duration}>
      <Headline title={'Split by time.\nBenchmark the baseline.'} subtitle="Random shuffling would leak the future." top={280} />
      <EvidenceImage file="notebook-time-split.png" caption="Notebook Cell 13 · create_time_splits()" style={{left: SAFE.left, right: SAFE.right, top: 800, height: 760}} position="left top" zoom={1.16} />
      <Reveal delay={28}>
        <Card style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1640, padding: '40px 44px'}}>
          <div style={{display: 'flex', height: 220, gap: 14}}>
            {[['70%', '127,858', 'TRAIN'], ['15%', '26,880', 'VALIDATE'], ['15%', '27,600', 'HOLDOUT'], ].map(([share, count, label], index) => (
              <div key={label} style={{flex: index === 0 ? 7 : 2, borderRadius: 16, padding: '22px 18px', background: index === 2 ? C.accentWash : C.darkWash, border: `${index === 2 ? 3 : 2}px solid ${index === 2 ? C.accent : C.border}`}}>
                <div style={{fontFamily: MONO, color: index === 2 ? C.accentDeep : C.soft, fontSize: 21, fontWeight: 800, letterSpacing: 1.4}}>{label}</div>
                <div style={{marginTop: 11, fontFamily: SERIF, color: C.ink, fontSize: 54, lineHeight: 0.9, fontWeight: 700}}>{count}</div>
                <div style={{fontFamily: SANS, color: C.soft, fontSize: 23}}>{share}</div>
              </div>
            ))}
          </div>
          <div style={{marginTop: 26, fontFamily: MONO, color: C.accentDeep, fontSize: 23, fontWeight: 800, letterSpacing: 1.2, lineHeight: 1.35}}>FIVE-DAY TARGET LABELS ARE PURGED AT EACH PARTITION BOUNDARY</div>
        </Card>
      </Reveal>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2280, display: 'flex', flexDirection: 'column', gap: 26}}>
        {models.map((model, index) => (
          <Reveal key={model} delay={115 + index * 13}>
            <Card style={{padding: '28px 36px', minHeight: 150, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontFamily: MONO, color: C.soft, fontSize: 22, fontWeight: 800, letterSpacing: 1.6}}>{index === 0 ? 'BENCHMARK' : `MODEL ${index + 1}`}</div>
              <div style={{fontFamily: SERIF, color: C.ink, fontSize: 50, lineHeight: 0.95, fontWeight: 700}}>{model}</div>
            </Card>
          </Reveal>
        ))}
      </div>
    </SceneShell>
  );
};

const ResultsScene: React.FC = () => (
  <SceneShell number="05" label="The worked result" source="Notebook Cell 25 recorded run · Implementation Report §4 outcomes table" duration={SCENES.results.duration}>
    <Headline title={'The honest result\nwas weak.'} subtitle="That is a finding—not a success claim to decorate." top={280} />
    <EvidenceImage file="report-and-run-outcomes.png" caption="Report §4 outcomes table · Notebook Cell 25 recorded output" style={{left: SAFE.left, right: SAFE.right, top: 820, height: 940}} position="left top" zoom={1.0} />
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1900, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 22}}>
      <Stat delay={24} label="Selected model" value="Logistic" note="chosen on validation" />
      <Stat delay={45} label="ROC AUC" value="0.5158" note="holdout; 0.50 is random" accent />
      <Stat delay={66} label="Brier score" value="0.2466" note="holdout calibration loss" />
      <Stat delay={87} label="Drift" value="Moderate" note="reported, not hidden" accent />
    </div>
    <Reveal delay={118}>
      <Card accent style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2540, padding: '46px 50px'}}>
        <div style={{fontFamily: SERIF, color: C.ink, fontSize: 58, lineHeight: 1.12, fontWeight: 700}}>Short-horizon price direction was not reliably predictable from this supplied data.</div>
      </Card>
    </Reveal>
  </SceneShell>
);

const StopScene: React.FC = () => (
  <SceneShell number="06" label="Falsifiability: the system may stop" source="Notebook Cell 21 · ThesisCaptureAgent and BehavioralBiasReviewAgent" duration={SCENES.limit.duration}>
    <Headline title="Do not invent the missing evidence." subtitle="The edge case is part of the method." top={280} />
    <EvidenceImage file="notebook-agent-classes.png" caption="Notebook Cell 21 · agent classes and returned status fields" style={{left: SAFE.left, right: SAFE.right, top: 800, height: 820}} position="left top" zoom={1.28} />
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1720, display: 'flex', flexDirection: 'column', gap: 28}}>
      <Stat delay={26} label="Original thesis" value="Not supplied" note="Thesis Capture returns needs_human_input" accent />
      <Stat delay={57} label="Behavioral bias" value="Not assessed" note="the prototype does not diagnose psychology without evidence" />
      <Stat delay={88} label="Decision state" value="Human review" note="missing source → insufficient evidence, not a verdict" accent />
    </div>
    <Reveal delay={140}>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2860, textAlign: 'center', color: C.accentDeep, fontFamily: MONO, fontSize: 36, fontWeight: 900, letterSpacing: 2.4}}>NO SOURCE · NO VERDICT</div>
    </Reveal>
  </SceneShell>
);

const AgentsScene: React.FC = () => {
  const frame = useCurrentFrame();
  const outcome = clamp(interpolate(frame, [230, 265], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
  const agents = ['Capture thesis', 'Retrieve evidence', 'Detect contradiction', 'Check bias', 'Human gate'];
  return (
    <SceneShell number="07" label="Agent workflow and human gate" source="Notebook Cell 21 · Notebook Cell 25 recorded run · Implementation Report §4" duration={SCENES.agents.duration}>
      <Headline title={'Five agents.\nOne human gate.'} subtitle="Automation organizes evidence; it does not decide." top={280} />
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 850, display: 'flex', flexDirection: 'column', alignItems: 'stretch', gap: 24}}>
        {agents.map((agent, index) => (
          <React.Fragment key={agent}>
            <ChainToken delay={30 + index * 20} title={agent} accent={index === 4} />
            {index < agents.length - 1 ? <VArrow delay={44 + index * 20} /> : null}
          </React.Fragment>
        ))}
      </div>
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2820, opacity: outcome, transform: `translateY(${(1 - outcome) * 22}px)`, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 18}}>
        <Stat delay={0} label="Reports" value="120" note="thesis-health reports" />
        <Stat delay={0} label="Trace events" value="600" note="agent trace events" />
        <Stat delay={0} label="Auto decisions" value="0" note="final actions stay human" accent />
      </div>
      <Reveal delay={310}>
        <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 3330, textAlign: 'center', fontFamily: MONO, color: C.soft, fontSize: 26, letterSpacing: 1.3, lineHeight: 1.3}}>MAINTAIN · REVISE · WATCHLIST · RETIRE — HUMAN GATE ONLY</div>
      </Reveal>
    </SceneShell>
  );
};

const EvidenceBoundaryScene: React.FC = () => (
  <SceneShell number="08" label="Evidence boundary" source="Notebook Cell 21 · Implementation Report §§2, 5" duration={SCENES.boundary.duration}>
    <Headline title="No source, no verdict." subtitle="Market data is not a substitute for a thesis or decision history." top={280} />
    <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 1150, display: 'flex', flexDirection: 'column', gap: 40}}>
      <Reveal delay={26}>
        <Card style={{padding: '46px 50px'}}>
          <div style={{fontFamily: MONO, color: C.soft, fontSize: 26, fontWeight: 900, letterSpacing: 2.4}}>AVAILABLE</div>
          <div style={{marginTop: 26, fontFamily: SERIF, color: C.ink, fontSize: 64, fontWeight: 700}}>Market evidence</div>
          {['prices and volume', 'engineered features', 'model scores and drift'].map((line) => (
            <div key={line} style={{marginTop: 24, fontFamily: SANS, color: C.ink, fontSize: 36}}>✓ {line}</div>
          ))}
        </Card>
      </Reveal>
      <Reveal delay={49}>
        <Card accent style={{padding: '46px 50px'}}>
          <div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 26, fontWeight: 900, letterSpacing: 2.4}}>NOT SUPPLIED</div>
          <div style={{marginTop: 26, fontFamily: SERIF, color: C.ink, fontSize: 64, fontWeight: 700}}>Decision evidence</div>
          {['original investment thesis', 'filings / news / calls', 'prior decision history'].map((line) => (
            <div key={line} style={{marginTop: 24, fontFamily: SANS, color: C.ink, fontSize: 36}}>— {line}</div>
          ))}
        </Card>
      </Reveal>
    </div>
    <Reveal delay={88}>
      <Card accent style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2620, padding: '38px 42px', textAlign: 'center'}}>
        <div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 26, fontWeight: 900, letterSpacing: 2.2}}>RETURNED STATUS</div>
        <div style={{marginTop: 18, fontFamily: SERIF, color: C.ink, fontSize: 50, fontWeight: 700, lineHeight: 1.18}}>insufficient evidence → human_review_required</div>
      </Card>
    </Reveal>
  </SceneShell>
);

const LoopScene: React.FC = () => {
  const stages = ['Validate', 'Engineer', 'Split by time', 'Evaluate', 'Monitor drift', 'Human review'];
  return (
    <SceneShell number="09" label="The auditable loop" source="Notebook Cells 13, 25, 50, 69 · Implementation Report §4" duration={SCENES.loop.duration}>
      <Headline title="Every stage leaves a record." subtitle="The end-to-end loop is a chain of artifacts a reviewer can inspect." top={280} />
      <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 800, display: 'flex', flexDirection: 'column', alignItems: 'stretch', gap: 18}}>
        {stages.map((stage, index) => (
          <React.Fragment key={stage}>
            <ChainToken delay={24 + index * 20} title={stage} accent={index === stages.length - 1} />
            {index < stages.length - 1 ? <VArrow delay={36 + index * 20} /> : null}
          </React.Fragment>
        ))}
      </div>
      <EvidenceImage file="notebook-visualization-scope.png" caption="Notebook Cell 50 · recorded list of nine generated figure files" style={{left: SAFE.left, right: SAFE.right, top: 2760, height: 420}} position="left top" zoom={1.13} />
      <Reveal delay={135}>
        <Card accent style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 3230, padding: '26px 30px'}}>
          <div style={{fontFamily: MONO, color: C.accentDeep, fontSize: 22, fontWeight: 900, letterSpacing: 1.6}}>VISUALIZATION EVIDENCE</div>
          <div style={{marginTop: 14, fontFamily: SERIF, color: C.ink, fontSize: 32, lineHeight: 1.05, fontWeight: 700}}>Nine figure filenames were recorded — not invented charts.</div>
        </Card>
      </Reveal>
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
        <Headline title="Run the review yourself." subtitle="A reusable scaffold—not a vague prompt." top={280} />
        <Card style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 760, padding: '56px 60px'}}>
          {rows.map(([n, name, prompt], index) => (
            <Reveal key={n} delay={24 + index * 17} y={12}>
              <div style={{paddingBottom: 44, marginTop: index === 0 ? 0 : 44, borderBottom: index === rows.length - 1 ? 'none' : `2px solid ${C.border}`}}>
                <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
                  <div style={{width: 56, height: 56, minWidth: 56, borderRadius: 56, background: index === rows.length - 1 ? C.accent : C.wash, color: index === rows.length - 1 ? C.card : C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: MONO, fontSize: 25, fontWeight: 900}}>{n}</div>
                  <div style={{fontFamily: SERIF, color: C.ink, fontSize: 50, fontWeight: 700}}>{name}</div>
                </div>
                <div style={{marginTop: 10, marginLeft: 78, fontFamily: SANS, color: C.soft, fontSize: 32}}>{prompt}</div>
              </div>
            </Reveal>
          ))}
        </Card>
        <Reveal delay={118}>
          <div style={{position: 'absolute', left: SAFE.left, right: SAFE.right, top: 2760, textAlign: 'center', fontFamily: MONO, color: C.accentDeep, fontSize: 28, fontWeight: 900, letterSpacing: 1.6, lineHeight: 1.35}}>IF THE CLAIM OR SOURCE IS MISSING: RECORD INSUFFICIENT EVIDENCE.</div>
        </Reveal>
      </div>
      <div style={{position: 'absolute', inset: 0, opacity: outroOpacity, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', textAlign: 'center', padding: `0 ${SAFE.left}px`}}>
        <div style={{fontFamily: SERIF, color: C.ink, fontSize: 118, fontWeight: 700, letterSpacing: '-0.04em', lineHeight: 0.98}}>Mycroft ThesisGuard<span style={{color: C.accentDeep}}>.</span></div>
        <div style={{marginTop: 40, fontFamily: SERIF, color: C.soft, fontSize: 50, fontStyle: 'italic', lineHeight: 1.15}}>Evidence first. Uncertainty visible. Judgment human.</div>
        <div style={{marginTop: 80, padding: '22px 28px', border: `2px solid ${C.border}`, borderRadius: 15, background: C.card, fontFamily: SANS, color: C.soft, fontSize: 27, lineHeight: 1.3}}>Educational research and model output; not personalized financial advice or an investment recommendation.</div>
        <div style={{marginTop: 32, fontFamily: MONO, color: C.accentDeep, fontSize: 26, fontWeight: 900, letterSpacing: 2}}>DHRUMIL SHAH · 2026</div>
      </div>
    </SceneShell>
  );
};

export const MycroftThesisGuardBrief9x16: React.FC = () => (
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
