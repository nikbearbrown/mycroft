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

const SKIP = new Set([
  '.git', 'node_modules', '.build', 'output', 'images', 'd3', 'data', 'MD',
  'PSD', 'epub', 'front-back', 'wayback-machine', // heavy / non-source
  'mycroft-main', 'ingest', 'gigo', 'tools',       // generated/provenance code
]);

const KIND = {
  '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
  '.mjs': 'js', '.js': 'js', '.py': 'py', '.sh': 'sh', '.md': 'md',
};

const DEFAULT_PATHS = [
  'prompts', 'brand', 'recipes', 'scripts',
  'DOMAIN.md', 'CLAUDE.md', 'AGENTS.md', 'SNICKERDOODLE.md', 'README.md',
  'metadata.yaml', 'package.json',
];

function collect(p, acc) {
  let st;
  try { st = fs.statSync(p); } catch { return; }
  if (st.isDirectory()) {
    if (SKIP.has(path.basename(p))) return;
    for (const e of fs.readdirSync(p)) collect(path.join(p, e), acc);
  } else if (KIND[path.extname(p)]) {
    acc.push(p);
  }
}

function tail(e) {
  const s = (e.stderr ? e.stderr.toString() : e.message || '').trim();
  return s.split('\n').filter(Boolean).slice(-1)[0] || 'failed';
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
    else if (kind === 'yaml') execSync(`python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "${file}"`, { stdio: 'pipe' });
    else if (kind === 'js') execSync(`node --check "${file}"`, { stdio: 'pipe' });
    else if (kind === 'py') execSync(`python3 -m py_compile "${file}"`, { stdio: 'pipe' });
    else if (kind === 'sh') execSync(`bash -n "${file}"`, { stdio: 'pipe' });
    else if (kind === 'md') checkMd(file);
    return { ok: true };
  } catch (e) {
    return { ok: false, msg: tail(e) };
  }
}

function main() {
  const paths = process.argv.slice(2).length ? process.argv.slice(2) : DEFAULT_PATHS;
  const files = [];
  for (const p of paths) collect(p, files);

  const fails = [];
  const byKind = {};
  for (const f of files) {
    const kind = KIND[path.extname(f)];
    byKind[kind] = (byKind[kind] || 0) + 1;
    const r = check(f, kind);
    if (!r.ok) fails.push({ file: f, msg: r.msg });
  }

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
