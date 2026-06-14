#!/usr/bin/env node
// build-instructions.mjs
// Compile the instruction SOURCE (instructions/_shared/*.md shared modules +
// instructions/<project>.md + instructions/manifest.yml) into the tool-native
// adapters AGENTS.md and CLAUDE.md — the same source-vs-adapter pattern as
// build-prompts.mjs, applied to the repo's instruction files.
//
//   AGENTS.md  — the cross-tool standard (Codex, Cursor, Gemini CLI, Copilot…):
//                shared modules + project, INLINED (AGENTS.md has no import syntax).
//   CLAUDE.md  — Claude Code reads this name: `@AGENTS.md` import + a claude_only
//                tail (Claude supports @import, so no duplication).
//
// Both carry a generated-file banner. NEVER hand-edit AGENTS.md / CLAUDE.md —
// edit instructions/ and rebuild. This is what kills the drift class (the two
// files can no longer diverge, because nobody writes them by hand).
//
// Usage:
//   node scripts/build-instructions.mjs            # build to .build/ + show the diff vs root
//   node scripts/build-instructions.mjs --promote  # build, then promote .build/ -> repo root
//
// The default (no --promote) is the VERIFIED gate: review the diff, then promote.

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

const SRC = 'instructions';
const SHARED = path.join(SRC, '_shared');
const BUILD = path.join(SRC, '.build');
const ROOT = '.';

const BANNER =
`<!-- GENERATED FILE — do not edit by hand.
     Source: instructions/ (_shared/ modules + project file) · manifest: instructions/manifest.yml
     Rebuild: node scripts/build-instructions.mjs   ·   Promote: --promote
     Hand edits are overwritten on the next build. -->\n\n`;

// --- manifest (YAML via PyYAML, like conformance.mjs) --------------------
function loadManifest() {
  const p = path.join(SRC, 'manifest.yml');
  if (!fs.existsSync(p)) { console.error(`No ${p}`); process.exit(2); }
  const json = execSync(
    `python3 -c "import yaml,json,sys;print(json.dumps(yaml.safe_load(open('${p}'))))"`,
    { encoding: 'utf8' });
  return JSON.parse(json);
}

function readModule(name) {
  // suite-local-first: a project may override a shared module by dropping a
  // same-named file in instructions/ (mirrors prompts/ _shared resolution)
  for (const base of [SRC, SHARED]) {
    const p = path.join(base, name);
    if (fs.existsSync(p)) return fs.readFileSync(p, 'utf8').trim();
  }
  throw new Error(`module not found (checked ${SRC}/ then ${SHARED}/): ${name}`);
}

function assembleBody(m) {
  const parts = (m.shared || []).map(readModule);
  if (m.project) parts.push(readModule(m.project));
  return parts.join('\n\n');
}

function buildAgents(body) {
  return BANNER + '# Agent Instructions\n\n' + body + '\n';
}
function buildClaude(m) {
  const tail = (m.claude_only || []).join('\n');
  return BANNER + '@AGENTS.md\n\n' + (tail ? tail + '\n' : '');
}

function diff(rootFile, buildFile) {
  if (!fs.existsSync(rootFile)) { console.log(`  (new) ${rootFile} — no current version`); return true; }
  try {
    execSync(`diff -u "${rootFile}" "${buildFile}"`, { stdio: 'pipe' });
    console.log(`  = ${rootFile} unchanged`); return false;
  } catch (e) {
    console.log(`--- diff: ${rootFile} ---`);
    console.log(e.stdout?.toString() || '(changed)');
    return true;
  }
}

function main() {
  const promote = process.argv.includes('--promote');
  const m = loadManifest();
  const body = assembleBody(m);

  fs.mkdirSync(BUILD, { recursive: true });
  const outputs = {};
  if ((m.targets || []).includes('agents')) outputs['AGENTS.md'] = buildAgents(body);
  if ((m.targets || []).includes('claude')) outputs['CLAUDE.md'] = buildClaude(m);

  for (const [name, content] of Object.entries(outputs))
    fs.writeFileSync(path.join(BUILD, name), content);
  console.log(`✓ staged ${Object.keys(outputs).join(' + ')} in ${BUILD}/\n`);

  if (!promote) {
    let changed = false;
    for (const name of Object.keys(outputs))
      changed = diff(path.join(ROOT, name), path.join(BUILD, name)) || changed;
    console.log(changed
      ? '\nReview the diff above, then promote:  node scripts/build-instructions.mjs --promote'
      : '\nNo changes vs the current root files.');
    return;
  }

  for (const name of Object.keys(outputs)) {
    fs.copyFileSync(path.join(BUILD, name), path.join(ROOT, name));
    console.log(`  promoted ${name} → repo root`);
  }
  console.log('✓ AGENTS.md and CLAUDE.md regenerated from source. Do not hand-edit them.');
}

main();
