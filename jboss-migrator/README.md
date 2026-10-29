# jboss-migrator

A config-driven tool for upgrading JBoss EAP applications, for example **EAP 7.x on Java 8 → EAP 8.0 on
Java 17** (WildFly, Quarkus and Spring Boot targets get the recipe baseline plus a list of manual work).
It runs the existing engines (OpenRewrite, Red Hat MTA, Eclipse Transformer, JBoss CLI) in order,
**proves** that business and UI code changed only in namespaces, and opens a PR with a migration report
and a per-class unit test plan.

> **Expect some manual work.** No tool migrates a real JBoss app 100% automatically. Namespaces,
> dependencies, descriptors and the test framework are highly automatable. Custom security modules,
> vendor-specific JNDI lookups and frameworks like Seam usually need a human. This tool automates what's
> safe, won't touch protected code beyond namespace changes, and lists exactly what's left.

## Pipeline

| # | Stage | What happens | Module |
|---|-------|--------------|--------|
| 1 | **Inputs** | Git URL, branch, and `migration.yaml` (source/target, upgrades, protected paths) | `config.py` |
| 2 | **Clone & baseline** | Clone, create `migration/<target>`, build, run tests, record per-test results; optional characterization test skeletons and Playwright screenshots of the source app | `git_ops.py`, `baseline.py` |
| 3 | **Analyze** | Build tool, dependencies, descriptors (`jboss-web.xml`, `jboss-deployment-structure.xml`, `persistence.xml`, …), `standalone.xml`, risky API usage; merges `mta-cli analyze` output when it's installed | `analyzer.py` |
| 4 | **Transform** | One commit per step: OpenRewrite recipes (Java 17, Jakarta EE 10, Hibernate 6, JUnit 5, your org recipes), XML/JSP/JSF namespace rewrites, Eclipse Transformer for bundled JARs, JBoss CLI scripts for datasources and Elytron. Optional LLM *suggestions* for leftover compile errors (never applied) | `planner.py`, `transformers/` |
| 5 | **Verify** | **Diff guard** on `protected_paths`, build on target, per-test pass/fail compared with baseline, UI screenshots on the target container compared with baseline | `verify/` |
| 6 | **Test plan & PR** | Per changed class: what changed, which step/recipe, risk, existing tests, test cases, gaps. Writes Markdown + XLSX, pushes the branch, opens a PR | `testplan/`, `report.py` |

## Quick start

```bash
pip install -e ".[dev]"            # core: pyyaml, jinja2, openpyxl
pip install -e ".[ui]" && playwright install chromium   # optional: UI screenshot check
pip install -e ".[llm]"            # optional: LLM fix suggestions (needs ANTHROPIC_API_KEY)

# See what would run against a local checkout
jboss-migrator plan    --config migration.yaml --repo-path ../orders
jboss-migrator analyze --config migration.yaml --repo-path ../orders

# Full run (clones repo.url; GITHUB_TOKEN enables automatic PR creation)
jboss-migrator migrate --config migration.yaml
jboss-migrator migrate --config migration.yaml --repo-path ../orders --no-push

# Re-check the guard between any two commits
jboss-migrator guard --config migration.yaml --repo-path ../orders --base develop --head HEAD
```

`migrate` exits with `0` when every check passes and `2` when something needs attention. The report says what.

External tools, used when they're on PATH or configured under `tools:`: Maven or Gradle (wrappers are
preferred), a JDK, `mta-cli`, the Eclipse Transformer CLI jar, Docker (for UI verification).
Missing optional tools are listed under "Engines skipped" in the report instead of failing the run.

## Configuration

See [`migration.yaml`](migration.yaml). Supported `upgrades`:

| Upgrade | Engine |
|---------|--------|
| *(java version bump)* | `org.openrewrite.java.migrate.UpgradeToJava17` (or 11/21) |
| `javax-to-jakarta` | `org.openrewrite.java.migrate.jakarta.JakartaEE10` + descriptor/JSP/JSF rewrites + Eclipse Transformer |
| `hibernate-5-to-6` | `org.openrewrite.hibernate.MigrateToHibernate61` |
| `junit4-to-junit5` | `org.openrewrite.java.testing.junit5.JUnit4to5Migration` |
| `picketlink-to-elytron` | `migration/jboss-cli/02-elytron.cli` from legacy security domains (Database, UsersRoles, RealmDirect mapped; others flagged) |

Organisation recipes live in [`recipes/`](recipes/). Every `*.yml` there is merged into the OpenRewrite
config, and the names listed under `custom_recipes` are activated.

## How the diff guard works

For every changed file matching `protected_paths`, the removed and added lines are compared after
normalization: javax→jakarta packages, JSF/JSTL/descriptor namespace URIs, schema file versions and
descriptor `version=""` attributes are canonicalized, and import and annotation-only lines are ignored. If
any line is left over on either side, the file is a violation and the run fails, with the offending lines
shown in the report. The guard and the XML transformer share one rule set (`migrator/namespaces.py`),
so the guard allows exactly the edits the tool is permitted to make.

## Output on the migration branch

```
migration/
├── migration-report.md      # verification results, steps, inventory, manual items
├── test-plan.md             # per-class test plan
├── test-plan.xlsx
└── jboss-cli/
    ├── 01-datasources.cli
    └── 02-elytron.cli
```

## Layout

```
jboss-migrator/
├── migrator/
│   ├── cli.py              # entry point: migrate | plan | analyze | guard
│   ├── pipeline.py         # stage orchestration
│   ├── git_ops.py          # clone, branch, per-step commits, push, PR
│   ├── baseline.py         # build, run tests, UI snapshots
│   ├── analyzer.py         # inventory + MTA report parsing
│   ├── planner.py          # maps upgrades -> steps/recipes
│   ├── namespaces.py       # javax->jakarta rules shared by transformer and guard
│   ├── transformers/       # openrewrite, xml_descriptors, server_config, jar_transformer, llm_suggest
│   ├── verify/             # diff_guard, test_compare, ui_compare, deploy
│   └── testplan/           # per-class test plan + characterization tests
├── recipes/                # custom OpenRewrite YAML recipes
├── templates/              # report, test plan and PR templates
├── docker/                 # source and target JBoss images for verification
├── tests/
└── migration.yaml
```

## Development

```bash
pip install -e ".[dev]"
pytest -q
```
