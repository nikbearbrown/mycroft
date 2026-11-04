"""Maps the configured upgrades to an ordered list of concrete transform steps.

Each step becomes its own commit on the migration branch, so every changed line can be traced
back to the step (and recipe) that produced it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .analyzer import Inventory
from .config import MigrationConfig

MIGRATE_JAVA = "org.openrewrite.recipe:rewrite-migrate-java:RELEASE"
HIBERNATE = "org.openrewrite.recipe:rewrite-hibernate:RELEASE"
TESTING = "org.openrewrite.recipe:rewrite-testing-frameworks:RELEASE"
SPRING = "org.openrewrite.recipe:rewrite-spring:RELEASE"

JAVA_RECIPES = {
    11: "org.openrewrite.java.migrate.Java8toJava11",
    17: "org.openrewrite.java.migrate.UpgradeToJava17",
    21: "org.openrewrite.java.migrate.UpgradeToJava21",
}


@dataclass
class Step:
    id: str
    engine: str                     # openrewrite | xml | server-config | jar-transformer | manual
    description: str
    recipes: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    risk: str = "low"               # default risk for files touched by this step

    @property
    def commit_message(self) -> str:
        return f"migrator({self.id}): {self.description}"


@dataclass
class Plan:
    steps: list[Step]
    manual_items: list[str] = field(default_factory=list)


def build_plan(cfg: MigrationConfig, inv: Inventory) -> Plan:
    steps: list[Step] = []
    manual: list[str] = []

    if cfg.target.java > cfg.source.java:
        recipe = JAVA_RECIPES.get(cfg.target.java)
        if recipe is None:
            manual.append(f"No Java {cfg.target.java} recipe mapped; upgrade the compiler level by hand.")
        else:
            steps.append(Step("java-upgrade", "openrewrite",
                              f"Java {cfg.source.java} -> {cfg.target.java}",
                              [recipe], [MIGRATE_JAVA], risk="medium"))

    if "javax-to-jakarta" in cfg.upgrades:
        steps.append(Step("javax-to-jakarta", "openrewrite", "javax.* -> jakarta.* (Jakarta EE 10)",
                          ["org.openrewrite.java.migrate.jakarta.JakartaEE10"], [MIGRATE_JAVA]))
        steps.append(Step("descriptors", "xml",
                          "Jakarta namespaces in XML descriptors, JSP taglibs and JSF views"))
        if inv.bundled_jars:
            steps.append(Step("bundled-jars", "jar-transformer",
                              f"Eclipse Transformer on {len(inv.bundled_jars)} bundled JAR(s)", risk="medium"))

    if "hibernate-5-to-6" in cfg.upgrades:
        steps.append(Step("hibernate-5-to-6", "openrewrite", "Hibernate 5 -> 6",
                          ["org.openrewrite.hibernate.MigrateToHibernate61"], [HIBERNATE], risk="high"))
        if any(f.category == "hibernate" and not f.automatable for f in inv.findings):
            manual.append("Legacy Hibernate Criteria API usage must be rewritten to JPA Criteria by hand.")

    if "junit4-to-junit5" in cfg.upgrades:
        steps.append(Step("junit4-to-junit5", "openrewrite", "JUnit 4 -> JUnit 5",
                          ["org.openrewrite.java.testing.junit5.JUnit4to5Migration"], [TESTING]))

    if cfg.target_family == "spring-boot":
        steps.append(Step("spring-boot", "openrewrite", "Spring Boot 3 baseline",
                          ["org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_0"], [SPRING], risk="high"))
        manual.append("Replacing the application server with Spring Boot requires re-wiring EJBs "
                      "and container-managed resources; the tool only applies the recipe baseline.")
    elif cfg.target_family == "quarkus":
        manual.append("Quarkus target: run `quarkus update`/MTA quarkus rules after this pass; "
                      "EJB and JSF code needs manual porting.")

    if cfg.custom_recipes:
        steps.append(Step("custom-recipes", "openrewrite", "Organisation recipes",
                          list(cfg.custom_recipes), risk="medium"))

    if cfg.target_family in ("jboss-eap-8", "wildfly-3"):
        steps.append(Step("server-config", "server-config",
                          "Generate JBoss CLI scripts for the target server", risk="medium"))

    if "picketlink-to-elytron" in cfg.upgrades:
        steps.append(Step("picketlink-to-elytron", "server-config",
                          "Legacy security domains -> Elytron (CLI script)", risk="high"))

    for f in inv.manual_findings:
        manual.append(f"{f.file}:{f.line} [{f.category}] {f.message}")

    return Plan(steps=steps, manual_items=manual)
