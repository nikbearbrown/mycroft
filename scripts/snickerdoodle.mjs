#!/usr/bin/env node
// snickerdoodle.mjs
//
// The command-line surface that 97 of the 99 recipes already document and that, until
// now, did not exist. Every recipe ends with a Snickerdoodle section telling the reader
// to run `snickerdoodle run <recipe> --step <name>` and
// `snickerdoodle gate <recipe> --gate N --decision approve --note "..."`. In practice the
// step scripts were invoked by hand with `python3 scripts/<layer>/<recipe>-<step>.py`,
// and gate decisions were written as JSON by hand.
//
// THE RECIPE IS THE CONFIG
//
// This tool has no config file and no registry of recipes. It reads the recipe markdown
// and uses the four tables every recipe already carries:
//
//   ### Step Commands     slug -> step name, and which flags that step accepts
//   ### Script Locations  step name -> script path, and which layer it belongs to
//   ### Gate Commands     gate number -> the command, including its note
//   ## Phase Gates        gate number -> name, testable condition, human capacity
//
// That is deliberate. A separate manifest would be a second source of truth for the same
// facts, free to drift from the recipe, and P6 says intent lives in the recipe. Parsing
// the recipe means a step renamed there is renamed here, with nothing to keep in sync.
//
// WHAT IT WILL NOT DO
//
//   - It does not invent steps. An unknown --step lists the ones the recipe declares.
//   - It does not invent a script. If the recipe names a path that does not exist, it
//     says so and stops, rather than guessing a filename from the slug.
//   - `gate` runs the gate's own test from the recipe and records what it actually saw.
//     It does not accept a decision for a gate whose test it could not run, because a
//     decision with no evidence is the "looks good" that P4 exists to forbid.
//   - `gate` will not overwrite an existing decision without --force. A gate decision is
//     a record of a judgment someone made on a date; silently replacing one is editing
//     history.

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const RECIPES_DIR = 'recipes';
const GATE_DIR = 'logs/gate-decisions';

// ---------------------------------------------------------------------------
// small helpers
// ---------------------------------------------------------------------------

const bold = (s) => `\u001b[1m${s}\u001b[0m`;
const dim = (s) => `\u001b[2m${s}\u001b[0m`;

function die(msg, code = 2) {
  console.error(`snickerdoodle: ${msg}`);
  process.exit(code);
}

function pythonCmd() {
  for (const c of ['python3', 'python', 'py']) {
    try {
      execFileSync(c, ['--version'], { stdio: 'pipe' });
      return c;
    } catch { /* try the next candidate */ }
  }
  die('no python interpreter found (tried python3, python, py)');
  return 'python3';
}

// Markdown table rows look like: | a | b | c |
function tableRows(section) {
  return section
    .split('\n')
    .filter((l) => l.trim().startsWith('|') && !/^\s*\|[\s|:-]+\|\s*$/.test(l))
    .map((l) => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim()))
    .filter((cells) => cells.length >= 2);
}

