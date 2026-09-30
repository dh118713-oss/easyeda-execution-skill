import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class SchemaTests(unittest.TestCase):
    def test_schemas_are_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(load_json(ROOT / "schemas" / "eda-operation-plan.schema.json"))
        Draft202012Validator.check_schema(load_json(ROOT / "schemas" / "eda-readback.schema.json"))

    def test_operation_plan_example(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
        self.assertEqual([], errors, "operation plan should satisfy its schema")

    def test_readback_example(self):
        schema = load_json(ROOT / "schemas" / "eda-readback.schema.json")
        instance = load_json(ROOT / "examples" / "eda-readback.json")
        errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
        self.assertEqual([], errors, "readback should satisfy its schema")

    def test_plan_rejects_unknown_operation(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        instance["operations"][0]["kind"] = "invented_api_call"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_plan_requires_board_and_constraints_revisions(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        del instance["sources"]["board_revision"]
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_readback_requires_design_review(self):
        schema = load_json(ROOT / "schemas" / "eda-readback.schema.json")
        instance = load_json(ROOT / "examples" / "eda-readback.json")
        del instance["design_review"]
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_completed_readback_requires_reopen_operation_and_evidence(self):
        schema = load_json(ROOT / "schemas" / "eda-readback.schema.json")
        instance = load_json(ROOT / "examples" / "eda-readback.json")
        instance["operations"] = [op for op in instance["operations"] if op["kind"] != "close_reopen"]
        instance["evidence"] = [item for item in instance["evidence"] if item["kind"] != "reopen"]
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_advanced_scope_rejects_write_operation(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        instance["scope"] = "advanced_manual_review"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_intermediate_requires_human_review_gate(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        instance["scope"] = "intermediate"
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_intermediate_accepts_human_review_record(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        instance["scope"] = "intermediate"
        instance["options"]["allow_intermediate_with_human_review"] = True
        instance["approval"]["manual_review_id"] = "review-001"
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(instance)))

    def test_unapproved_plan_rejects_checks_and_mutation(self):
        schema = load_json(ROOT / "schemas" / "eda-operation-plan.schema.json")
        instance = load_json(ROOT / "examples" / "eda-operation-plan.json")
        instance["approval"]["approved"] = False
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(instance)))


if __name__ == "__main__":
    unittest.main()
