# detect_fixtures_plugin.py
import json
import os

collected = []
deselected = set()


def pytest_collection_finish(session):
    """Called after all collection and filtering (e.g. -k) is complete."""
    collected = []
    for item in session.items:
        collected.append(
            {
                "nodeid": item.nodeid,
                "fixtures": item.fixturenames,
            }
        )

    out = os.getenv("FIXTURE_REPORT_PATH", "fixture_report.json")
    with open(out, "w") as f:
        json.dump(collected, f)