function section(text, heading) {
  // Capture from the heading to the next heading of the same or higher level.
  const level = heading.match(/^#+/)[0].length;
  const re = new RegExp(`^${heading}\\s*$`, 'm');
  const m = text.match(re);
  if (!m) return '';
  const rest = text.slice(m.index + m[0].length);
  const stop = rest.search(new RegExp(`^#{1,${level}} `, 'm'));
  return stop === -1 ? rest : rest.slice(0, stop);
}

const backtick = (s) => (s.match(/`([^`]+)`/) || [null, s])[1];

// ---------------------------------------------------------------------------
// recipe parsing
// ---------------------------------------------------------------------------

function loadRecipe(name) {
  const slug = name.replace(/\.md$/, '');
  const file = path.join(RECIPES_DIR, `${slug}.md`);
  if (!fs.existsSync(file)) {
    const avail = fs.existsSync(RECIPES_DIR)
      ? fs.readdirSync(RECIPES_DIR).filter((f) => f.endsWith('.md')).length
      : 0;
    die(`no recipe at ${file}\n  ${avail} recipes exist; try: snickerdoodle list`);
  }
  const text = fs.readFileSync(file, 'utf8');

  // --- steps: slug -> { name, flags, script, layer } -------------------------
  const steps = new Map();
  for (const cells of tableRows(section(text, '### Step Commands'))) {
    const [stepName, command, flags = ''] = cells;
    if (/^Step$/i.test(stepName)) continue;
    const slugMatch = command.match(/--step\s+([a-z0-9-]+)/);
    if (!slugMatch) continue;
    steps.set(slugMatch[1], {
      slug: slugMatch[1],
      name: stepName,
      flags: (flags.match(/`--[a-z-]+`/g) || []).map((f) => f.replace(/`/g, '')),
      script: null,
      layer: null,
    });
  }
  // Script Locations keys on the step NAME, so join on that.
  for (const cells of tableRows(section(text, '### Script Locations'))) {
    const [stepName, scriptPath, layer = ''] = cells;
    if (/^Step$/i.test(stepName)) continue;
    const entry = [...steps.values()].find((s) => s.name === stepName);
    if (entry) {
      entry.script = backtick(scriptPath);
      entry.layer = layer;
    }
  }

  // --- gates: N -> { name, condition, test, capacity } -----------------------
  const gates = new Map();
  for (const line of section(text, '## Phase Gates').split('\n')) {
    const m = line.match(/^\s*(\d+)\.\s*(.+?):\s*(.*)$/);
    if (!m) continue;
    const [, num, gname, rest] = m;
    const test = (rest.match(/Test:\s*`([^`]+)`/) || [])[1] || null;
    const capacity = (rest.match(/Human capacity:\s*\[([A-Z]+)\]/) || [])[1] || null;
    const condition = rest.split(/Test:/)[0].trim().replace(/\.$/, '');
    gates.set(Number(num), { gate: Number(num), name: gname.trim(), condition, test, capacity });
  }

  // --- frontmatter -----------------------------------------------------------
  const fm = {};
  const fmBlock = text.startsWith('---\n') ? text.slice(4, text.indexOf('\n---', 4)) : '';
  for (const line of fmBlock.split('\n')) {
    const m = line.match(/^([a-z_]+):\s*(.*)$/);
    if (m) fm[m[1]] = m[2].replace(/^["']|["']$/g, '');
  }

  const title = (text.match(/^#\s+(.+)$/m) || [null, slug])[1];
  return { slug, file, text, title, steps, gates, frontmatter: fm };
}

// ---------------------------------------------------------------------------
// run
// ---------------------------------------------------------------------------

function runStep(recipe, step, passthrough, { quiet = false } = {}) {
  if (!step.script) {
    die(`recipe declares no script path for step "${step.slug}"\n  add it to the Script Locations table in ${recipe.file}`);
  }
  if (!fs.existsSync(step.script)) {
    die(
      `the recipe names a script that does not exist:\n  ${step.script}\n` +
      `  declared for step "${step.slug}" in ${recipe.file}\n` +
      '  this step is not built yet; snickerdoodle will not guess a different path',
    );
  }
  // Only pass a flag to a step that the RECIPE says that step accepts. The recipe is
  // the contract; sending a step a flag it never advertised is how a runner papers over
  // a mismatch between what is documented and what is built.
  //
  // There is no special case here on purpose. An earlier version let --fixture-set ride
  // along wherever --sample was allowed, reasoning that it was "an argument to --sample".
  // It was passed straight to a step that does not implement it, which is exactly the
  // guessing this filter exists to prevent. The fix was to document the flag in the
  // recipe for the five steps that do implement it, so the table decides.
  const allowed = new Set(step.flags);
  const VALUED = new Set(['--fixture-set']);
  const filtered = [];
  const dropped = [];
  for (let i = 0; i < passthrough.length; i += 1) {
    const f = passthrough[i];
    if (!f.startsWith('--')) { filtered.push(f); continue; }
    const takesValue = VALUED.has(f);
    if (allowed.has(f)) {
      filtered.push(f);
      if (takesValue && passthrough[i + 1] !== undefined) filtered.push(passthrough[i + 1]);
    } else {
      dropped.push(f);
    }
    if (takesValue) i += 1;
  }
  if (dropped.length) {
    console.error(dim(`  ${dropped.join(' ')} not declared for this step in the recipe — not passed`));
  }
  if (!quiet) console.error(dim(`→ ${step.slug}  ${step.script}`));
  const r = spawnSync(pythonCmd(), [step.script, ...filtered], { stdio: 'inherit' });
  if (r.status === 2) {
    // argparse exits 2 on an unrecognised argument. That means the recipe advertises a
    // flag the script does not implement -- a recipe/script disagreement, which P6 calls
    // a logged defect. Name it rather than letting it read as a step failure.
    console.error(dim(`  (exit 2 from argparse usually means ${recipe.file} advertises a flag this script does not implement)`));
  }
  return r.status === null ? 1 : r.status;
}

function cmdRun(argv) {
  const recipeName = argv._[0];
  if (!recipeName) die('usage: snickerdoodle run <recipe> [--step <name>] [--mode dialogic] [--sample] [--no-write]');
  const recipe = loadRecipe(recipeName);

  const passthrough = [];
  if (argv.sample) passthrough.push('--sample');
  if (argv['no-write']) passthrough.push('--no-write');
  if (argv['fixture-set']) passthrough.push('--fixture-set', argv['fixture-set']);

  if (argv.step) {
    const step = recipe.steps.get(argv.step);
    if (!step) {
      die(`unknown step "${argv.step}"\n  ${recipe.slug} declares:\n` +
          [...recipe.steps.keys()].map((s) => `    ${s}`).join('\n'));
    }
    process.exit(runStep(recipe, step, passthrough));
  }

  // No --step: run the whole flow in the order the recipe lists it.
  if (argv.mode && argv.mode !== 'dialogic') {
    die(`--mode ${argv.mode} is not available. Only dialogic mode exists; silent mode is earned, not configured (P8).`);
  }
  const steps = [...recipe.steps.values()];
  if (!steps.length) die(`${recipe.slug} declares no steps`);

  console.error(bold(`${recipe.title}`) + dim(`  ·  ${steps.length} steps  ·  mode dialogic`));
  const results = [];
  for (const step of steps) {
    const code = runStep(recipe, step, passthrough);
    results.push({ step: step.slug, code });
    if (code !== 0) {
      // A nonzero exit is a hard stop, not a warning. The step has already reported
      // everything it found; continuing past it would be proceeding past a judgment.
      console.error(`\n${bold('STOPPED')} at step "${step.slug}" (exit ${code}).`);
      console.error(dim('  The step reported its findings above. A human decides whether to continue.'));
      process.exit(code);
    }
  }
  console.error(`\n${bold('All ' + results.length + ' steps completed.')}`);
  console.error(dim('  Completing is not passing. Gate decisions are a separate, human act:'));
  console.error(dim(`    snickerdoodle gate ${recipe.slug} --gate 1 --decision approve --note "..."`));
}

// ---------------------------------------------------------------------------
// gate
// ---------------------------------------------------------------------------

function declaredMode(recipe) {
  const envelope = `data/raw/${recipe.slug}/run-envelope.json`;
  if (!fs.existsSync(envelope)) return { mode: null, source: null };
  try {
    return { mode: JSON.parse(fs.readFileSync(envelope, 'utf8')).mode || null, source: envelope };
  } catch { return { mode: null, source: envelope }; }
}

function whoAmI(explicit) {
  if (explicit) return explicit;
  try {
    return execFileSync('git', ['config', 'user.name'], { encoding: 'utf8' }).trim() || null;
  } catch { return null; }
}

// The gate tests in every recipe are POSIX shell: `test -f ...`, `find ... -exec ... \;`,
// `rg ... || true`. Node's `shell: true` uses cmd.exe on Windows, which cannot run any of
// that -- `find` there is a different program entirely. Running the tests under cmd.exe
// made gate 3 report a failure for a test that passes, which would have been recorded as
// real evidence. Run them in a POSIX shell, and say so if none is available rather than
// reporting a shell mismatch as a failed gate.
function posixShell() {
  for (const sh of ['bash', 'sh']) {
    try {
      execFileSync(sh, ['-c', 'exit 0'], { stdio: 'pipe' });
      return sh;
    } catch { /* try the next */ }
  }
  return null;
}

// The hand-written records from week five carried an evidence set: the files the decision
// rests on, each with its SHA-256, so a reader can confirm they are looking at what was
// judged. Deriving that set has to be principled rather than a guess, so it comes from the
// gate's OWN test: the paths the test names are the files the gate is about. The recipe is
// added because every gate decision rests on the version of the recipe it was made against.
//
// Directories are expanded one level into their files; a path that does not exist is
// recorded as absent rather than skipped, because "the evidence was missing" is itself
// evidence about the decision.
function gateEvidenceFiles(recipe, gate) {
  const seen = new Map();
  const addFile = (p) => {
    const rel = p.split(path.sep).join('/');
    if (seen.has(rel)) return;
    let sha = null;
    let bytes = null;
    try {
      const buf = fs.readFileSync(rel);
      sha = createHash('sha256').update(buf).digest('hex');
      bytes = buf.length;
    } catch { /* unresolved; described below */ }
    if (sha !== null) {
      seen.set(rel, { path: rel, resolved: true, sha256: sha, size_bytes: bytes });
      return;
    }
    // Not every path-shaped token in a shell command is a path. Gate 4's test is
    // `for s in tools/verify-provenance ingest/ingest-inputs ...` -- those are loop
    // VALUES; gate 6's names logs/<recipe>-[DATE].json, a template. Calling either an
    // "absent file" would assert something missing that is not, so an unresolved token
    // is recorded as exactly that, with its ambiguity named.
    seen.set(rel, {
      path: rel,
      resolved: false,
      sha256: null,
      note: 'named by the gate test but not a file on disk — a loop value, a template '
        + 'such as [DATE], or a genuinely missing file; this record does not distinguish them',
    });
  };

  addFile(recipe.file);

  // Pull path-shaped tokens out of the gate's test command.
  const tokens = (gate.test || '').match(/[A-Za-z0-9_./-]+\/[A-Za-z0-9_./*-]+/g) || [];
  for (const raw of tokens) {
    const t = raw.replace(/["'`]/g, '');
    if (t.includes('*')) continue;            // a glob is not a file
    if (!fs.existsSync(t)) { addFile(t); continue; }
    const st = fs.statSync(t);
    if (st.isDirectory()) {
      // Walk the tree, not one level. Gate 3's test names data/raw/<slug> and
      // data/verified/<slug>, whose artifacts live two levels down under sample/ and
      // runs/ -- stopping at depth 1 hashed the directory's children and missed every
      // file the gate is actually about.
      walk(t, (f) => addFile(f));
    } else addFile(t);
  }
  const files = [...seen.values()];
  // A decision record is read by a person. Hashing an unbounded tree would bury the
  // decision under its own evidence, so cap it and say that the cap was hit.
  if (files.length > EVIDENCE_CAP) {
    const kept = files.slice(0, EVIDENCE_CAP);
    kept.push({
      path: `… ${files.length - EVIDENCE_CAP} more file(s) not listed`,
      resolved: true,
      sha256: null,
      truncated: true,
      total_matched: files.length,
      note: `evidence set capped at ${EVIDENCE_CAP}; the gate test covers all of them`,
    });
    return kept;
  }
  return files;
}

