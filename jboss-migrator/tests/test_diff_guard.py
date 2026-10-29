from migrator.verify import diff_guard
from tests.conftest import write

PROTECTED = ["src/main/java/com/company/orders/domain/**", "src/main/webapp/**"]

ORDER = """package com.company.orders.domain;

import javax.persistence.Entity;
import javax.persistence.Id;

@Entity
public class Order {
    @Id
    private Long id;

    public java.math.BigDecimal total(java.math.BigDecimal net) {
        return net.multiply(new java.math.BigDecimal("1.20"));
    }
}
"""


def test_glob_matching():
    assert diff_guard.is_protected("src/main/webapp/WEB-INF/web.xml", PROTECTED)
    assert diff_guard.is_protected("src/main/java/com/company/orders/domain/Order.java", PROTECTED)
    assert diff_guard.is_protected("a/b/c.xhtml", ["**/*.xhtml"])
    assert not diff_guard.is_protected("src/main/java/com/company/orders/service/X.java", PROTECTED)
    assert not diff_guard.is_protected("src/main/webapp.txt", PROTECTED)


def _setup(repo):
    write(repo.path, "src/main/java/com/company/orders/domain/Order.java", ORDER)
    write(repo.path, "src/main/webapp/index.xhtml",
          '<html xmlns:h="http://xmlns.jcp.org/jsf/html">\n<h:body>Orders</h:body>\n</html>\n')
    return repo.commit_all("baseline")


def test_namespace_only_changes_pass(git_repo):
    base = _setup(git_repo)
    order = git_repo.path / "src/main/java/com/company/orders/domain/Order.java"
    order.write_text(ORDER.replace("javax.persistence", "jakarta.persistence")
                     .replace("@Entity", '@Entity\n@Table(name = "orders")'), encoding="utf-8")
    view = git_repo.path / "src/main/webapp/index.xhtml"
    view.write_text(view.read_text().replace("http://xmlns.jcp.org/jsf/html", "jakarta.faces.html"),
                    encoding="utf-8")
    git_repo.commit_all("migrate")

    result = diff_guard.check(git_repo, base, "HEAD", PROTECTED)
    assert sorted(result.checked) == ["src/main/java/com/company/orders/domain/Order.java",
                                      "src/main/webapp/index.xhtml"]
    assert result.ok, result.violations


def test_business_logic_change_fails(git_repo):
    base = _setup(git_repo)
    order = git_repo.path / "src/main/java/com/company/orders/domain/Order.java"
    order.write_text(ORDER.replace('"1.20"', '"1.21"'), encoding="utf-8")
    view = git_repo.path / "src/main/webapp/index.xhtml"
    view.write_text(view.read_text().replace("Orders", "All orders"), encoding="utf-8")
    git_repo.commit_all("sneaky")

    result = diff_guard.check(git_repo, base, "HEAD", PROTECTED)
    assert {v.file for v in result.violations} == {
        "src/main/java/com/company/orders/domain/Order.java", "src/main/webapp/index.xhtml"}
    order_v = next(v for v in result.violations if v.file.endswith("Order.java"))
    assert any('"1.21"' in line for line in order_v.added)
    assert any('"1.20"' in line for line in order_v.removed)
