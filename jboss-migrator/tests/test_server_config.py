from migrator.transformers import server_config
from tests.conftest import write

STANDALONE = """<server xmlns="urn:jboss:domain:10.0">
  <profile>
    <subsystem xmlns="urn:jboss:domain:datasources:5.0">
      <datasources>
        <datasource jndi-name="java:jboss/datasources/OrdersDS" pool-name="OrdersDS">
          <connection-url>jdbc:postgresql://db:5432/orders</connection-url>
          <driver>postgresql</driver>
          <security><user-name>orders</user-name><password>secret</password></security>
        </datasource>
      </datasources>
    </subsystem>
    <subsystem xmlns="urn:jboss:domain:security:2.0">
      <security-domains>
        <security-domain name="other"><authentication>
          <login-module code="Remoting" flag="optional"/></authentication></security-domain>
        <security-domain name="orders"><authentication>
          <login-module code="Database" flag="required">
            <module-option name="dsJndiName" value="java:jboss/datasources/OrdersDS"/>
            <module-option name="principalsQuery" value="SELECT pwd FROM app_user WHERE login=?"/>
            <module-option name="rolesQuery" value="SELECT role, 'Roles' FROM app_role WHERE login=?"/>
          </login-module></authentication></security-domain>
        <security-domain name="partners"><authentication>
          <login-module code="com.company.sso.SsoLoginModule" flag="required"/>
        </authentication></security-domain>
      </security-domains>
    </subsystem>
  </profile>
</server>"""


def test_generates_datasource_and_elytron_scripts(tmp_path):
    write(tmp_path, "configuration/standalone.xml", STANDALONE)
    written, manual = server_config.run(tmp_path, include_security=True)
    assert written == ["migration/jboss-cli/01-datasources.cli", "migration/jboss-cli/02-elytron.cli"]

    ds = (tmp_path / written[0]).read_text()
    assert "--name=OrdersDS --jndi-name=java:jboss/datasources/OrdersDS" in ds
    assert "jdbc:postgresql://db:5432/orders" in ds
    assert "secret" not in ds                       # passwords never copied

    ely = (tmp_path / written[1]).read_text()
    assert "jdbc-realm=orders-realm" in ely
    assert "SELECT pwd FROM app_user WHERE login=?" in ely
    assert "/subsystem=undertow/application-security-domain=orders:add" in ely
    assert "security-domain=other" not in ely
    assert "TODO(partners)" in ely
    assert manual and "partners" in manual[0]


def test_references_without_standalone(tmp_path):
    write(tmp_path, "src/main/resources/META-INF/persistence.xml",
          "<persistence><persistence-unit name='p'><jta-data-source>java:/OrdersDS</jta-data-source>"
          "</persistence-unit></persistence>")
    written, _ = server_config.run(tmp_path, include_security=False)
    assert written == ["migration/jboss-cli/01-datasources.cli"]
    assert "${env.DB_URL}" in (tmp_path / written[0]).read_text()