const EVIDENCE_CAP = 60;

function walk(dir, onFile, depth = 0) {
  if (depth > 6) return;
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, onFile, depth + 1);
    else if (e.isFile()) onFile(p);
  }
}

// Does a RUN_LOG entry exist for today? The record should point at one, but asserting a
// pointer to an entry nobody wrote is exactly the broken link P3 is about. Check, and say
// what was found either way.
function runLogRef(today) {
  const file = 'logs/RUN_LOG.md';
  if (!fs.existsSync(file)) return { path: file, entry_exists: false, note: 'no RUN_LOG at that path' };
  const text = fs.readFileSync(file, 'utf8');
  const has = new RegExp(`^## ${today}\\b`, 'm').test(text);
  return {
    path: `${file}#${today}`,
    entry_exists: has,
    note: has ? null : `no "## ${today}" entry yet — log this decision; a decision not logged is not durable evidence`,
  };
}

function runGateTest(test) {
  if (!test) return { ran: false, reason: 'the recipe declares no test for this gate' };
  const sh = posixShell();
  if (!sh) {
    return {
      ran: false,
      command: test,
      reason: 'no POSIX shell (bash or sh) available; the recipe gate tests are POSIX shell '
        + 'and will not run under cmd.exe. Install one, or run the test by hand and record '
        + 'the result with --residual-risk.',
    };
  }
  const r = spawnSync(sh, ['-c', test], { encoding: 'utf8' });
  const out = `${r.stdout || ''}${r.stderr || ''}`.trim();
  return {
    ran: true,
    shell: sh,
    command: test,
    exit_code: r.status === null ? -1 : r.status,
    passed: r.status === 0,
    output_tail: out.split('\n').slice(-6).join('\n').slice(0, 1200) || null,
  };
}

