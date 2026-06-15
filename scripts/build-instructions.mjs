#!/usr/bin/env node
// build-instructions.mjs
// Compile the instruction SOURCE (instructions/_shared/*.md shared modules +
// instructions/<project>.md + instructions/manifest.yml) into the tool-native
// adapters — the same source-vs-adapter pattern, applied to the repo's
// instruction files.
//
//   AGENTS.md  — the cross-tool standard (Codex, Cursor, Gemini CLI, Copilot…):
//                shared modules + project, INLINED. The CANONICAL adapter.
//   CLAUDE.md  — Claude Code reads this name: `@AGENTS.md` import + a claude_only tail.
//
// Thin shims (generated, never hand-edited — they cannot drift; each points at
// the canonical AGENTS.md / SNICKERDOODLE.md instead of duplicating rule content):
//   .gemini/settings.json               — Gemini CLI context.fileName → AGENTS.md
//   .aider.conf.yml                     — Aider read: AGENTS.md
//   .github/copilot-instructions.md     — Copilot pointer to AGENTS.md
//   .cursor/rules/mycroft.mdc           — Cursor alwaysApply rule → AGENTS.md
//
// Which shims are emitted is controlled by `targets:` in instructions/manifest.yml.
// NEVER hand-edit any generated file — edit instructions/ and rebuild.
//
//   node scripts/build-instructions.mjs            # build to .build/ + show the diff vs root
//   node scripts/build-instructions.mjs --promote  # build, then promote .build/ -> repo root

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

const SRC = 'instructions';
const SHARED = path.join(SRC, '_shared');
const BUILD = path.join(SRC, '.build');
const ROOT = '.';

// Per-repo identity (Mycroft is the framework; constitution renamed to avoid
// confusion with the Mycroft project at mycroft.biz).
const CONSTITUTION = 'SNICKERDOODLE.md';
const TITLE = 'Mycroft';
const CURSOR_RULE = '.cursor/rules/mycroft.mdc';

const MD_BANNER =
`<!-- GENERATED FILE — do not edit by hand.
     Source: instructions/ (_shared/ modules + project file) · manifest: instructions/manifest.yml
     Rebuild: node scripts/build-instructions.mjs   ·   Promote: --promote
     Hand edits are overwritten on the next build. -->\n\n`;

const YAML_BANNER =
`# GENERATED FILE — do not edit by hand.
# Source: instructions/ · manifest: instructions/manifest.yml
# Rebuild: node scripts/build-instructions.mjs --promote\n`;

const GEN_NOTE =
`GENERATED from instructions/ by scripts/build-instructions.mjs — do not edit by hand. ` +
`Thin shim: points at the canonical AGENTS.md (${CONSTITUTION} governs).`;

function loadManifest() {
  const p = path.join(SRC, 'manifest.yml');
  if (!fs.existsSync(p)) { console.error(`No ${p}`); process.exit(2); }
  const json = execSync(
    `python3 -c "import yaml,json,sys;print(json.dumps(yaml.safe_load(open('${p}'))))"`,
    { encoding: 'utf8' });
  return JSON.parse(json);
}

function readModule(name) {
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

// --- builders ------------------------------------------------------------
function buildAgents(body) {
  return MD_BANNER + '# Agent Instructions\n\n' + body + '\n';
}
function buildClaude(m) {
  const tail = (m.claude_only || []).join('\n');
  return MD_BANNER + '@AGENTS.md\n\n' + (tail ? tail + '\n' : '');
}
function buildGemini() {
  return JSON.stringify({
    _comment: GEN_NOTE,
    context: { fileName: ['AGENTS.md', CONSTITUTION] },
  }, null, 2) + '\n';
}
function buildAider() {
  return YAML_BANNER + `read:\n  - AGENTS.md\n  - ${CONSTITUTION}\n`;
}
function buildCopilot() {
  return MD_BANNER +
`# Copilot Instructions — ${TITLE}

Read **\`AGENTS.md\`** (generated cross-agent instructions) and **\`${CONSTITUTION}\`**
(the constitution — it governs) before acting. The portable read-first map is
**\`_MANIFEST.md\`**.

If anything conflicts with \`${CONSTITUTION}\`, it wins, and the conflict is a bug —
log it in \`logs/RUN_LOG.md\`.
`;
}
function buildCursor() {
  return `---
description: ${TITLE} — read the canonical agent instructions
alwaysApply: true
---
` + MD_BANNER +
`Read \`AGENTS.md\` (generated cross-agent instructions) and \`${CONSTITUTION}\`
(the constitution; it governs) before acting. Portable read-first map: \`_MANIFEST.md\`.
Conflicts → \`${CONSTITUTION}\` wins; log them in \`logs/RUN_LOG.md\`.
`;
}

const TARGETS = {
  agents:  { file: 'AGENTS.md',                          build: (m, body) => buildAgents(body) },
  claude:  { file: 'CLAUDE.md',                          build: (m)       => buildClaude(m) },
  gemini:  { file: '.gemini/settings.json',             build: ()        => buildGemini() },
  aider:   { file: '.aider.conf.yml',                   build: ()        => buildAider() },
  copilot: { file: '.github/copilot-instructions.md',   build: ()        => buildCopilot() },
  cursor:  { file: CURSOR_RULE,                          build: ()        => buildCursor() },
};

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

function writeNested(base, name, content) {
  const out = path.join(base, name);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, content);
}

function main() {
  const promote = process.argv.includes('--promote');
  const m = loadManifest();
  const body = assembleBody(m);

  fs.mkdirSync(BUILD, { recursive: true });
  const outputs = {};
  for (const t of (m.targets || [])) {
    const spec = TARGETS[t];
    if (!spec) { console.error(`  ! unknown target in manifest.yml: ${t} (skipped)`); continue; }
    outputs[spec.file] = spec.build(m, body);
  }

  for (const [name, content] of Object.entries(outputs))
    writeNested(BUILD, name, content);
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
    const dest = path.join(ROOT, name);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(path.join(BUILD, name), dest);
    console.log(`  promoted ${name}`);
  }
  console.log('✓ Adapters regenerated from source. Do not hand-edit them.');
}

main();
