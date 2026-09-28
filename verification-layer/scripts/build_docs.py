"""
Build the reference documentation site (docs/reference/) from its Markdown sources.

    python scripts/build_docs.py            # build into docs/reference/
    python scripts/build_docs.py --check    # build in memory, report problems, write nothing

The written parts live in docs/reference/src/ (see its AUTHORING.md). Everything that can be
read off the code is generated here on every build, so it can't drift from it:

    - the inventory under each file entry: functions, classes, constants, exports, the
      internal files it imports and the files that import it, test counts, line counts;
    - the HTTP route table (from web/server.py's route decorators);
    - the environment-variable table (from os.environ / os.getenv reads);
    - the layer dependency matrix (from every Python import);
    - the Honest Ledger page (from web/self_report.py's KNOWN_ISSUES);
    - the search index.

Source code is parsed (ast for Python, regular expressions for TypeScript), never imported,
so a module with a missing dependency or a syntax error can't stop the docs building.

Stdlib only. The site is plain HTML with one stylesheet and two small scripts, so it opens
straight from disk (file://) with no server and no build tools. Pages are light by default;
the header's theme toggle switches to dark and remembers the choice. A one-line script in each
page's <head> applies a saved dark choice before the first paint, so the page doesn't flash.

tests/test_docs_coverage.py runs build() and fails on any problem it reports: a project file
with no entry, an entry for a file that doesn't exist, a file matched by two entries, a
[[link]] or page link that doesn't resolve.
"""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import fnmatch
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # verification-layer/
SRC = ROOT / "docs" / "reference" / "src"
OUT = ROOT / "docs" / "reference"

SECTIONS = ("Start", "Architecture", "Features", "Reference", "Files", "History")
SITE_TITLE = "Verification layer reference"

# Python packages, in the dependency order tests/test_layering.py enforces.
LAYERS = ("core", "adapters", "pipeline", "datasources", "producers", "validation", "web", "scripts", "tests")


# ─── Project files ────────────────────────────────────────────────────────────────


def project_files() -> list[str]:
    """Every file that belongs to the project: tracked by git, or new and not ignored.

    A tracked file deleted in the working copy is still listed (it is still in the
    repository), and its entry says so."""
    def git(*args: str) -> list[str]:
        out = subprocess.run(["git", *args, "-z", "--", "."], cwd=ROOT, capture_output=True, check=True)
        return [p for p in out.stdout.decode("utf-8").split("\0") if p]

    files = set(git("ls-files")) | set(git("ls-files", "--others", "--exclude-standard"))
    return sorted(files)


def is_deleted(rel: str) -> bool:
    return not (ROOT / rel).exists()


# ─── Globs ────────────────────────────────────────────────────────────────────────


def glob_match(pattern: str, path: str) -> bool:
    """`*` matches within one folder, `**` across folders."""
    if pattern == path:
        return True
    rx = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**", i):
            rx += ".*"
            i += 2
        elif pattern[i] == "*":
            rx += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            rx += "[^/]"
            i += 1
        else:
            rx += re.escape(pattern[i])
            i += 1
    return re.fullmatch(rx, path) is not None


def is_glob(pattern: str) -> bool:
    return any(c in pattern for c in "*?")


# ─── Markdown (the subset AUTHORING.md documents) ─────────────────────────────────


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "section"


def file_anchor(path: str) -> str:
    return "f-" + slugify(path)


@dataclass
class Ctx:
    """What inline rendering needs to resolve links, and where it records problems."""
    page: str
    resolve_file: "callable"
    problems: list[str]


_INLINE_CODE = re.compile(r"`([^`]+)`")
_WIKI = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")


