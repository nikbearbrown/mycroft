from migrator import analyzer, config, planner
from tests.conftest import ROOT, write

POM = """<project xmlns="http://maven.apache.org/POM/4.0.0">
  <properties><hibernate.version>5.3.20.Final</hibernate.version></properties>
  <dependencies>
    <dependency><groupId>org.hibernate</groupId><artifactId>hibernate-core</artifactId>
      <version>${hibernate.version}</version><scope>provided</scope></dependency>
    <dependency><groupId>junit</groupId><artifactId>junit</artifactId><version>4.13.2</version>
      <scope>test</scope></dependency>
  </dependencies>
</project>"""

SECURITY_BEAN = """package com.company.orders.security;

import javax.ejb.Stateless;
import org.picketlink.Identity;

@Stateless
public class LoginBean {
    Object ds = new javax.naming.InitialContext().lookup("java:jboss/datasources/OrdersDS");
}
"""


def _project(tmp_path):
    write(tmp_path, "pom.xml", POM)
    write(tmp_path, "src/main/java/com/company/orders/security/LoginBean.java", SECURITY_BEAN)
    write(tmp_path, "src/main/webapp/WEB-INF/jboss-web.xml",
          "<jboss-web><security-domain>orders</security-domain></jboss-web>")
    write(tmp_path, "src/main/webapp/WEB-INF/lib/legacy.jar", "not really a jar")
    cfg = config.load(ROOT / "migration.yaml")
    cfg.tools.mta_cli = "definitely-not-installed-mta"
    return cfg


def test_inventory(tmp_path):
    cfg = _project(tmp_path)
    inv = analyzer.analyze(cfg, tmp_path, "maven", tmp_path / "out")
    deps = {(d.artifact, d.version, d.scope) for d in inv.dependencies}
    assert ("hibernate-core", "5.3.20.Final", "provided") in deps
    assert "src/main/webapp/WEB-INF/jboss-web.xml" in inv.descriptors
    assert inv.bundled_jars == ["src/main/webapp/WEB-INF/lib/legacy.jar"]
    cats = inv.by_category()
    assert {"jakarta-namespace", "security", "jndi"} <= cats.keys()
    assert not inv.mta_ran


def test_plan_orders_steps_and_lists_manual_items(tmp_path):
    cfg = _project(tmp_path)
    inv = analyzer.analyze(cfg, tmp_path, "maven", tmp_path / "out")
    plan = planner.build_plan(cfg, inv)
    ids = [s.id for s in plan.steps]
    assert ids == ["java-upgrade", "javax-to-jakarta", "descriptors", "bundled-jars",
                   "hibernate-5-to-6", "junit4-to-junit5", "custom-recipes", "server-config",
                   "picketlink-to-elytron"]
    jakarta = plan.steps[1]
    assert jakarta.recipes == ["org.openrewrite.java.migrate.jakarta.JakartaEE10"]
    assert any("PicketLink" in m for m in plan.manual_items)
    assert any("java:jboss/" in m for m in plan.manual_items)


def test_parse_mta_output(tmp_path):
    write(tmp_path, "src/A.java", "class A {}")
    output = tmp_path / "mta" / "output.yaml"
    write(tmp_path, "mta/output.yaml", f"""
- name: eap8/eap7
  violations:
    javax-to-jakarta-import-00001:
      description: Replace javax with jakarta
      category: mandatory
      effort: 1
      incidents:
        - uri: file://{(tmp_path / 'src/A.java').as_posix()}
          message: Replace the `javax.ejb` import
          lineNumber: 3
    picketlink-00002:
      description: PicketLink removed
      category: mandatory
      effort: 5
      incidents:
        - uri: file://{(tmp_path / 'src/A.java').as_posix()}
          lineNumber: 9
""")
    found = analyzer.parse_mta_output(output, tmp_path)
    assert [(f.file, f.line, f.automatable) for f in found] == [("src/A.java", 3, True),
                                                                ("src/A.java", 9, False)]
    assert found[0].category == "mta:mandatory"
