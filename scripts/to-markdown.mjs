#!/usr/bin/env node
// to-markdown.mjs
// Render any AI-native record (JSON or YAML) as a human-readable Markdown
// "review sheet": a "Needs your input" checklist (nulls, [CONFLICT],
// [Unverifiable], and any _human_gate fields) followed by the full content in
// plain prose/tables.
//
// AI-native formats are the source of truth for the machine; humans default to
// this Markdown view. The `review` skill's `apply` step writes feedback back into
// the original file. This is a VIEW — it never edits the source.
//
// Usage: node scripts/to-markdown.mjs <file.json|.yaml|.yml>
// (YAML is parsed via python3 + PyYAML; comments are dropped in the view.)

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

// Load JSON directly; convert YAML to JSON via PyYAML (no node yaml dependency).
function load(file) {
  if (/\.ya?ml$/i.test(file)) {
    const j = execSync(
      `python3 -c "import json,sys,yaml; json.dump(yaml.safe_load(open(sys.argv[1])), sys.stdout)" "${file}"`,
      { encoding: 'utf8' }
    );
    return JSON.parse(j);
  }
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

const NEEDS = /^\s*\[(unverifiable|conflict)/i; // strings that signal an open gate

const isGap = (v) => v === null || (typeof v === 'string' && NEEDS.test(v));

// Resolve a _human_gate path (supports a.b, results[].risk) to {path,value} leaves.
function leaves(obj, parts, prefix = '') {
  if (parts.length === 0) return [{ path: prefix.replace(/^\./, ''), value: obj }];
  const [head, ...rest] = parts;
  if (head.endsWith('[]')) {
    const key = head.slice(0, -2);
    const arr = obj?.[key];
    if (!Array.isArray(arr)) return [];
    return arr.flatMap((it, i) => leaves(it, rest, `${prefix}.${key}[${i}]`));
  }
  return obj == null ? [] : leaves(obj[head], rest, `${prefix}.${head}`);
}

// Walk the tree collecting every gap (null / [Unverifiable] / [CONFLICT]).
function collectGaps(node, prefix, out) {
  if (Array.isArray(node)) {
    node.forEach((v, i) => collectGaps(v, `${prefix}[${i}]`, out));
  } else if (node && typeof node === 'object') {
    for (const [k, v] of Object.entries(node)) {
      if (k.startsWith('_')) continue;
      const p = prefix ? `${prefix}.${k}` : k;
      if (isGap(v)) out.push({ path: p, value: v });
      else collectGaps(v, p, out);
    }
  }
}

const esc = (s) => String(s).replace(/\|/g, '\\|');

// Render a value as readable markdown.
function render(node, depth) {
  const pad = '  '.repeat(depth);
  if (node === null) return '_(empty — needs you)_ ⚠';
  if (Array.isArray(node)) {
    if (node.length === 0) return '_(none)_';
    return '\n' + node.map((v) => {
      if (v && typeof v === 'object') {
        // render each object's fields as a bulleted block (no leading "- -")
        return Object.entries(v)
          .filter(([k]) => !k.startsWith('_'))
          .map(([k, val]) => `${pad}- **${k}:** ${render(val, depth + 1).trim()}`)
          .join('\n');
      }
      return `${pad}- ${scalar(v)}`;
    }).join('\n\n');
  }
  if (node && typeof node === 'object') {
    return '\n' + Object.entries(node)
      .filter(([k]) => !k.startsWith('_'))
      .map(([k, v]) => `${pad}- **${k}:** ${render(v, depth + 1).trim()}`)
      .join('\n');
  }
  return scalar(node);
}
const scalar = (v) => (isGap(v) ? `${v == null ? '_(empty)_' : esc(v)} ⚠` : esc(v));

function main() {
  const file = process.argv[2];
  if (!file) { console.error('usage: node scripts/to-markdown.mjs <file.json|.yaml|.yml>'); process.exit(2); }
  const data = load(file);

  // gaps: tree scan + any declared _human_gate paths (collected at every object level)
  const gaps = [];
  collectGaps(data, '', gaps);
  (function scanGates(node, prefix) {
    if (Array.isArray(node)) return node.forEach((v, i) => scanGates(v, `${prefix}[${i}]`));
    if (node && typeof node === 'object') {
      for (const g of node._human_gate || []) {
        for (const { path: p, value } of leaves(node, g.split('.'), prefix)) {
          if (isGap(value) && !gaps.some((x) => x.path === p)) gaps.push({ path: p, value });
        }
      }
      for (const [k, v] of Object.entries(node)) if (!k.startsWith('_')) scanGates(v, prefix ? `${prefix}.${k}` : k);
    }
  })(data, '');

  const out = [];
  out.push(`# Review: ${path.basename(file)}`);
  out.push(`\n_Readable view of \`${file}\`. Reply with plain-language feedback (or mark the ⚠ items), then run \`apply\`. The original file stays the source of truth — this is just the human-readable face of it._`);

  out.push(`\n## ⚠ Needs your input (${gaps.length})`);
  if (gaps.length === 0) out.push('\n_All gated fields are filled. You can mark this artifact attested._');
  else out.push('\n' + gaps.map((g) => `- [ ] \`${g.path}\` — ${g.value == null ? 'empty' : esc(g.value)}`).join('\n'));

  if (data._label_key) {
    out.push('\n## Legend');
    out.push('\n' + Object.entries(data._label_key).map(([k, v]) => `- \`${k}\` — ${v}`).join('\n'));
  }

  out.push('\n## Content');
  for (const [k, v] of Object.entries(data)) {
    if (k.startsWith('_')) continue;
    out.push(`\n### ${k}`);
    out.push(render(v, 0));
  }
  console.log(out.join('\n'));
}

main();
