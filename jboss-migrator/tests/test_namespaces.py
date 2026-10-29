from migrator import namespaces
from migrator.transformers import xml_descriptors
from tests.conftest import write

WEB_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!-- keep this comment -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">
    <context-param>
        <param-name>javax.faces.PROJECT_STAGE</param-name>
        <param-value>Production</param-value>
    </context-param>
    <resource-ref><res-type>javax.sql.DataSource</res-type></resource-ref>
</web-app>
"""


def test_package_rewrite_skips_jdk_packages():
    src = ("import javax.servlet.http.HttpServlet; import javax.sql.DataSource; "
           "import javax.annotation.PostConstruct; import javax.annotation.processing.Processor; "
           "import javax.transaction.Transactional; import javax.transaction.xa.XAResource;")
    out = namespaces.rewrite_text(src)
    assert "jakarta.servlet.http.HttpServlet" in out
    assert "javax.sql.DataSource" in out
    assert "jakarta.annotation.PostConstruct" in out
    assert "javax.annotation.processing.Processor" in out
    assert "jakarta.transaction.Transactional" in out
    assert "javax.transaction.xa.XAResource" in out


def test_web_xml_rewrite_preserves_formatting():
    out = namespaces.bump_root_version(namespaces.rewrite_text(WEB_XML))
    assert 'xmlns="https://jakarta.ee/xml/ns/jakartaee"' in out
    assert "https://jakarta.ee/xml/ns/jakartaee/web-app_6_0.xsd" in out
    assert 'version="6.0"' in out
    assert '<?xml version="1.0"' in out          # XML declaration untouched
    assert "jakarta.faces.PROJECT_STAGE" in out
    assert "javax.sql.DataSource" in out
    assert "<!-- keep this comment -->" in out
    assert namespaces.rewrite_text(out) == out   # idempotent


def test_views_and_taglibs(tmp_path):
    write(tmp_path, "src/main/webapp/index.xhtml",
          '<html xmlns:h="http://xmlns.jcp.org/jsf/html" xmlns:f="http://java.sun.com/jsf/core">'
          '<h:body>Hello</h:body></html>')
    write(tmp_path, "src/main/webapp/list.jsp",
          '<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>\n<c:out value="x"/>')
    write(tmp_path, "src/main/resources/META-INF/persistence.xml",
          '<persistence xmlns="http://xmlns.jcp.org/xml/ns/persistence" version="2.2">'
          '<property name="javax.persistence.lock.timeout" value="1"/></persistence>')
    write(tmp_path, "target/classes/ignored.xhtml", 'xmlns:h="http://xmlns.jcp.org/jsf/html"')

    changed = sorted(xml_descriptors.run(tmp_path))
    assert changed == ["src/main/resources/META-INF/persistence.xml",
                       "src/main/webapp/index.xhtml", "src/main/webapp/list.jsp"]
    assert 'xmlns:h="jakarta.faces.html"' in (tmp_path / "src/main/webapp/index.xhtml").read_text()
    assert 'uri="jakarta.tags.core"' in (tmp_path / "src/main/webapp/list.jsp").read_text()
    persistence = (tmp_path / "src/main/resources/META-INF/persistence.xml").read_text()
    assert 'version="3.0"' in persistence and "jakarta.persistence.lock.timeout" in persistence
