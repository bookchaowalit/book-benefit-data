import copy
import unittest
from unittest.mock import patch

from book_benefit_data.cli import filter_items, main, resource, validate


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.data = resource("demo.json")

    def test_synthetic_fixture(self):
        self.assertEqual(validate(self.data)["data_status"], "fixture")

    def test_domain_terms_required(self):
        self.data["items"][0]["terms"] = {}
        with self.assertRaises(ValueError): validate(self.data)

    def test_cross_domain_rejected(self):
        self.data["schema_version"] = "unrelated.v1"
        with self.assertRaises(ValueError): validate(self.data)

    def test_duplicate_rejected(self):
        self.data["items"].append(copy.deepcopy(self.data["items"][0]))
        with self.assertRaises(ValueError): validate(self.data)

    def test_fixture_cannot_be_claimed_live(self):
        self.data["data_status"] = "live"
        with self.assertRaises(ValueError): validate(self.data)

    def test_negative_value_rejected(self):
        self.data["items"][0]["value"]["amount"] = -1
        with self.assertRaises(ValueError): validate(self.data)

    def test_amount_requires_currency(self):
        self.data["items"][0]["value"]["amount"] = 100
        with self.assertRaises(ValueError): validate(self.data)

    def test_deadline_timezone_required(self):
        self.data["items"][0]["deadline"]["at"] = "2026-09-08T00:00:00"
        with self.assertRaises(ValueError): validate(self.data)

    def test_unknown_and_closed_not_open(self):
        found = filter_items(self.data, "2026-09-07T00:00:00Z", True)
        self.assertEqual(len(found), 1)

    def test_deadline_boundary_and_stale(self):
        self.assertEqual(filter_items(self.data, "2026-09-08T00:00:00Z", True), [])
        self.data["items"][0]["deadline"] = {"kind":"rolling", "at":None}
        self.assertEqual(filter_items(self.data, "2026-09-12T00:00:00Z", True), [])

    def test_future_check_not_open(self):
        self.assertEqual(filter_items(self.data, "2026-09-06T00:00:00Z", True), [])

    def test_secret_url_rejected(self):
        self.data["items"][0]["source_url"] = "https://example.org/claim?token=synthetic"
        with self.assertRaises(ValueError): validate(self.data)

    def test_search(self):
        self.assertEqual(filter_items(self.data, "2026-09-07T00:00:00Z", query="not-a-match"), [])

    def test_demo_never_uses_network(self):
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), patch("builtins.print"):
            self.assertEqual(main(["demo", "--open-only"]), 0)


class DemoV2Tests(unittest.TestCase):
    def ids(self, as_of, max_age_hours=72):
        payload = resource("demo-v2.json")
        return [item["id"] for item in filter_items(payload, as_of, open_only=True, max_age_hours=max_age_hours)]

    def test_v2_demo_is_a_valid_v2_fixture(self):
        payload = validate(resource("demo-v2.json"))
        self.assertEqual((payload["schema_version"], payload["data_status"]), ("benefit.v2", "fixture"))
        kinds = {item["availability"]["kind"] for item in payload["items"]}
        self.assertEqual(kinds, {"continuous", "scheduled", "fixed_window", "unknown"})

    def test_open_only_follows_availability_windows(self):
        self.assertEqual(self.ids("2026-09-07T00:00:00Z"), ["benefit-v2-demo-continuous"])

    def test_scheduled_start_is_an_instant_not_a_local_date(self):
        # starts_at 2026-10-01T00:00+07:00 is 2026-09-30T17:00Z.
        cases = {
            "2026-09-30T16:59:59Z": ["benefit-v2-demo-continuous"],
            "2026-09-30T17:00:00Z": ["benefit-v2-demo-continuous", "benefit-v2-demo-scheduled"],
            "2026-09-30T23:59:59+07:00": ["benefit-v2-demo-continuous"],
            "2026-10-01T00:00:00+07:00": ["benefit-v2-demo-continuous", "benefit-v2-demo-scheduled"],
            "2026-09-30T13:00:00-04:00": ["benefit-v2-demo-continuous", "benefit-v2-demo-scheduled"],
        }
        for as_of, expected in cases.items():
            with self.subTest(as_of=as_of):
                self.assertEqual(self.ids(as_of, max_age_hours=24 * 60), expected)

    def test_cli_demo_version_flag(self):
        with patch("sys.stdout") as out:
            self.assertEqual(main(["demo", "--version", "v2", "--open-only"]), 0)
        printed = "".join(call.args[0] for call in out.write.call_args_list)
        self.assertIn("benefit-v2-demo-continuous", printed)
        self.assertNotIn("benefit-v2-demo-ended", printed)
        with patch("sys.stdout"), patch("sys.stderr"), self.assertRaises(SystemExit):
            main(["demo", "--version", "v3"])


if __name__ == "__main__": unittest.main()