def inline(text: str, ctx: Ctx) -> str:
    """Render inline Markdown. Code spans are protected first so nothing inside them is
    treated as markup."""
    stash: list[str] = []

    def keep(fragment: str) -> str:
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    def wiki(m: re.Match) -> str:
        target, label = m.group(1).strip(), m.group(2)
        href = ctx.resolve_file(target)
        if href is None:
            ctx.problems.append(f"{ctx.page}: [[{target}]] matches no file entry")
            return keep(f"<code>{html.escape(target)}</code>")
        text_ = html.escape(label) if label else f"<code>{html.escape(target)}</code>"
        return keep(f'<a href="{href}">{text_}</a>')

    text = _INLINE_CODE.sub(lambda m: keep(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = _WIKI.sub(wiki, text)  # after code spans, so a `[[link]]` example stays literal
    text = _LINK.sub(lambda m: keep(f'<a href="{html.escape(m.group(2), quote=True)}">'
                                     f"{inline_plain(m.group(1), ctx)}</a>"), text)
    # Raw inline HTML tags pass through; everything else is escaped.
    parts = re.split(r"(<\/?[a-zA-Z][^<>]*>)", text)
    text = "".join(p if re.fullmatch(r"<\/?[a-zA-Z][^<>]*>", p) else html.escape(p, quote=False) for p in parts)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)


def inline_plain(text: str, ctx: Ctx) -> str:
    """Link text: inline code and emphasis only (no nested links)."""
    text = html.escape(text, quote=False)
    text = _INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    return _ITALIC.sub(r"<em>\1</em>", text)


def _table(lines: list[str], ctx: Ctx) -> str:
    def cells(line: str) -> list[str]:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|") and not line.endswith("\\|"):
            line = line[:-1]
        # Split on pipes that aren't escaped and aren't inside a code span.
        out, cur, in_code = [], "", False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
                cur += "|"
                i += 2
                continue
            if ch == "`":
                in_code = not in_code
            if ch == "|" and not in_code:
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
            i += 1
        out.append(cur.strip())
        return out

    head = cells(lines[0])
    body = [cells(l) for l in lines[2:]]
    h = "".join(f"<th>{inline(c, ctx)}</th>" for c in head)
    rows = "".join("<tr>" + "".join(f"<td>{inline(c, ctx)}</td>" for c in r) + "</tr>" for r in body)
    return f'<div class="table-wrap"><table><thead><tr>{h}</tr></thead><tbody>{rows}</tbody></table></div>'


_LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def _list(lines: list[str], ctx: Ctx) -> str:
    """Nested lists by indentation (two spaces per level). Continuation lines (indented,
    not a new item) join the previous item."""
    items: list[tuple[int, bool, str]] = []  # (indent, ordered, text)
    for line in lines:
        m = _LIST_ITEM.match(line)
        if m:
            items.append((len(m.group(1)), m.group(2)[0].isdigit(), m.group(3)))
        elif items:
            ind, ordered, text = items[-1]
            items[-1] = (ind, ordered, text + " " + line.strip())

    out: list[str] = []
    stack: list[tuple[int, str]] = []  # (indent, tag)
    for ind, ordered, text in items:
        tag = "ol" if ordered else "ul"
        while stack and ind < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
        if not stack or ind > stack[-1][0]:
            out.append(f"<{tag}><li>")
            stack.append((ind, tag))
        else:
            out.append("</li><li>")
        out.append(inline(text, ctx))
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


@dataclass
class Heading:
    level: int
    text: str
    anchor: str


def render_markdown(md: str, ctx: Ctx, headings: list[Heading], hook=None) -> str:
    """Render a Markdown document. `hook(level, raw_heading_text)` may return extra HTML to
    append after that heading's section (used to insert generated inventories)."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    used: set[str] = {h.anchor for h in headings}
    pending: list[str] = []  # generated HTML waiting for the end of the current entry
    pending_level = 0
    i = 0

    def flush_pending(level: int) -> None:
        nonlocal pending, pending_level
        if pending and level <= pending_level:
            out.extend(pending)
            pending = []

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>")
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level, raw = len(m.group(1)), m.group(2).strip()
            flush_pending(level)
            fm = re.fullmatch(r"`([^`]+)`", raw)
            dm = re.match(r"(D-\d+)(?!\d)", raw)  # a decision record: a short, stable anchor (#d-07)
            anchor = file_anchor(fm.group(1)) if (level == 2 and fm) else (dm.group(1).lower() if dm else slugify(raw))
            base, n = anchor, 2
            while anchor in used:
                anchor = f"{base}-{n}"
                n += 1
            used.add(anchor)
            headings.append(Heading(level, raw, anchor))
            cls = ' class="file-entry"' if (level == 2 and fm) else ""
            out.append(f'<h{level} id="{anchor}"{cls}>{inline(raw, ctx)}'
                       f'<a class="anchor" href="#{anchor}" aria-label="Link to this section">#</a></h{level}>')
            if hook:
                extra = hook(level, raw)
                if extra:
                    pending, pending_level = [extra], level
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(_table(block, ctx))
            continue
        if _LIST_ITEM.match(line):
            block = []
            while i < len(lines) and lines[i].strip() and (_LIST_ITEM.match(lines[i]) or lines[i].startswith(" ")):
                block.append(lines[i])
                i += 1
            out.append(_list(block, ctx))
            continue
        if line.startswith(">"):
            block = []
            while i < len(lines) and lines[i].startswith(">"):
                block.append(lines[i][1:].strip())
                i += 1
            inner = render_markdown("\n".join(block), ctx, headings)
            out.append(f'<aside class="callout">{inner}</aside>')
            continue
        if re.match(r"^\s*<(div|table|figure|svg|details|section|aside|p)\b", line):
            block = []
            while i < len(lines) and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue
        if re.fullmatch(r"\{\{[a-z-]+\}\}", line.strip()):
            out.append(line.strip())  # a generated block, filled in later
            i += 1
            continue
        block = []
        while (i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", ">"))
               and not _LIST_ITEM.match(lines[i]) and not lines[i].lstrip().startswith("|")):
            block.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(block), ctx)}</p>")
    flush_pending(0)
    return "\n".join(out)


# ─── Sources ──────────────────────────────────────────────────────────────────────


@dataclass
class Page:
    slug: str
    title: str
    section: str
    order: int
    summary: str
    body: str
    source: Path
    entries: list[str] = field(default_factory=list)  # file patterns documented here
    headings: list[Heading] = field(default_factory=list)
    html: str = ""


def parse_front_matter(text: str, source: Path) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.DOTALL)
    if not m:
        raise ValueError(f"{source}: missing front matter")
    meta = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text.replace("\r\n", "\n")[m.end():]


def load_pages(problems: list[str]) -> list[Page]:
    pages: list[Page] = []
    for source in sorted(list((SRC / "pages").glob("*.md")) + list((SRC / "files").glob("*.md"))):
        meta, body = parse_front_matter(source.read_text(encoding="utf-8"), source)
        for key in ("title", "slug", "section", "order"):
            if key not in meta:
                problems.append(f"{source.name}: front matter has no {key}")
        section = meta.get("section", "Reference")
        if section not in SECTIONS:
            problems.append(f"{source.name}: unknown section {section!r}")
        page = Page(slug=meta.get("slug", source.stem), title=meta.get("title", source.stem), section=section,
                    order=int(meta.get("order", 999)), summary=meta.get("summary", ""), body=body, source=source)
        # Headings inside fenced code blocks are examples, not entries.
        in_code = False
        for line in body.split("\n"):
            if line.startswith("```"):
                in_code = not in_code
            m = None if in_code else re.match(r"^##\s+`([^`]+)`\s*$", line)
            if m:
                page.entries.append(m.group(1))
        pages.append(page)
    slugs = [p.slug for p in pages]
    for s in {s for s in slugs if slugs.count(s) > 1}:
        problems.append(f"slug {s!r} is used by more than one page")
    return sorted(pages, key=lambda p: (SECTIONS.index(p.section) if p.section in SECTIONS else 99, p.order, p.title))


# ─── Code inventory ───────────────────────────────────────────────────────────────


@dataclass
class Inventory:
    path: str
    lines: int = 0
    bytes: int = 0
    kind: str = ""
    classes: list[tuple[str, str, list[str]]] = field(default_factory=list)  # name, bases, public methods
    functions: list[tuple[str, str, str]] = field(default_factory=list)      # name, signature, first doc line
    constants: list[tuple[str, str]] = field(default_factory=list)           # name, short value
    exports: list[tuple[str, str]] = field(default_factory=list)             # kind, name (TypeScript)
    imports: set[str] = field(default_factory=set)                           # internal files it imports
    lazy_imports: set[str] = field(default_factory=set)                      # imported inside a function
    externals: set[str] = field(default_factory=set)                         # third-party top-level modules
    tests: int | None = None
    routes: list[tuple[str, str, str, str]] = field(default_factory=list)    # method, path, function, doc
    env: list[tuple[str, str]] = field(default_factory=list)                 # variable, default
    error: str = ""


_STDLIB = set(getattr(sys, "stdlib_module_names", ()))


def _py_module_file(module: str, files: set[str]) -> str | None:
    parts = module.split(".")
    for n in range(len(parts), 0, -1):
        base = "/".join(parts[:n])
        for cand in (base + ".py", base + "/__init__.py"):
            if cand in files:
                return cand
    return None


def _short(node: ast.AST) -> str:
    try:
        text = ast.unparse(node)
    except Exception:
        return ""
    return text if len(text) <= 60 else text[:57] + "..."


def _first_line(doc: str | None) -> str:
    if not doc:
        return ""
    para = doc.strip().split("\n\n")[0]
    return " ".join(para.split())


def inventory_python(inv: Inventory, text: str, files: set[str]) -> None:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        inv.error = f"does not parse: {exc}"
        return
    inv.kind = "Python module"
    module_level = {id(n) for n in tree.body}
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
        for name in names:
            top = name.split(".")[0]
            target = _py_module_file(name, files) if top in LAYERS else None
            if target and target != inv.path:
                (inv.imports if id(node) in module_level else inv.lazy_imports).add(target)
            elif top not in LAYERS and top not in _STDLIB and top != "__future__":
                inv.externals.add(top)
    inv.lazy_imports -= inv.imports
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and (not n.name.startswith("_") or n.name == "__call__")]
            inv.classes.append((node.name, ", ".join(_short(b) for b in node.bases), methods))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            route = None
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                        and dec.func.attr in ("get", "post", "put", "delete", "patch")
                        and isinstance(dec.func.value, ast.Name) and dec.func.value.id in ("app", "router")
                        and dec.args and isinstance(dec.args[0], ast.Constant)):
                    route = (dec.func.attr.upper(), dec.args[0].value)
                    inv.routes.append((*route, node.name, _first_line(ast.get_docstring(node))))
            if route is None:
                args = ast.unparse(node.args)
                prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
                inv.functions.append((node.name, f"{prefix}{node.name}({args})", _first_line(ast.get_docstring(node))))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and re.fullmatch(r"_?[A-Z][A-Z0-9_]+", t.id) and node.value is not None:
                    inv.constants.append((t.id, _short(node.value)))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = None
            if isinstance(f, ast.Attribute) and f.attr in ("get", "getenv") and node.args:
                owner = ast.unparse(f.value)
                if owner in ("os.environ", "os", "environ"):
                    name = node.args[0]
            if name is not None and isinstance(name, ast.Constant) and isinstance(name.value, str):
                default = _short(node.args[1]) if len(node.args) > 1 else ""
                inv.env.append((name.value, default))
        elif isinstance(node, ast.Subscript) and ast.unparse(node.value) == "os.environ":
            if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                inv.env.append((node.slice.value, "(required)"))
    if re.search(r"(^|/)test_[^/]+\.py$", inv.path):
        inv.tests = sum(1 for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"))


_TS_EXPORT = re.compile(r"^export\s+(?:default\s+)?(?:async\s+)?(function|const|let|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)", re.M)
_TS_IMPORT = re.compile(r"""^\s*import\s+(?:type\s+)?(?:[^'"]*?\s+from\s+)?['"]([^'"]+)['"]""", re.M)


def _ts_resolve(src: str, spec: str, files: set[str]) -> str | None:
    base = (Path(src).parent / spec).as_posix()
    parts: list[str] = []
    for p in base.split("/"):
        if p == "..":
            if parts:
                parts.pop()
        elif p != ".":
            parts.append(p)
    base = "/".join(parts)
    for cand in (base, base + ".ts", base + ".tsx", base + "/index.ts", base + "/index.tsx", base + ".d.ts"):
        if cand in files:
            return cand
    return None


def inventory_ts(inv: Inventory, text: str, files: set[str]) -> None:
    inv.kind = "TypeScript" + (" (React)" if inv.path.endswith(".tsx") else "")
    inv.exports = [(k, n) for k, n in _TS_EXPORT.findall(text)]
    for spec in _TS_IMPORT.findall(text):
        if spec.startswith("."):
            target = _ts_resolve(inv.path, spec, files)
            if target:
                inv.imports.add(target)
        else:
            inv.externals.add(spec if not spec.startswith("@") else "/".join(spec.split("/")[:2]))
    if ".test." in inv.path:
        inv.tests = len(re.findall(r"^\s*(?:it|test)\(", text, re.M))


_KINDS = {".md": "Markdown", ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".js": "JavaScript", ".json": "JSON",
          ".sh": "Shell script", ".txt": "Text", ".py": "Python module", ".yaml": "YAML", ".yml": "YAML"}


def build_inventory(files: list[str]) -> dict[str, Inventory]:
    fileset = set(files)
    invs: dict[str, Inventory] = {}
    for rel in files:
        inv = Inventory(rel)
        invs[rel] = inv
        p = ROOT / rel
        if not p.exists():
            inv.error = "deleted in the working copy (still tracked by git)"
            continue
        data = p.read_bytes()
        inv.bytes = len(data)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            inv.kind = "binary"
            continue
        inv.lines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        suffix = p.suffix.lower()
        inv.kind = _KINDS.get(suffix, {"requirements.txt": "pip requirements"}.get(p.name, "file"))
        if p.name.startswith(".env"):
            inv.kind = "environment template"
        elif p.name.startswith(".git"):
            inv.kind = "git configuration"
        if suffix == ".py":
            inventory_python(inv, text, fileset)
        elif suffix in (".ts", ".tsx"):
            inventory_ts(inv, text, fileset)
    return invs


def imported_by(invs: dict[str, Inventory]) -> dict[str, set[str]]:
    rev: dict[str, set[str]] = {}
    for inv in invs.values():
        for t in inv.imports | inv.lazy_imports:
            rev.setdefault(t, set()).add(inv.path)
    return rev


# ─── Rendering ────────────────────────────────────────────────────────────────────


def _e(s: str) -> str:
    return html.escape(s, quote=True)


_CURRENT = ' aria-current="page"'


def _title_attr(text: str) -> str:
    return f' title="{_e(text)}"' if text else ""


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


class Site:
    def __init__(self) -> None:
        self.problems: list[str] = []
        self.files = project_files()
        self.pages = load_pages(self.problems)
        self.invs = build_inventory(self.files)
        self.rev = imported_by(self.invs)
        self.entry_of: dict[str, tuple[Page, str]] = {}  # file -> (page, pattern)
        self._assign_entries()

    # Coverage: each project file must match exactly one entry, and each entry some file.
    def _assign_entries(self) -> None:
        patterns: list[tuple[Page, str]] = [(p, e) for p in self.pages for e in p.entries]
        seen: dict[str, Page] = {}
        for page, pat in patterns:
            if pat in seen:
                self.problems.append(f"{pat!r} has an entry on both {seen[pat].slug} and {page.slug}")
            seen[pat] = page
        for f in self.files:
            exact = [(pg, pat) for pg, pat in patterns if pat == f]
            matches = exact or [(pg, pat) for pg, pat in patterns if is_glob(pat) and glob_match(pat, f)]
            if not matches:
                self.problems.append(f"{f}: no entry documents this file")
            elif len(matches) > 1 and not exact:
                where = ", ".join(f"{pg.slug}:{pat}" for pg, pat in matches)
                self.problems.append(f"{f}: matched by more than one entry ({where})")
            if matches:
                self.entry_of[f] = matches[0]
        for page, pat in patterns:
            if not any(glob_match(pat, f) for f in self.files):
                self.problems.append(f"{page.slug}: entry {pat!r} matches no project file")

    def href_for_file(self, path: str) -> str | None:
        if path in self.entry_of:
            page, pat = self.entry_of[path]
            return f"{page.slug}.html#{file_anchor(pat)}"
        for page in self.pages:  # a link to a glob entry itself
            if path in page.entries:
                return f"{page.slug}.html#{file_anchor(path)}"
        return None

    # ── generated blocks ──

    def _file_links(self, paths: set[str] | list[str]) -> str:
        items = []
        for p in sorted(paths):
            href = self.href_for_file(p)
            label = f"<code>{_e(p)}</code>"
            items.append(f'<a href="{href}">{label}</a>' if href else label)
        return ", ".join(items)

    def inventory_html(self, pattern: str) -> str:
        matched = [f for f in self.files if glob_match(pattern, f)]
        if is_glob(pattern):
            rows = "".join(
                f"<tr><td><code>{_e(f)}</code></td><td>{_e(self.invs[f].kind or '-')}</td>"
                f"<td class=\"num\">{self.invs[f].lines or '-'}</td><td class=\"num\">{self.invs[f].bytes or '-'}</td></tr>"
                for f in matched)
            return (f'<details class="inventory" open><summary>Generated: {_plural(len(matched), "file")} matched</summary>'
                    f'<div class="table-wrap"><table><thead><tr><th>File</th><th>Kind</th><th class="num">Lines</th>'
                    f'<th class="num">Bytes</th></tr></thead><tbody>{rows}</tbody></table></div></details>')
        if not matched:
            return ""
        inv = self.invs[matched[0]]
        facts = []
        if inv.error:
            facts.append(f"<strong>{_e(inv.error)}</strong>")
        else:
            facts.append(_e(inv.kind or "file"))
            if inv.lines:
                facts.append(_plural(inv.lines, "line"))
            if inv.tests is not None:
                facts.append(_plural(inv.tests, "test case"))
        parts = [f'<p class="facts">{" · ".join(facts)}</p>']
        if inv.imports:
            parts.append(f"<p><span class=\"label\">Imports</span> {self._file_links(inv.imports)}</p>")
        if inv.lazy_imports:
            parts.append(f"<p><span class=\"label\">Imports inside functions</span> {self._file_links(inv.lazy_imports)}</p>")
        if inv.externals:
            parts.append(f"<p><span class=\"label\">Third-party</span> "
                         f"{', '.join(f'<code>{_e(x)}</code>' for x in sorted(inv.externals))}</p>")
        users = self.rev.get(inv.path)
        if users:
            parts.append(f"<p><span class=\"label\">Imported by</span> {self._file_links(users)}</p>")
        if inv.routes:
            parts.append("<p><span class=\"label\">Routes</span> "
                         f"{_plural(len(inv.routes), 'route')}, listed on the <a href=\"api.html\">HTTP API</a> page.</p>")
        rows = []
        for name, bases, methods in inv.classes:
            rows.append(f"<tr><td><code>class {_e(name)}</code></td><td>{_e(bases) or '-'}</td>"
                        f"<td>{', '.join(f'<code>{_e(m)}</code>' for m in methods) or '-'}</td></tr>")
        if rows:
            parts.append('<div class="table-wrap"><table><thead><tr><th>Class</th><th>Bases</th><th>Public methods</th>'
                         f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")
        if inv.functions:
            rows = "".join(f"<tr><td><code>{_e(sig)}</code></td><td>{_e(doc) or '-'}</td></tr>" for _, sig, doc in inv.functions)
            parts.append('<div class="table-wrap"><table><thead><tr><th>Function</th><th>Docstring (first paragraph)</th>'
                         f"</tr></thead><tbody>{rows}</tbody></table></div>")
        if inv.constants:
            rows = "".join(f"<tr><td><code>{_e(n)}</code></td><td><code>{_e(v)}</code></td></tr>" for n, v in inv.constants)
            parts.append('<div class="table-wrap"><table><thead><tr><th>Constant</th><th>Value</th></tr></thead>'
                         f"<tbody>{rows}</tbody></table></div>")
        if inv.exports:
            parts.append("<p><span class=\"label\">Exports</span> "
                         + ", ".join(f"<code>{_e(k)} {_e(n)}</code>" for k, n in inv.exports) + "</p>")
        return ('<details class="inventory"><summary>Generated inventory</summary>'
                + "".join(parts) + "</details>")

    def routes_html(self) -> str:
        inv = self.invs.get("web/server.py")
        if not inv or not inv.routes:
            self.problems.append("no routes found in web/server.py")
            return ""
        rows = "".join(
            f"<tr><td><code>{m}</code></td><td><code>{_e(p)}</code></td><td><code>{_e(fn)}</code></td>"
            f"<td>{_e(doc) or '-'}</td></tr>" for m, p, fn, doc in inv.routes)
        return (f'<p class="facts">Generated from <a href="{self.href_for_file("web/server.py")}"><code>web/server.py</code></a>: '
                f'{_plural(len(inv.routes), "route")}, in source order.</p>'
                '<div class="table-wrap"><table><thead><tr><th>Method</th><th>Path</th><th>Handler</th>'
                f"<th>Docstring (first paragraph)</th></tr></thead><tbody>{rows}</tbody></table></div>")

    def env_html(self) -> str:
        found: dict[str, dict[str, set[str]]] = {}
        for inv in self.invs.values():
            if inv.path.startswith(("archive/", "tests/")):
                continue
            for name, default in inv.env:
                d = found.setdefault(name, {"defaults": set(), "files": set()})
                d["defaults"].add(default or "(none)")
                d["files"].add(inv.path)
        example = ROOT / ".env.example"
        listed = set(re.findall(r"^([A-Z][A-Z0-9_]+)=", example.read_text(encoding="utf-8"), re.M)) if example.exists() else set()
        rows = "".join(
            f"<tr><td><code>{_e(n)}</code></td><td>{', '.join(f'<code>{_e(x)}</code>' for x in sorted(d['defaults']))}</td>"
            f"<td>{self._file_links(d['files'])}</td><td>{'yes' if n in listed else 'no'}</td></tr>"
            for n, d in sorted(found.items()))
        return ('<p class="facts">Generated: every <code>os.environ</code> / <code>os.getenv</code> read in runtime code '
                '(tests and archive excluded), with the default the code falls back to.</p>'
                '<div class="table-wrap"><table><thead><tr><th>Variable</th><th>Default in code</th><th>Read in</th>'
                f"<th>In <code>.env.example</code></th></tr></thead><tbody>{rows}</tbody></table></div>")

    def layers_html(self) -> str:
        counts: dict[tuple[str, str], int] = {}
        for inv in self.invs.values():
            src = inv.path.split("/")[0]
            if src not in LAYERS or not inv.path.endswith(".py"):
                continue
            for t in inv.imports | inv.lazy_imports:
                dst = t.split("/")[0]
                if dst != src:
                    counts[(src, dst)] = counts.get((src, dst), 0) + 1
        head = "".join(f"<th class=\"num\"><code>{l}</code></th>" for l in LAYERS)
        rows = ""
        for src in LAYERS:
            cells = "".join(f"<td class=\"num\">{counts.get((src, dst), '') if src != dst else '·'}</td>" for dst in LAYERS)
            rows += f"<tr><th><code>{src}</code></th>{cells}</tr>"
        return ('<p class="facts">Generated: the number of files in the row\'s package that import a file in the '
                'column\'s package (module-level and function-local imports both counted).</p>'
                f'<div class="table-wrap"><table class="matrix"><thead><tr><th>imports ↓ from →</th>{head}</tr></thead>'
                f"<tbody>{rows}</tbody></table></div>")

    def ledger_html(self) -> str:
        path = ROOT / "web" / "self_report.py"
        issues = None
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
                if any(isinstance(t, ast.Name) and t.id == "KNOWN_ISSUES" for t in targets):
                    issues = ast.literal_eval(node.value)
        except Exception as exc:
            self.problems.append(f"could not read KNOWN_ISSUES from web/self_report.py: {exc}")
            return ""
        if issues is None:
            self.problems.append("KNOWN_ISSUES not found in web/self_report.py")
            return ""
        order = {"OPEN": 0, "UNVERIFIED": 1, "BY_DESIGN": 2, "RESOLVED": 3}
        issues = sorted(issues, key=lambda i: (order.get(i.get("status"), 9), i.get("id", "")))
        counts: dict[str, int] = {}
        for i in issues:
            counts[i.get("status", "?")] = counts.get(i.get("status", "?"), 0) + 1
        summary = ", ".join(f"{n} {s.lower().replace('_', ' ')}" for s, n in sorted(counts.items(), key=lambda kv: order.get(kv[0], 9)))
        ctx = Ctx("ledger", self.href_for_file, self.problems)
        blocks = []
        for i in issues:
            blocks.append(
                f'<section class="issue"><h3 id="{_e(i.get("id", ""))}">{_e(i.get("title", ""))}'
                f'<a class="anchor" href="#{_e(i.get("id", ""))}" aria-label="Link to this issue">#</a></h3>'
                f'<p class="facts"><code>{_e(i.get("id", ""))}</code> · {_e(i.get("status", ""))} · '
                f'severity {_e(i.get("severity", ""))} · {_e(i.get("area", ""))}</p>'
                f'<p>{inline(i.get("detail", ""), ctx)}</p>'
                f'<p class="source-line">Source: {_e(i.get("source", ""))}</p></section>')
        return (f'<p class="facts">Generated from <a href="{self.href_for_file("web/self_report.py")}">'
                f'<code>KNOWN_ISSUES</code></a>: {_plural(len(issues), "entry")} ({summary}). Open items first.</p>'
                + "".join(blocks))

    def files_index_html(self) -> str:
        rows = []
        for f in self.files:
            href = self.href_for_file(f)
            inv = self.invs[f]
            page = self.entry_of.get(f, (None, ""))[0]
            name = f'<a href="{href}"><code>{_e(f)}</code></a>' if href else f"<code>{_e(f)}</code>"
            rows.append(f"<tr><td>{name}</td>"
                        f"<td>{_e(inv.kind or ('deleted' if inv.error else '-'))}</td><td class=\"num\">{inv.lines or '-'}</td>"
                        f"<td>{_e(page.title) if page else '-'}</td></tr>")
        return (f'<p class="facts">Generated: {_plural(len(self.files), "project file")} (tracked by git, or new and '
                'not ignored).</p><div class="table-wrap"><table><thead><tr><th>File</th><th>Kind</th>'
                f'<th class="num">Lines</th><th>Documented on</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

    def stats_html(self) -> str:
        py = [i for i in self.invs.values() if i.path.endswith(".py") and not i.path.startswith("archive/")]
        ts = [i for i in self.invs.values() if i.path.endswith((".ts", ".tsx")) and "/tests/" not in i.path]
        pyt = sum(i.tests or 0 for i in py if i.path.startswith("tests/"))
        tst = sum(i.tests or 0 for i in self.invs.values() if ".test." in i.path)
        return ('<div class="stats">'
                f'<div><span class="stat">{len(self.files)}</span><span class="stat-label">project files</span></div>'
                f'<div><span class="stat">{len([i for i in py if not i.path.startswith("tests/")])}</span><span class="stat-label">Python modules (not tests)</span></div>'
                f'<div><span class="stat">{len(ts)}</span><span class="stat-label">frontend source files</span></div>'
                f'<div><span class="stat">{pyt}</span><span class="stat-label">Python test cases</span></div>'
                f'<div><span class="stat">{tst}</span><span class="stat-label">frontend test cases</span></div>'
                '</div><p class="facts">Generated by counting test functions in the source; the number that pass is '
                'whatever the last run of the suites says, not this.</p>')

    # ── pages ──

    def render(self) -> dict[str, str]:
        for page in self.pages:
            ctx = Ctx(page.slug, self.href_for_file, self.problems)

            def hook(level: int, raw: str, page=page) -> str | None:
                m = re.fullmatch(r"`([^`]+)`", raw)
                if level == 2 and m and m.group(1) in page.entries:
                    return self.inventory_html(m.group(1))
                return None

            body = render_markdown(page.body, ctx, page.headings, hook)
            generated = {"{{routes}}": self.routes_html, "{{env}}": self.env_html, "{{layers}}": self.layers_html,
                         "{{ledger}}": self.ledger_html, "{{files-index}}": self.files_index_html,
                         "{{stats}}": self.stats_html}
            for key, fn in generated.items():
                if key in body:
                    body = body.replace(key, fn())
            if page.slug == "ledger":  # generated headings join the page's table of contents
                for m in re.finditer(r'<h3 id="([^"]+)">(.*?)<a class="anchor"', body):
                    page.headings.append(Heading(3, html.unescape(re.sub(r"<[^>]+>", "", m.group(2))), m.group(1)))
            page.html = body
        out = {f"{p.slug}.html": self.page_html(p) for p in self.pages}
        out["assets/search-index.js"] = self.search_index()
        self.check_links(out)
        return out

    def nav_html(self, current: Page) -> str:
        groups = []
        for section in SECTIONS:
            items = [p for p in self.pages if p.section == section]
            if not items:
                continue
            lis = "".join(
                f'<li><a href="{p.slug}.html"{_CURRENT if p is current else ""}'
                f'{_title_attr(p.summary)}>{_e(p.title)}</a></li>' for p in items)
            groups.append(f'<h2 class="nav-section">{section}</h2><ul>{lis}</ul>')
        return "".join(groups)

    def toc_html(self, page: Page) -> str:
        hs = [h for h in page.headings if h.level in (2, 3) and not (page.section == "Files" and h.level == 3)]
        if len(hs) < 3:
            return ""
        items = "".join(
            f'<li class="toc-{h.level}"><a href="#{h.anchor}">{inline_plain(h.text, Ctx(page.slug, self.href_for_file, []))}</a></li>'
            for h in hs)
        return f'<nav class="toc" aria-label="On this page"><h2>On this page</h2><ul>{items}</ul></nav>'

    def page_html(self, page: Page) -> str:
        idx = self.pages.index(page)
        prev_p = self.pages[idx - 1] if idx > 0 else None
        next_p = self.pages[idx + 1] if idx + 1 < len(self.pages) else None
        pager = '<nav class="pager" aria-label="Previous and next page">'
        pager += f'<a class="prev" href="{prev_p.slug}.html"><span>Previous</span>{_e(prev_p.title)}</a>' if prev_p else "<span></span>"
        pager += f'<a class="next" href="{next_p.slug}.html"><span>Next</span>{_e(next_p.title)}</a>' if next_p else "<span></span>"
        pager += "</nav>"
        src_rel = page.source.relative_to(ROOT).as_posix()
        crumbs = (f'<a href="index.html">Reference</a> <span aria-hidden="true">/</span> {_e(page.section)}'
                  f' <span aria-hidden="true">/</span> <span aria-current="page">{_e(page.title)}</span>')
        today = _dt.date.today().isoformat()
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(page.title)} · {SITE_TITLE}</title>
<meta name="description" content="{_e(page.summary)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital@0;1&family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap">
<script>try{{if(localStorage.getItem("docs-theme")==="dark")document.documentElement.dataset.theme="dark"}}catch(e){{}}</script>
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a class="brand" href="index.html">{SITE_TITLE}</a>
  <div class="search" role="search">
    <label for="search-input" class="visually-hidden">Search the reference</label>
    <input id="search-input" type="search" placeholder="Search files, functions, pages" autocomplete="off"
           aria-controls="search-results" aria-describedby="search-status">
    <p id="search-status" class="visually-hidden" aria-live="polite"></p>
    <ul id="search-results" class="search-results" hidden></ul>
  </div>
  <button class="theme-toggle" type="button" aria-pressed="false">Dark theme</button>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
</header>
<div class="layout">
  <nav id="site-nav" class="site-nav" aria-label="Reference pages">{self.nav_html(page)}</nav>
  <main id="main">
    <p class="crumbs">{crumbs}</p>
    <p class="eyebrow">{_e(page.section)}</p>
    <h1>{_e(page.title)}</h1>
    {f'<p class="lede">{_e(page.summary)}</p>' if page.summary else ''}
    {self.toc_html(page)}
    <article>
{page.html}
    </article>
    {pager}
    <footer class="site-footer">
      <p class="source-line">Written in <code>{_e(src_rel)}</code> · generated parts built from the source
      on {today} by <code>scripts/build_docs.py</code></p>
    </footer>
  </main>
</div>
<script src="assets/search-index.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
"""

    def search_index(self) -> str:
        entries = []
        for page in self.pages:
            entries.append({"t": page.title, "u": f"{page.slug}.html", "k": "page", "s": page.section, "x": page.summary})
            for h in page.headings:
                if h.level > 3:
                    continue
                text = re.sub(r"[`*]", "", h.text)
                kind = "file" if h.anchor.startswith("f-") else ("issue" if page.slug == "ledger" else "section")
                entries.append({"t": text, "u": f"{page.slug}.html#{h.anchor}", "k": kind, "s": page.title})
        for inv in self.invs.values():
            href = self.href_for_file(inv.path)
            if not href:
                continue
            for name, _, doc in inv.functions:
                entries.append({"t": name, "u": href, "k": "function", "s": inv.path, "x": doc[:120]})
            for name, _, _ in inv.classes:
                entries.append({"t": name, "u": href, "k": "class", "s": inv.path})
            for kind, name in inv.exports:
                entries.append({"t": name, "u": href, "k": kind, "s": inv.path})
            for m, p, fn, doc in inv.routes:
                entries.append({"t": f"{m} {p}", "u": "api.html", "k": "route", "s": fn, "x": doc[:120]})
        return ("// Generated by scripts/build_docs.py. A script, not JSON, so it loads from file:// too.\n"
                f"window.DOCS_INDEX = {json.dumps(entries, ensure_ascii=False, separators=(',', ':'))};\n")

    def check_links(self, out: dict[str, str]) -> None:
        anchors = {name: set(re.findall(r'\sid="([^"]+)"', text)) for name, text in out.items() if name.endswith(".html")}
        assets = {p.relative_to(OUT).as_posix() for p in (OUT / "assets").glob("*")} | {"assets/search-index.js"}
        for name, text in out.items():
            if not name.endswith(".html"):
                continue
            for href in re.findall(r'href="([^"]+)"', text):
                if re.match(r"^(https?:|mailto:)", href):
                    continue
                target, _, frag = href.partition("#")
                target = target or name
                if target.startswith("assets/"):
                    if target not in assets:
                        self.problems.append(f"{name}: link to missing asset {target}")
                    continue
                if target.startswith("../"):
                    if not (OUT / target).resolve().exists():
                        self.problems.append(f"{name}: link to missing file {target}")
                    continue
                if target not in anchors:
                    self.problems.append(f"{name}: link to missing page {href}")
                elif frag and frag not in anchors[target]:
                    self.problems.append(f"{name}: link to missing anchor {href}")


def build(write: bool = True) -> list[str]:
    """Build the site. Returns the problems found (empty means it's complete and consistent)."""
    site = Site()
    out = site.render()
    if write:
        for name, text in out.items():
            target = OUT / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")
    return sorted(set(site.problems))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="build in memory and report problems; write nothing")
    args = parser.parse_args()
    problems = build(write=not args.check)
    for p in problems:
        print(f"problem: {p}")
    print(f"{'checked' if args.check else 'built'}: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
