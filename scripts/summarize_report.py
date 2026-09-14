import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def main() -> None:
    xml_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests-report.xml")

    root = ET.parse(xml_file).getroot()

    # pytest generates:
    #
    # <testsuites>
    #   <testsuite ...>
    #     <testcase ... />
    #   </testsuite>
    # </testsuites>
    #
    # Aggregate all testsuites rather than reading attributes from
    # the <testsuites> wrapper.

    suites = list(root.iter("testsuite"))

    tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)
    duration = sum(float(suite.attrib.get("time", 0)) for suite in suites)

    passed = tests - failures - errors - skipped

    if failures == 0 and errors == 0:
        status = "✅ Passed"
    else:
        status = "❌ Failed"

    # Overall Results (table)
    print(f"# Pytest Results {status}")
    print()

    print("| Metric | Count |")
    print("|---|---:|")
    print(f"| Total | {tests} |")
    print(f"| ✅ Passed | {passed} |")
    print(f"| ❌ Failed | {failures} |")
    print(f"| 💥 Errors | {errors} |")
    print(f"| ⏭️ Skipped | {skipped} |")
    print(f"| ⏱️ Duration | {duration:.3f}s |")
    print()

    # Test Details (Table)
    print("## Test Details")
    print()

    print("| Test | Result | Duration |")
    print("|---|---|---:|")

    for suite in suites:
        for case in suite.findall("testcase"):
            name = case.attrib.get("name", "")
            classname = case.attrib.get("classname", "")
            case_time = float(case.attrib.get("time", 0))

            failure = case.find("failure")
            error = case.find("error")
            skipped_node = case.find("skipped")

            if failure is not None:
                result = "❌ Failed"
            elif error is not None:
                result = "💥 Error"
            elif skipped_node is not None:
                result = "⏭️ Skipped"
            else:
                result = "✅ Passed"

            test_name = f"`{classname}.{name}`" if classname else f"`{name}`"

            print(f"| {test_name} | {result} | {case_time:.3f}s |")

            # Failure/error details
            node = failure if failure is not None else error

            if node is not None:
                message = node.attrib.get("message", "Unknown error")
                details = node.text or ""

                print()
                print("<details>")
                print(f"<summary>❌ {name} failure details</summary>")
                print()
                print("```text")
                print(message)

                if details.strip():
                    print(details)

                print("```")
                print()
                print("</details>")
                print()


if __name__ == "__main__":
    main()
