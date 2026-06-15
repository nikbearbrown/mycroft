#!/usr/bin/env node
// manifest-check.mjs — the ENFORCEABLE half of the portable context layer.
// conformance.mjs proves every file is well-formed; this proves the manifest
// still tells the truth about the repo.
//
// Checks (ERROR = exit 1, fails the gate · WARN = exit 0, surfaced for a human):
//   E1  .ai/manifest.yaml and _MANIFEST.md exist and parse.
//   E2  Every canonical file in .ai/manifest.yaml actually exists.
//   E3  Every generated adapter matches what build-instructions.mjs would emit
//       (catches hand-edits and "forgot to rebuild" drift).
//   W1  Every ignore: entry that is a real path is covered by .gitignore.
//   W2  Every private: path is covered by .gitignore (root or nested ignore-all).
//   W3  _MANIFEST.md Tier-1 set and .ai/manifest.yaml canonical: set agree.
//
//   node scripts/manifest-check.mjs           # report; exit 1 on any ERROR
//   node scripts/manifest-check.mjs --strict  # treat WARN as ERROR too

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

const strict = process.argv.includes('--strict');
const errors = [];
const warns = [];
const E = (m) => errors.push(m);
const W = (m) => warns.push(m);

const AI = '.ai/manifest.yaml';
const MAN = '_MANIFEST.md';

const loadYaml = (p) => JSON.parse(execSync(
  `python3 -c "import yaml,json;print(json.dumps(yaml.safe_load(open('${p}')),default=str))"`,
  { encoding: 'utf8' }));

console.log('MANIFEST CHECK — Mycroft');
console.log('='.repeat(42));

let m = null;
if (!fs.existsSync(AI)) E(`E1 missing ${AI}`);
if (!fs.existsSync(MAN)) E(`E1 missing ${MAN}`);
if (fs.existsSync(AI)) {
  try { m = loadYaml(AI); } catch (e) { E(`E1 ${AI} does not parse: ${String(e).split('\n')[0]}`); }
}

if (m) {
  for (const f of m.canonical || []) if (!fs.existsSync(f)) E(`E2 canonical file missing: ${f}`);

  try { execSync('node scripts/build-instructions.mjs', { stdio: 'ignore' }); }
  catch (e) { E(`E3 build-instructions.mjs failed to stage: ${String(e).split('\n')[0]}`); }
  for (const f of m.generated_instructions || []) {
    const staged = path.join('instructions', '.build', f);
    if (!fs.existsSync(staged)) { E(`E3 ${f} not produced by build (is it in manifest.yml targets?)`); continue; }
    if (!fs.existsSync(f)) { E(`E3 generated file missing on disk: ${f} — run build --promote`); continue; }
    if (fs.readFileSync(f, 'utf8') !== fs.readFileSync(staged, 'utf8'))
      E(`E3 ${f} is out of sync with instructions/ — hand-edited or not rebuilt (run: node scripts/build-instructions.mjs --promote)`);
  }

  const gi = fs.existsSync('.gitignore') ? fs.readFileSync('.gitignore', 'utf8') : '';
  const giHas = (entry) => {
    const base = entry.replace(/^[./]+/, '').replace(/\/$/, '');
    return gi.split('\n').some((l) => {
      const t = l.trim().replace(/^[./]+/, '').replace(/\/$/, '');
      return t && (t === base || base.startsWith(t + '/') || base.endsWith(t));
    });
  };
  for (const ig of m.ignore || []) {
    if (ig.includes('*')) continue;
    if (fs.existsSync(ig) && !giHas(ig)) W(`W1 ignore path not in .gitignore: ${ig}`);
  }

  const privateCovered = (pv) => {
    if (giHas(pv)) return true;
    const nested = path.join(pv.replace(/\/$/, ''), '.gitignore');
    if (fs.existsSync(nested)) return fs.readFileSync(nested, 'utf8').split('\n').some((l) => l.trim() === '*');
    return false;
  };
  for (const pv of m.private || []) {
    if (pv.includes('*')) { if (pv.startsWith('.env') && !gi.includes('.env')) W(`W2 private pattern not gitignored: ${pv}`); continue; }
    if (!privateCovered(pv)) W(`W2 private path not gitignored (PII/secret risk): ${pv}`);
  }

  if (fs.existsSync(MAN)) {
    const md = fs.readFileSync(MAN, 'utf8');
    const t1 = md.slice(md.indexOf('Tier 1'), md.indexOf('Tier 2') >= 0 ? md.indexOf('Tier 2') : undefined);
    const inMd = new Set([...t1.matchAll(/\|\s*`([^`]+)`/g)].map((x) => x[1]));
    const inYaml = new Set(m.canonical || []);
    for (const f of inYaml) if (!inMd.has(f)) W(`W3 in .ai canonical but not _MANIFEST.md Tier 1: ${f}`);
    for (const f of inMd) if (!inYaml.has(f)) W(`W3 in _MANIFEST.md Tier 1 but not .ai canonical: ${f}`);
  }
}

if (warns.length) { console.log(`\nWARN (${warns.length}):`); for (const w of warns) console.log('  ' + w); }
if (errors.length) { console.log(`\nERROR (${errors.length}):`); for (const e of errors) console.log('  ' + e); }

const fail = errors.length > 0 || (strict && warns.length > 0);
console.log('\n' + (fail
  ? `✗ manifest check FAILED (${errors.length} error${errors.length === 1 ? '' : 's'}${strict ? `, ${warns.length} warn` : ''})`
  : `✓ manifest check passed${warns.length ? ` (${warns.length} warning${warns.length === 1 ? '' : 's'})` : ''}`));
process.exit(fail ? 1 : 0);
