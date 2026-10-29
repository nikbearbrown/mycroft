from migrator.verify import test_compare
from tests.conftest import write

JUNIT4 = """<testsuite name="com.x.OrderTest" tests="3">
  <testcase classname="com.x.OrderTest" name="total"/>
  <testcase classname="com.x.OrderTest" name="discount"><failure message="boom"/></testcase>
  <testcase classname="com.x.OrderTest" name="tax"/>
</testsuite>"""

JUNIT5 = """<testsuite name="com.x.OrderTest" tests="3">
  <testcase classname="com.x.OrderTest" name="total()"><failure message="regressed"/></testcase>
  <testcase classname="com.x.OrderTest" name="discount()"/>
  <testcase classname="com.x.OrderTest" name="refund()"/>
</testsuite>"""


def test_parse_and_compare(tmp_path):
    write(tmp_path, "before/TEST-com.x.OrderTest.xml", JUNIT4)
    write(tmp_path, "after/TEST-com.x.OrderTest.xml", JUNIT5)
    before = test_compare.parse_reports([tmp_path / "before"])
    after = test_compare.parse_reports([tmp_path / "after"])
    assert before["com.x.OrderTest#discount"] == test_compare.FAILED

    c = test_compare.compare(before, after)
    assert c.regressions == ["com.x.OrderTest#total"]
    assert c.fixed == ["com.x.OrderTest#discount"]
    assert c.missing == ["com.x.OrderTest#tax"]
    assert c.new == ["com.x.OrderTest#refund"]
    assert not c.ok
