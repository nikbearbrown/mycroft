"""
The reference docs (docs/reference/) cover the whole project and are internally consistent.

What this locks in
    - Every project file (tracked by git, or new and not ignored) matches exactly one entry
      in docs/reference/src/, and every entry matches a file. A new file without an entry
      fails here, which is the point: the docs can't silently fall behind the code.
    - Every [[file link]], page link and anchor in the built site resolves.
    - The site builds (scripts/build_docs.py), in memory, without writing anything.
    - The Markdown renderer handles the constructs AUTHORING.md documents, and globs match
      the way it says.

Network-free and model-free: the builder parses source with ast and regular expressions and
never imports project modules. It does call `git ls-files`; without git the coverage test
is skipped, not failed, since there is then no list of project files to check against.
"""

from __future__ import annotations

import shutil
import unittest

from scripts import build_docs as bd


@unittest.skipUnless(shutil.which("git"), "git is needed to list the project's files")
class DocsCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = bd.Site()
        cls.out = cls.site.render()

    def test_the_site_builds_with_no_problems(self):
        problems = sorted(set(self.site.problems))
        self.assertEqual(problems, [], "\n" + "\n".join(problems) + "\n\nFix the docs in docs/reference/src/, "
                         "then run: python scripts/build_docs.py")

    def test_every_project_file_is_documented(self):
        undocumented = [f for f in self.site.files if f not in self.site.entry_of]
        self.assertEqual(undocumented, [])

    def test_this_test_and_the_builder_are_themselves_documented(self):
        for f in ("tests/test_docs_coverage.py", "scripts/build_docs.py"):
            self.assertIn(f, self.site.entry_of)

    def test_every_page_links_the_stylesheet_and_search(self):
        for name, text in self.out.items():
            if name.endswith(".html"):
                self.assertIn('href="assets/site.css"', text, name)
                self.assertIn('src="assets/search-index.js"', text, name)

    def test_every_page_has_the_theme_toggle_and_applies_a_saved_choice_before_paint(self):
        for name, text in self.out.items():
            if name.endswith(".html"):
                self.assertIn('class="theme-toggle"', text, name)
                head = text.split("</head>")[0]
                self.assertLess(head.index('localStorage.getItem("docs-theme")'),
                                head.index('href="assets/site.css"'), name)


class MarkdownTest(unittest.TestCase):
    def render(self, md, files=None):
        problems: list[str] = []
        files = files or {}
        ctx = bd.Ctx("t", lambda p: files.get(p), problems)
        return bd.render_markdown(md, ctx, []), problems

    def test_file_links_resolve_or_are_reported(self):
        html, problems = self.render("See [[core/parsing.py]] and [[nope.py]].", {"core/parsing.py": "files-core.html#f-core-parsing-py"})
        self.assertIn('<a href="files-core.html#f-core-parsing-py"><code>core/parsing.py</code></a>', html)
        self.assertEqual(problems, ["t: [[nope.py]] matches no file entry"])

    def test_code_spans_are_not_markup(self):
        html, _ = self.render("Use `**not bold** <b>` here, and **bold**.")
        self.assertIn("<code>**not bold** &lt;b&gt;</code>", html)
        self.assertIn("<strong>bold</strong>", html)

    def test_file_entry_headings_get_file_anchors(self):
        headings: list = []
        html = bd.render_markdown("## `web/server.py`\n\ntext", bd.Ctx("t", lambda p: None, []), headings)
        self.assertIn('id="f-web-server-py"', html)
        self.assertEqual(headings[0].anchor, "f-web-server-py")

    def test_tables_lists_and_callouts(self):
        html, _ = self.render("| a | b |\n|---|---|\n| `x\\|y` | 2 |\n\n- one\n  - nested\n- two\n\n> note")
        self.assertIn("<td><code>x|y</code></td>", html)
        self.assertIn("<ul><li>one<ul><li>nested</li></ul></li><li>two</li></ul>", html)
        self.assertIn('<aside class="callout"><p>note</p></aside>', html)

    def test_text_is_escaped(self):
        html, _ = self.render("a < b & c")
        self.assertIn("a &lt; b &amp; c", html)


class GlobTest(unittest.TestCase):
    def test_single_star_stays_in_its_folder(self):
        self.assertTrue(bd.glob_match("tests/fixtures/*", "tests/fixtures/a.json"))
        self.assertFalse(bd.glob_match("tests/fixtures/*", "tests/fixtures/sub/a.json"))

    def test_double_star_crosses_folders(self):
        self.assertTrue(bd.glob_match("docs/reference/**", "docs/reference/assets/site.css"))


if __name__ == "__main__":
    unittest.main()
