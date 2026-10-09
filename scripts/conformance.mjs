#!/usr/bin/env node
// conformance.mjs
// The MACHINE half of MYCROFT P4 — "machines verify conformance; humans verify
// adequacy." Deterministically checks that every machine-readable file is
// well-formed: JSON parses, YAML parses (PyYAML), JS/MJS compiles (node --check),
// Python compiles (py_compile), shell parses (bash -n), Markdown is well-formed
// (balanced code fences + terminated front-matter).
//
// This is the conformance gate. It is NOT the adequacy gate — that is the human's
// job (the `review` skill / attestation). Both together are the provenance check.
//
// Usage:
//   node scripts/conformance.mjs                 # default surfaces
//   node scripts/conformance.mjs prompts brand   # specific paths
//   npm run verify

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

// Directory names skipped wherever they appear. These are genuinely non-source:
// binaries, build scratch, and dependencies.
//
// `ingest`, `gigo`, `tools` and `data` used to be here, labelled "generated/
// provenance code". That hid every recipe's step scripts from the default run --
// 476 Python files, the entire executable surface of 99 recipes -- so `npm run
// verify` was green while never reading a single line of pipeline code. Two
// market-sentiment PRs passed CI without CI compiling any of their Python.
// Removed 2026-10-09; see SKIP_PREFIXES for what still needs protecting.
const SKIP = new Set([
  '.git', 'node_modules', '.build', '__pycache__', 'output', 'images', 'd3',
  'MD', 'PSD', 'epub', 'front-back', 'wayback-machine', // heavy / non-source
]);

// Path prefixes skipped by location rather than by name, because the reason to
// skip them is WHERE they are, not what they are called. A bare basename rule
// cannot express this: it would skip every directory of that name in the repo.
const SKIP_PREFIXES = [
  'data/mycroft-main',    // quarantined Tier 3 vendored import -- provenance only
  'scripts/mycroft-main', // same import, code half
  'docs/mycroft-main',    // same import, docs half
  'data/private',         // private by default; never read, never committed
];

const KIND = {
  '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
  '.mjs': 'js', '.js': 'js', '.py': 'py', '.sh': 'sh', '.md': 'md',
};

const DEFAULT_PATHS = [
  'prompts', 'brand', 'recipes', 'scripts',
  // The two-layer data architecture. Gate 3 of every pipeline recipe asks whether
  // its raw and verified JSON parses; this is the machine half of that, run once
  // for the whole repo instead of recipe by recipe. Quarantined and private trees
  // under data/ are excluded by SKIP_PREFIXES, not by skipping `data` wholesale.
  'data/raw', 'data/verified',
  'DOMAIN.md', 'CLAUDE.md', 'AGENTS.md', 'SNICKERDOODLE.md', 'README.md',
  'metadata.yaml', 'package.json',
];

function skipped(p) {
  if (SKIP.has(path.basename(p))) return true;
  const rel = path.relative(process.cwd(), path.resolve(p)).split(path.sep).join('/');
  return SKIP_PREFIXES.some((q) => rel === q || rel.startsWith(`${q}/`));
}

function collect(p, acc) {
  let st;
  try { st = fs.statSync(p); } catch { return; }
  if (st.isDirectory()) {
    if (skipped(p)) return;
    for (const e of fs.readdirSync(p)) collect(path.join(p, e), acc);
  } else if (KIND[path.extname(p)]) {
    // A file named explicitly on the command line is still checked; only
    // directory traversal honours the skip rules.
    acc.push(p);
  }
}

function tail(e) {
  const s = (e.stderr ? e.stderr.toString() : e.message || '').trim();
  return s.split('\n').filter(Boolean).slice(-1)[0] || 'failed';
}

let PY_CMD = null;
function pythonCmd() {
  if (PY_CMD) return PY_CMD;
  for (const c of ['python3', 'python', 'py']) {
    try {
      execSync(`${c} --version`, { stdio: 'pipe' });
      PY_CMD = c;
      return PY_CMD;
    } catch { /* try next candidate */ }
  }
  PY_CMD = 'python3'; // none found; fail loudly with the conventional name
  return PY_CMD;
}

