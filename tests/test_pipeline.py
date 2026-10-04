from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evaluation.batch_evaluation import discover_candidates, main as evaluate_main
from pipelines.direct_baseline import main as pipeline_main


HUMANEVAL_ZERO_SOLUTION = '''def has_close_elements(numbers, threshold):
    for index, left in enumerate(numbers):
        for right in numbers[index + 1:]:
            if abs(left - right) < threshold:
                return True
    return False
'''


def write_candidate(
    output_dir: Path,
    *,
    timestamp: str,
    created_at: str,
    model: str = "org/model",
    code: str = HUMANEVAL_ZERO_SOLUTION,
) -> Path:
    artifact = (
        output_dir
        / "direct_generation"
        / "pipeline_test"
        / "response_model"
        / "humaneval"
        / f"HumanEval_0_{timestamp}"
    )
    artifact.mkdir(parents=True)
    (artifact / "solution.py").write_text(code, encoding="utf-8")
    (artifact / "metadata.json").write_text(
        json.dumps(
            {
                "created_at": created_at,
                "requested_model": model,
                "problem": {
                    "dataset": "humaneval",
                    "problem_id": "HumanEval/0",
                    "split": "test",
                },
            }
        ),
        encoding="utf-8",
    )
    return artifact


class EvaluationPipelineTests(unittest.TestCase):
    def test_discovery_uses_latest_candidate_per_problem(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_candidate(
                output_dir, timestamp="old", created_at="2026-01-01T00:00:00Z"
            )
            latest = write_candidate(
                output_dir, timestamp="new", created_at="2026-01-02T00:00:00Z"
            )

            candidates = discover_candidates(
                output_dir=output_dir,
                run_name="pipeline_test",
                dataset="humaneval",
                model="org/model",
                split="test",
            )

            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0].artifact_dir, latest)

    def test_parallel_evaluation_writes_candidate_and_aggregate_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            artifact = write_candidate(
                output_dir, timestamp="one", created_at="2026-01-01T00:00:00Z"
            )

            status = evaluate_main(
                [
                    "--run-name",
                    "pipeline_test",
                    "--model",
                    "org/model",
                    "--output-dir",
                    str(output_dir),
                    "--workers",
                    "2",
                ],
                dataset="humaneval",
            )

            summary_path = (
                output_dir
                / "evaluations"
                / "pipeline_test"
                / "org_model"
                / "humaneval"
                / "summary.json"
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(status, 0)
            self.assertTrue((artifact / "evaluation.json").is_file())
            self.assertEqual(summary["fully_passed"], 1)
            self.assertEqual(summary["evaluation_config"]["test_policy"], "official_harness")
            self.assertEqual(summary["evaluation_config"]["timeout_seconds"], 5.0)
            self.assertEqual(summary["pass_at_1"], 1.0)
            self.assertTrue((summary_path.parent / "results.csv").is_file())
            self.assertTrue((summary_path.parent / "results.jsonl").is_file())

    def test_parallel_apps_evaluation_reports_partial_test_counts(self) -> None:
        code = '''s = input()
left_bracket = s.find('[')
left_colon = s.find(':', left_bracket + 1) if left_bracket >= 0 else -1
right_bracket = s.rfind(']')
right_colon = s.rfind(':', 0, right_bracket) if right_bracket >= 0 else -1
if left_colon < 0 or right_colon <= left_colon:
    print(-1)
else:
    print(4 + s[left_colon + 1:right_colon].count('|'))
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            artifact = (
                output_dir
                / "direct_generation"
                / "apps_pipeline_test"
                / "response_model"
                / "apps"
                / "0000_timestamp"
            )
            artifact.mkdir(parents=True)
            (artifact / "solution.py").write_text(code, encoding="utf-8")
            (artifact / "metadata.json").write_text(
                json.dumps(
                    {
                        "created_at": "2026-01-01T00:00:00Z",
                        "requested_model": "org/model",
                        "problem": {
                            "dataset": "apps",
                            "problem_id": "0000",
                            "split": "test",
                        },
                    }
                ),
                encoding="utf-8",
            )

            status = evaluate_main(
                [
                    "--run-name",
                    "apps_pipeline_test",
                    "--model",
                    "org/model",
                    "--output-dir",
                    str(output_dir),
                    "--workers",
                    "2",
                    "--max-tests",
                    "3",
                ],
                dataset="apps",
            )

            report = json.loads(
                (artifact / "evaluation.json").read_text(encoding="utf-8")
            )
            self.assertEqual(status, 0)
            self.assertEqual(report["passed_tests"], 3)
            self.assertEqual(report["total_tests"], 3)

    def test_failure_logs_identify_problem_and_failed_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_candidate(
                output_dir,
                timestamp="wrong",
                created_at="2026-01-01T00:00:00Z",
                code="def has_close_elements(numbers, threshold):\n    return False\n",
            )

            status = evaluate_main(
                [
                    "--run-name",
                    "pipeline_test",
                    "--model",
                    "org/model",
                    "--output-dir",
                    str(output_dir),
                    "--workers",
                    "2",
                ],
                dataset="humaneval",
            )

            aggregate = (
                output_dir
                / "evaluations"
                / "pipeline_test"
                / "org_model"
                / "humaneval"
            )
            failure = json.loads(
                (aggregate / "failures.jsonl").read_text(encoding="utf-8").strip()
            )
            summary = json.loads((aggregate / "summary.json").read_text(encoding="utf-8"))
            log = (aggregate / "evaluation.log").read_text(encoding="utf-8")
            self.assertEqual(status, 0)
            self.assertEqual(failure["problem_id"], "HumanEval/0")
            self.assertEqual(failure["passed_tests"], 0)
            self.assertEqual(failure["failed_test_indices"], [0])
            self.assertEqual(summary["failed_problem_ids"], ["HumanEval/0"])
            self.assertIn("problem=HumanEval/0", log)
            self.assertIn("passed=0/1", log)

    def test_pipeline_plan_does_not_require_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = pipeline_main(
                [
                    "--stage",
                    "all",
                    "--dataset",
                    "all",
                    "--run-name",
                    "pipeline_plan",
                    "--model",
                    "org/model",
                    "--output-dir",
                    temp_dir,
                    "--limit",
                    "2",
                    "--plan",
                ]
            )

            self.assertEqual(status, 0)

    def test_pipeline_stage_log_records_evaluation_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            status = pipeline_main(
                [
                    "--stage",
                    "evaluate",
                    "--dataset",
                    "humaneval",
                    "--run-name",
                    "pipeline_log_test",
                    "--model",
                    "org/model",
                    "--output-dir",
                    temp_dir,
                    "--workers",
                    "1",
                ]
            )

            log_path = (
                Path(temp_dir)
                / "pipeline_logs"
                / "pipeline_log_test"
                / "org_model"
                / "pipeline.log"
            )
            log = log_path.read_text(encoding="utf-8")
            self.assertEqual(status, 0)
            self.assertIn("EVALUATE_START dataset=humaneval", log)
            self.assertIn("EVALUATE_END dataset=humaneval status=0", log)


if __name__ == "__main__":
    unittest.main()