function cmdGate(argv) {
  const recipeName = argv._[0];
  if (!recipeName) die('usage: snickerdoodle gate <recipe> --gate N --decision approve|deny|defer --note "..."');
  const recipe = loadRecipe(recipeName);

  const num = Number(argv.gate);
  if (!Number.isInteger(num)) die('--gate N is required (an integer)');
  const gate = recipe.gates.get(num);
  if (!gate) {
    die(`${recipe.slug} declares no gate ${num}\n  gates: ${[...recipe.gates.keys()].join(', ') || 'none'}`);
  }

  const decision = argv.decision;
  if (!['approve', 'deny', 'defer'].includes(decision)) {
    die('--decision must be approve, deny or defer\n  deny and defer are real outcomes: a gate decided "no" is a closed gate, an unexamined one is not');
  }
  if (!argv.note) die('--note "..." is required. "Looks good" is not a handoff condition (P4); say what you judged.');

  const by = whoAmI(argv.by);
  if (!by) die('--by "Name" is required (git user.name is unset). A gate is cleared by a NAMED human (P4).');

  // Some gates govern outward-facing, irreversible actions -- a model call, a message
  // sent, an external write. Their tests are necessarily negative: gate 5's passes
  // because nothing has performed a live call, which is evidence that nothing HAS run,
  // never evidence that running is approved. Letting a passing test carry such an
  // approval is the category error P4 calls clearing on vibes, so approving one of these
  // takes a second, explicit act.
  //
  // Which gates these are is read from the recipe's own wording, not hardcoded to a
  // number -- gate 5 happens to be the approval gate in this recipe's template, and that
  // is a fact about the template rather than about gates.
  const governsLive = /live (network )?call|external write|credential|publish|notification|model call/i
    .test(`${gate.condition} ${gate.name}`);
  if (decision === 'approve' && governsLive && !argv['authorize-live']) {
    die(
      `gate ${num} ("${gate.name}") governs live or external action.\n` +
      `  condition: ${gate.condition}\n` +
      "  Its test passing means nothing has run unapproved -- that is not evidence FOR an approval.\n" +
      '  Approving it authorises irreversible outward-facing actions. If you intend that,\n' +
      '  pass --authorize-live as well, and write a note that says what you checked.\n' +
      '  To record a refusal instead: --decision deny',
    );
  }

  const evidence = runGateTest(gate.test);
  if (decision === 'approve' && evidence.ran && !evidence.passed) {
    die(
      `refusing to record an approval: this gate's own test failed (exit ${evidence.exit_code}).\n` +
      `  test: ${gate.test}\n` +
      '  approve a gate whose test fails and the test stops meaning anything.\n' +
      '  fix the failure, or record --decision deny / defer with a note explaining why.',
    );
  }

  // Local date, not toISOString(): that is UTC and can read a day ahead of the person
  // recording the decision, which is confusing in a record whose whole point is who
  // decided what, when.
  const now = new Date();
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  const { mode, source: modeSource } = declaredMode(recipe);
  const evidenceFiles = gateEvidenceFiles(recipe, gate);
  const unresolvedEvidence = evidenceFiles.filter((f) => f.resolved === false).length;

  // What was SEEN, assembled from the test that actually ran -- not a restatement of the
  // operator's note, which is what they concluded.
  const observed = evidence.ran
    ? `Gate test exited ${evidence.exit_code} (${evidence.passed ? 'passed' : 'failed'}) under ${evidence.shell}. `
      + `${evidenceFiles.length - unresolvedEvidence} evidence file(s) hashed, ${unresolvedEvidence} token(s) unresolved.`
      + (evidence.output_tail ? ` Output tail: ${evidence.output_tail.split(/\r?\n/).slice(-2).join(' / ')}` : '')
    : `No test run: ${evidence.reason}. ${evidenceFiles.length - unresolvedEvidence} evidence file(s) hashed, ${unresolvedEvidence} token(s) unresolved.`;

  const record = {
    workflow: recipe.title,
    recipe: recipe.file.split(path.sep).join('/'),
    recipe_version: recipe.frontmatter.recipe_version || null,
    gate: num,
    gate_name: gate.name,
    human_capacity: gate.capacity ? `[${gate.capacity}]` : null,
    handoff_condition: gate.condition,
    decision,
    note: argv.note,
    decided_by: { name: by, role: argv.role || 'recipe owner' },
    decided_at: today,
    mode,
    mode_source: modeSource,
    scope: mode === 'sample'
      ? 'This decision covers the sample run over the frozen fixture corpus only. It says nothing about live execution.'
      : mode
        ? `This decision covers a run declared mode=${mode}.`
        : 'No run envelope declares a mode, so the scope of this decision is not established by any artifact.',
    evidence_observed: observed,
    evidence_files: evidenceFiles,
    run_log: runLogRef(today),
    governs_live_action: governsLive,
    approved_for_live_action: decision === 'approve' && governsLive && Boolean(argv['authorize-live']),
    gate_test: evidence,
    recorded_by: 'scripts/snickerdoodle.mjs',
    residual_risk: argv['residual-risk'] || (
      'NOT STATED by the decider. What the gate test establishes is conformance; whether the '
      + 'result is ADEQUATE is a human judgment and no test captures it (P1). '
      + (unresolvedEvidence
        ? `${unresolvedEvidence} token(s) in the gate test did not resolve to a file, so the evidence set may be partial. `
        : '')
      + 'Pass --residual-risk to replace this with what you actually judged to be left open.'
    ),
    residual_risk_stated: Boolean(argv['residual-risk']),
    voids_if: 'Any edit to the recipe or its step scripts, or any change to the data this gate was cleared against, voids this decision.',
  };

  fs.mkdirSync(GATE_DIR, { recursive: true });
  const out = path.join(GATE_DIR, `${recipe.slug}-gate-${num}.json`);
  if (fs.existsSync(out) && !argv.force) {
    const prev = JSON.parse(fs.readFileSync(out, 'utf8'));
    die(
      `a decision for gate ${num} already exists:\n` +
      `  ${out}\n` +
      `  ${prev.decision} by ${prev.decided_by?.name || '?'} on ${prev.decided_at}\n` +
      '  a gate decision records a judgment someone made on a date; replacing one is editing history.\n' +
      '  pass --force if you intend to supersede it.',
    );
  }
  fs.writeFileSync(out, `${JSON.stringify(record, null, 2)}\n`, 'utf8');

  console.error(`${bold(`gate ${num} — ${gate.name}`)}  ${decision.toUpperCase()}`);
  console.error(dim(`  by ${by} on ${today}`));
  if (evidence.ran) {
    console.error(dim(`  test ${evidence.passed ? 'passed' : `FAILED (exit ${evidence.exit_code})`}: ${gate.test}`));
  } else {
    console.error(dim(`  no test recorded: ${evidence.reason}`));
  }
  console.error(dim(`  written to ${out}`));
  console.error(dim('  log it in logs/RUN_LOG.md — a decision not logged is not durable evidence.'));
}