function checkMd(file) {
  const t = fs.readFileSync(file, 'utf8');
  const fences = (t.match(/^```/gm) || []).length;
  if (fences % 2 !== 0) throw new Error(`unbalanced code fences (${fences})`);
  if (t.startsWith('---\n') && !/^---\n[\s\S]*?\n---\s*\n/.test(t))
    throw new Error('unterminated front-matter');
}

function check(file, kind) {
  try {
    if (kind === 'json') JSON.parse(fs.readFileSync(file, 'utf8'));
    else if (kind === 'yaml') execSync(`${pythonCmd()} -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "${file}"`, { stdio: 'pipe' });
    else if (kind === 'js') execSync(`node --check "${file}"`, { stdio: 'pipe' });
    else if (kind === 'py') execSync(`${pythonCmd()} -m py_compile "${file}"`, { stdio: 'pipe' });
    else if (kind === 'sh') execSync(`bash -n "${file}"`, { stdio: 'pipe' });
    else if (kind === 'md') checkMd(file);
    return { ok: true };
  } catch (e) {
    return { ok: false, msg: tail(e) };
  }
}

// Spawning one interpreter per file costs ~130ms each. Unhiding the step scripts
// added 476 Python files, which turned a 6-second run into a 68-second one -- slow
// enough that people stop running it, which is how a check quietly stops working.
//
// So compile the whole batch in one process. On success (the common case) that is
// one spawn instead of hundreds. On failure, fall back to per-file checks to
// attribute the error, because a batch tells you something broke but a report has
// to say which file. Correctness is identical either way; only speed differs.
// cmd.exe caps a command line at 8191 characters -- not the 32767 of CreateProcess,
// which is the number usually quoted. Past roughly 150 paths the spawn fails with
// "The command line is too long", the batch falls back to per-file, and the speed-up
// silently evaporates while everything still passes. So chunk well under the cap.
const ARG_BUDGET = 6000;

function chunk(files) {
  const out = [];
  let cur = [];
  let len = 0;
  for (const f of files) {
    const cost = f.length + 3;
    if (len + cost > ARG_BUDGET && cur.length) { out.push(cur); cur = []; len = 0; }
    cur.push(f);
    len += cost;
  }
  if (cur.length) out.push(cur);
  return out;
}

function checkPyBatch(files) {
  const fails = [];
  for (const group of chunk(files)) {
    const args = group.map((f) => `"${f}"`).join(' ');
    try {
      execSync(`${pythonCmd()} -m py_compile ${args}`, { stdio: 'pipe' });
    } catch {
      // Something in this group failed. Re-check it file by file so the report can
      // name the offender -- a batch proves a failure exists but not where.
      for (const f of group) {
        const r = check(f, 'py');
        if (!r.ok) fails.push({ file: f, msg: r.msg });
      }
    }
  }
  return fails;
}

function checkYamlBatch(files) {
  if (files.length === 0) return [];
  const script = [
    'import sys, yaml',
    'for f in sys.argv[1:]:',
    '    try:',
    '        yaml.safe_load(open(f, encoding="utf-8"))',
    '    except Exception as e:',
    '        print(f + "\\t" + str(e).split(chr(10))[0])',
  ].join('\n');
  const runner = `${pythonCmd()} -c "${script.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"`;
  const fails = [];
  for (const group of chunk(files)) {
    const args = group.map((f) => `"${f}"`).join(' ');
    try {
      const out = execSync(`${runner} ${args}`, { stdio: 'pipe' }).toString();
      for (const l of out.split('\n')) {
        if (!l.includes('\t')) continue;
        const [file, ...rest] = l.split('\t');
        fails.push({ file, msg: rest.join('\t').trim() });
      }
    } catch {
      // The runner itself failed (no PyYAML, no interpreter). Fall back so the
      // reason is reported per file rather than swallowed.
      for (const f of group) {
        const r = check(f, 'yaml');
        if (!r.ok) fails.push({ file: f, msg: r.msg });
      }
    }
  }
  return fails;
}

function main() {
  const paths = process.argv.slice(2).length ? process.argv.slice(2) : DEFAULT_PATHS;
  const files = [];
  for (const p of paths) collect(p, files);

  const fails = [];
  const byKind = {};
  const batched = { py: [], yaml: [] };
  for (const f of files) {
    const kind = KIND[path.extname(f)];
    byKind[kind] = (byKind[kind] || 0) + 1;
    if (batched[kind]) { batched[kind].push(f); continue; }
    const r = check(f, kind);
    if (!r.ok) fails.push({ file: f, msg: r.msg });
  }
  fails.push(...checkPyBatch(batched.py));
  fails.push(...checkYamlBatch(batched.yaml));

  const counts = Object.entries(byKind).map(([k, n]) => `${n} ${k}`).join(' · ');
  console.log(`conformance: ${files.length} files (${counts})`);
  if (fails.length === 0) {
    console.log('✓ all conform (machine half of P4). Adequacy is still the human gate.');
    process.exit(0);
  }
  console.error(`\n✗ ${fails.length} file(s) FAILED conformance:`);
  for (const f of fails) console.error(`  • ${f.file} — ${f.msg}`);
  process.exit(1);
}

main();