// ---------------------------------------------------------------------------
// check — does the recipe describe the scripts that exist?
// ---------------------------------------------------------------------------

// Every script carries --input and --output as plumbing, and no Step Commands table
// documents them. Counting them as "built but undocumented" would bury the real
// findings under 6 lines of noise per recipe.
const PLUMBING = new Set(['--input', '--output', '--help']);

// Read the flags a script accepts without executing it. argparse calls put the flag in
// the first string argument, sometimes on the following line, so match across newlines.
function scriptFlags(file) {
  const src = fs.readFileSync(file, 'utf8');
  const out = new Set();
  const re = /add_argument\(\s*['"](--[a-z][a-z0-9-]*)['"]/g;
  let m;
  while ((m = re.exec(src)) !== null) out.add(m[1]);
  return out;
}

// A missing script is only a defect if the recipe CLAIMS it should be there.
//
// SNICKERDOODLE's lifecycle settles when that is: a DEV todo closes on "script exists",
// and DRAFT -> SPECIFIED requires zero open todos. So scripts must exist from SPECIFIED
// onward. At DRAFT their absence is not a defect -- it is what DRAFT means.
//
// The first version of this check ignored status and reported every unbuilt step as a
// finding, which made 94 of 97 recipes look broken and buried the ~20 real contract
// mismatches under ~600 entries for work that simply has not been done yet.
const BUILT_EXPECTED_FROM = ['SPECIFIED', 'RUNNABLE-SAMPLE', 'RUNNABLE-LIVE', 'VERIFIED'];

function checkRecipe(recipe) {
  const findings = [];
  let comparable = 0; // steps whose script exists, so its flags could be compared
  // severity: 'defect' contradicts something the recipe claims; 'expected' is the
  // honest state of unbuilt work and must not be counted as breakage.
  const add = (kind, where, detail, severity = 'defect') => findings.push({ kind, where, detail, severity });

  const status = recipe.frontmatter.status || null;
  const claimsBuilt = BUILT_EXPECTED_FROM.includes(status);

  if (!status) {
    add('no-lifecycle-status', 'recipe', 'no status frontmatter, so the recipe claims nothing and nothing can contradict it');
  }

  for (const step of recipe.steps.values()) {
    if (!step.script) {
      add('no-script-declared', step.slug, 'the Script Locations table has no row for this step');
      continue;
    }
    if (!fs.existsSync(step.script)) {
      if (claimsBuilt) {
        add('script-missing', step.slug, `status is ${status}, which requires this script to exist: ${step.script}`);
      } else {
        add('step-not-built', step.slug, `${step.script} does not exist`
          + (status ? ` — expected at status ${status}` : ' — the recipe claims no status'), 'expected');
      }
      continue;
    }
    comparable += 1;
    const impl = scriptFlags(step.script);
    for (const f of step.flags) {
      if (!impl.has(f)) {
        add('documented-not-built', step.slug, `recipe advertises ${f}; the script does not implement it`);
      }
    }
    for (const f of impl) {
      if (PLUMBING.has(f)) continue;
      if (!step.flags.includes(f)) {
        add('built-not-documented', step.slug, `script implements ${f}; the recipe does not list it`);
      }
    }
  }

  for (const gate of recipe.gates.values()) {
    if (!gate.test) add('gate-without-test', `gate ${gate.gate}`, `"${gate.name}" declares no testable condition`);
    if (!gate.capacity) add('gate-without-capacity', `gate ${gate.gate}`, `"${gate.name}" names no human capacity`);
  }

  if (!recipe.steps.size) add('no-steps', 'recipe', 'declares no steps in its Step Commands table');
  return { findings, comparable };
}

function cmdCheck(argv) {
  const all = argv.all || !argv._[0];
  const slugs = all
    ? fs.readdirSync(RECIPES_DIR)
      .filter((f) => f.endsWith('.md') && !['_shared.md', 'README.md'].includes(f))
      .map((f) => f.replace(/\.md$/, ''))
    : [argv._[0].replace(/\.md$/, '')];

  const byKind = new Map();
  const perRecipe = [];
  let scanned = 0;

  for (const slug of slugs) {
    let recipe;
    try { recipe = loadRecipe(slug); } catch { continue; }
    scanned += 1;
    const { findings, comparable } = checkRecipe(recipe);
    perRecipe.push({ slug, findings, comparable, steps: recipe.steps.size });
    for (const f of findings) {
      if (!byKind.has(f.kind)) byKind.set(f.kind, new Set());
      byKind.get(f.kind).add(`${slug}::${f.where}::${f.detail.replace(/^.*?(--[a-z-]+).*$/, '$1')}`);
    }
  }

  const comparableOf = (r) => r.comparable;
  if (!all) {
    const { slug, findings } = perRecipe[0];
    const defects = findings.filter((f) => f.severity !== 'expected');
    const expected = findings.filter((f) => f.severity === 'expected');
    const status = loadRecipe(slug).frontmatter.status || 'no status';
    console.log(`${bold(slug)}  ${dim(status)}  ${defects.length ? `${defects.length} defect(s)` : 'no contract defects'}\n`);
    for (const f of defects) {
      console.log(`  ${f.kind.padEnd(24)} ${f.where.padEnd(26)} ${f.detail}`);
    }
    if (!defects.length) {
      // Do not claim the scripts match when there are none. "No defects" on an unbuilt
      // DRAFT means nothing contradicts its claims, which is a much weaker statement.
      console.log(dim(expected.length
        ? `  Nothing here contradicts what the recipe claims. ${expected.length} of its `
          + `${expected.length + comparableOf(perRecipe[0])} step(s) are unbuilt, which is what status ${status} means.`
        : '  every declared step has a script, and its flags match what the script implements.'));
    }
    if (expected.length) {
      console.log(dim(`\n  ${expected.length} step(s) not built — expected at this status, not counted as defects:`));
      for (const f of expected) console.log(dim(`    ${f.where.padEnd(26)} ${f.detail}`));
    }
    process.exit(defects.length ? 1 : 0);
  }

  // Repo-wide: the point is to show whether a finding is one shared defect or many
  // separate ones. A kind that appears in nearly every recipe came from the template.
  const defectsOf = (r) => r.findings.filter((f) => f.severity !== 'expected');
  const affected = new Map();
  for (const r of perRecipe) {
    for (const f of new Set(defectsOf(r).map((x) => x.kind))) {
      affected.set(f, (affected.get(f) || 0) + 1);
    }
  }
  const clean = perRecipe.filter((r) => !defectsOf(r).length).length;
  const total = perRecipe.reduce((n, r) => n + defectsOf(r).length, 0);
  const unbuiltSteps = perRecipe.reduce((n, r) => n + r.findings.filter((f) => f.severity === 'expected').length, 0);
  const unbuiltRecipes = perRecipe.filter((r) => r.findings.some((f) => f.severity === 'expected')).length;

  // A flag mismatch can only be seen where the script exists to compare against. Scoring
  // those findings out of all 97 recipes would report them as rare when they are near
  // universal among the recipes where they are measurable at all -- a denominator that
  // flatters the result. Each kind is scored against the population it could be found in.
  const flagKinds = new Set(['documented-not-built', 'built-not-documented']);
  const measurable = perRecipe.filter((r) => r.comparable > 0).length;

  console.log(`${bold('recipe/script contract check')}  ·  ${scanned} recipes  ·  ${total} defect(s)\n`);
  console.log(`  ${'FINDING'.padEnd(26)} ${'OF MEASURABLE'.padEnd(15)} READ AS`);
  for (const [kind, n] of [...affected.entries()].sort((a, b) => b[1] - a[1])) {
    const denom = flagKinds.has(kind) ? measurable : scanned;
    const share = denom ? Math.round((n / denom) * 100) : 0;
    const reading = share >= 80 ? 'one template-wide defect' : share >= 20 ? 'a widespread pattern' : 'individual recipes';
    console.log(`  ${kind.padEnd(26)} ${`${n}/${denom}`.padEnd(15)} ${String(share).padStart(3)}%  ${dim(reading)}`);
  }
  if (measurable < scanned) {
    console.log(dim(`\n  Flag findings are scored out of the ${measurable} recipe(s) with at least one script on disk —`));
    console.log(dim(`  the other ${scanned - measurable} have nothing to compare against, so counting them would understate the rate.`));
  }
  console.log(`\n  ${clean} recipe(s) with no defects.`);
  if (unbuiltSteps) {
    console.log(dim(`  ${unbuiltSteps} step(s) across ${unbuiltRecipes} recipe(s) are not built — NOT counted above.`));
    console.log(dim('  A DRAFT recipe whose scripts do not exist is correctly described, not broken.'));
    console.log(dim('  Scripts are required from SPECIFIED onward, because a DEV todo closes on "script exists".'));
  }
  console.log(dim('  A finding present in nearly every recipe is one defect in the template they share,\n'
    + '  not N defects. Fix it there and it closes everywhere.'));
  console.log(dim(`\n  Per recipe:  snickerdoodle check <recipe>`));
  process.exit(total ? 1 : 0);
}

// ---------------------------------------------------------------------------
// list / status / help
// ---------------------------------------------------------------------------

function cmdList(argv) {
  const files = fs.readdirSync(RECIPES_DIR).filter((f) => f.endsWith('.md') && f !== '_shared.md' && f !== 'README.md');
  const rows = [];
  for (const f of files) {
    const text = fs.readFileSync(path.join(RECIPES_DIR, f), 'utf8');
    const status = (text.match(/^status:\s*(\S+)/m) || [null, '—'])[1];
    const built = (text.match(/### Script Locations[\s\S]*?(?=\n## |\n### |$)/) || [''])[0]
      .split('\n').map((l) => backtick(l)).filter((p) => p && p.endsWith('.py') && fs.existsSync(p)).length;
    rows.push({ slug: f.replace(/\.md$/, ''), status, built });
  }
  if (argv.built) rows.sort((a, b) => b.built - a.built);
  const show = argv.built ? rows.filter((r) => r.built > 0) : rows;
  console.log(`${show.length} recipe(s)${argv.built ? ' with at least one built step' : ''}\n`);
  for (const r of show) {
    console.log(`  ${r.slug.padEnd(52)} ${String(r.status).padEnd(18)} ${r.built}/6 steps built`);
  }
}

function cmdHelp() {
  console.log(`${bold('snickerdoodle')} — run a recipe, record a gate decision

${bold('USAGE')}
  snickerdoodle run <recipe> [--step <name>] [--mode dialogic] [--sample] [--no-write]
  snickerdoodle gate <recipe> --gate N --decision approve|deny|defer --note "..." [--by "Name"]
  snickerdoodle check [<recipe>] [--all]
  snickerdoodle list [--built]

${bold('RUN')}
  With --step, runs that one step. Without it, runs every step the recipe declares,
  in order, and ${bold('stops on the first nonzero exit')} — a step that halts has already
  reported what it found, and continuing would proceed past a judgment.

  --sample      no live network calls, no external writes
  --no-write    compute, write nothing
  --fixture-set clean|defective (passed through to steps that accept it)

${bold('GATE')}
  Runs the gate's own test from the recipe, records what it saw, and writes
  ${GATE_DIR}/<recipe>-gate-N.json.

  It refuses to record an ${bold('approve')} when the gate's test fails, refuses a decision
  without --note, and refuses to overwrite an existing decision without --force.
  deny and defer are first-class: a gate decided "no" is closed; an unexamined one is not.

${bold('CHECK')}
  Compares what a recipe documents against what its scripts implement, without
  running anything: missing scripts, flags advertised but not built, flags built
  but not documented, gates with no testable condition.

  With no recipe (or --all) it scans every recipe and reports what share carries
  each finding — a defect in 90% of recipes is one defect in the template they
  share, not ninety.

${bold('NOTES')}
  The recipe is the configuration. Steps, scripts, gates and tests are read from the
  recipe markdown, so there is nothing to keep in sync with it.

  Completing the steps is not passing the gates. Running is an AI act; clearing a gate
  is a human one (P1).
`);
}

// ---------------------------------------------------------------------------
// argv
// ---------------------------------------------------------------------------

function parseArgv(args) {
  const out = { _: [] };
  for (let i = 0; i < args.length; i += 1) {
    const a = args[i];
    if (a.startsWith('--')) {
      const [k, inline] = a.slice(2).split('=');
      if (inline !== undefined) out[k] = inline;
      else if (args[i + 1] && !args[i + 1].startsWith('--')) { out[k] = args[i + 1]; i += 1; }
      else out[k] = true;
    } else out._.push(a);
  }
  return out;
}

function main() {
  const [verb, ...rest] = process.argv.slice(2);
  const argv = parseArgv(rest);
  if (!verb || verb === 'help' || argv.help) return cmdHelp();
  if (verb === 'run') return cmdRun(argv);
  if (verb === 'gate') return cmdGate(argv);
  if (verb === 'check') return cmdCheck(argv);
  if (verb === 'list') return cmdList(argv);
  die(`unknown command "${verb}"\n  commands: run, gate, list, help`);
}

main();
