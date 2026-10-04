from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from Executors.common import ExecutionReport

from .config import SearchConfig
from .parsing import ThoughtProposal, extract_code
from .policies import select_child
from .reward import compute_reward
from .tree import CandidateRecord, SearchNode


@dataclass(frozen=True)
class ProblemContext:
    dataset: str
    split: str
    problem_id: str
    statement: str
    starter_code: str = ""
    entry_point: str | None = None
    public_test_count: int = 0
    private_test_indices: tuple[int, ...] = ()
    total_test_count: int = 0
    public_tests: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "split": self.split,
            "problem_id": self.problem_id,
            "entry_point": self.entry_point,
            "public_test_count": self.public_test_count,
            "private_test_count": len(self.private_test_indices),
            "total_test_count": self.total_test_count,
            "public_policy": "given_tests" if self.dataset == "humaneval" else "half_or_configured_count",
            "metadata": self.metadata,
        }


class SearchLLM(Protocol):
    def expand_thoughts(self, context: ProblemContext, node: SearchNode, width: int) -> list[ThoughtProposal]: ...

    def generate_code(self, context: ProblemContext, node: SearchNode) -> Any: ...

    def self_evaluate(self, context: ProblemContext, node: SearchNode, code: str) -> float: ...

    def analyze_feedback(
        self,
        context: ProblemContext,
        node: SearchNode,
        code: str,
        failed_test: str,
        trace_text: str,
    ) -> str: ...

    def rethink(
        self,
        context: ProblemContext,
        node: SearchNode,
        code: str,
        feedback: str,
    ) -> Any: ...


class SearchExecutor(Protocol):
    def evaluate_public(self, context: ProblemContext, code: str) -> ExecutionReport: ...

    def evaluate_private(self, context: ProblemContext, code: str) -> ExecutionReport: ...

    def trace_failure(self, context: ProblemContext, code: str, failed_test_index: int) -> str: ...


@dataclass(frozen=True)
class SearchResult:
    context: ProblemContext
    root: SearchNode
    candidates: list[CandidateRecord]
    best_candidate: CandidateRecord | None
    private_evaluation: dict[str, Any] | None

    def to_summary(self, config: SearchConfig, request_count: int, token_usage: dict[str, int]) -> dict[str, Any]:
        best = self.best_candidate
        return {
            "run_name": config.run_name,
            "model": config.model,
            "dataset": self.context.dataset,
            "problem_id": self.context.problem_id,
            "config": {
                "rollouts": config.rollouts,
                "width": config.width,
                "c_base": config.c_base,
                "exploration_weight": config.exploration_weight,
                "reward_a": config.reward_a,
                "reward_b": config.reward_b,
                "seed": config.seed,
                "public_cases_type": config.public_cases_type,
                "max_rethink_times": config.max_rethink_times,
            },
            "problem": self.context.to_dict(),
            "candidate_count": len(self.candidates),
            "request_count": request_count,
            "token_usage": token_usage,
            "rethink_count": sum(candidate.status == "rethink" for candidate in self.candidates),
            "best_candidate_id": best.candidate_id if best else None,
            "best_reward": best.reward if best else None,
            "private_evaluation": self.private_evaluation,
        }


class SearchEngine:
    def __init__(
        self,
        context: ProblemContext,
        llm: SearchLLM,
        executor: SearchExecutor,
        config: SearchConfig,
        *,
        on_event: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        config.validate()
        self.context = context
        self.llm = llm
        self.executor = executor
        self.config = config
        self.on_event = on_event or (lambda event: None)
        self._candidate_number = 0
        self.candidates: list[CandidateRecord] = []
        self.rng = random.Random(config.seed)

    def _event(self, kind: str, **payload: Any) -> None:
        self.on_event({"event": kind, **payload})

    @staticmethod
    def _call_content(value: Any) -> str:
        return str(getattr(value, "content", value))

    def _expand(self, node: SearchNode) -> None:
        proposals = self.llm.expand_thoughts(self.context, node, self.config.width)
        if len(proposals) != self.config.width:
            raise ValueError(f"Expansion returned {len(proposals)} thoughts; expected {self.config.width}")
        node.expansion_count += 1
        for index, proposal in enumerate(proposals):
            child = SearchNode(
                node_id=f"{node.node_id}.{index + 1}.{node.expansion_count}",
                thoughts=[*node.thoughts, proposal.thought],
                parent=node,
                prior=proposal.reasonableness,
                action=proposal.thought,
            )
            node.add_child(child)
        self._event(
            "expand",
            node_id=node.node_id,
            children=[
                {"node_id": child.node_id, "thought": child.action, "prior": child.prior}
                for child in node.children
            ],
        )

    def _failed_test_text(self, report: ExecutionReport) -> tuple[int, str]:
        for test in report.tests:
            if not test.passed:
                return test.index, json.dumps(
                    {
                        "index": test.index,
                        "status": test.status,
                        "expected": test.expected,
                        "actual": test.actual,
                        "error": test.error,
                    },
                    ensure_ascii=False,
                )
        return -1, "No failed test details were returned by the executor."

    def _evaluate(self, node: SearchNode, *, phase: str) -> CandidateRecord:
        raw_code = self.llm.generate_code(self.context, node)
        response_text = self._call_content(raw_code)
        code = extract_code(response_text)
        if not code:
            raise ValueError(f"Code generation returned an empty response for {node.node_id}")
        node.candidate_code = code
        public_report = self.executor.evaluate_public(self.context, code)
        pass_rate = public_report.pass_rate
        llm_score = None
        if pass_rate == 1.0:
            llm_score = self.llm.self_evaluate(self.context, node, code)
        reward = compute_reward(
            pass_rate,
            llm_score,
            a=self.config.reward_a,
            b=self.config.reward_b,
        )
        feedback: dict[str, Any] | None = None
        if pass_rate < 1.0:
            failed_index, failed_text = self._failed_test_text(public_report)
            trace_text = self.executor.trace_failure(self.context, code, failed_index)
            analysis = self.llm.analyze_feedback(
                self.context,
                node,
                code,
                failed_text,
                trace_text,
            )
            feedback = {
                "failed_test_index": failed_index,
                "failed_test": failed_text,
                "trace": trace_text,
                "analysis": analysis,
            }
            node.feedback = feedback
        else:
            node.feedback = None
        self._candidate_number += 1
        candidate = CandidateRecord(
            candidate_id=f"candidate_{self._candidate_number:04d}",
            node_id=node.node_id,
            code=code,
            public_passed_tests=public_report.passed_tests,
            public_total_tests=public_report.total_tests,
            public_pass_rate=pass_rate,
            llm_score=llm_score,
            reward=reward,
            status=phase,
            feedback=feedback,
            request_ids=[
                request_id
                for request_id in [getattr(raw_code, "request_id", None)]
                if request_id
            ],
            response_text=response_text,
            execution=public_report.to_dict(),
            thoughts=tuple(node.thoughts),
        )
        self.candidates.append(candidate)
        node.backpropagate(reward)
        self._event(
            "evaluate",
            phase=phase,
            candidate_id=candidate.candidate_id,
            node_id=node.node_id,
            public_pass_rate=pass_rate,
            llm_score=llm_score,
            reward=reward,
        )
        return candidate

    def _rethink(self, node: SearchNode, candidate: CandidateRecord) -> CandidateRecord | None:
        if candidate.public_pass_rate >= 1.0 or node.rethink_count >= self.config.max_rethink_times:
            return None
        feedback_text = json.dumps(candidate.feedback or {}, ensure_ascii=False)
        replacement = self._call_content(
            self.llm.rethink(self.context, node, candidate.code, feedback_text)
        ).strip()
        if not replacement:
            return None
        node.replace_last_thought(replacement, feedback=candidate.feedback)
        self._event("rethink", node_id=node.node_id, replacement=replacement)
        return self._evaluate(node, phase="rethink")

    def run(self) -> SearchResult:
        root = SearchNode(node_id="root")
        for rollout in range(self.config.rollouts):
            node = root
            while node.children:
                node = select_child(
                    node,
                    c_base=self.config.c_base,
                    exploration_weight=self.config.exploration_weight,
                    rng=self.rng,
                )
            self._expand(node)
            node = select_child(
                node,
                c_base=self.config.c_base,
                exploration_weight=self.config.exploration_weight,
                rng=self.rng,
            )
            self._event("select", rollout=rollout, node_id=node.node_id)
            candidate = self._evaluate(node, phase="initial")
            while candidate.public_pass_rate < 1.0 and node.rethink_count < self.config.max_rethink_times:
                refined = self._rethink(node, candidate)
                if refined is None:
                    break
                candidate = refined
            if candidate.public_pass_rate < 1.0 and rollout + 1 < self.config.rollouts:
                self._event("rethink_next", rollout=rollout, node_id=node.node_id)
                self._expand(node)

        best = max(self.candidates, key=lambda item: item.reward, default=None)
        private_evaluation = None
        if best is not None:
            private_evaluation = self.executor.evaluate_private(self.context, best.code).to_dict()
        self._event(
            "complete",
            candidate_count=len(self.candidates),
            best_candidate_id=best.candidate_id if best else None,
            best_reward=best.reward if best else None,
        )
        return SearchResult(
            context=self.context,
            root=root,
            candidates=self.candidates,
            best_candidate=best,
            private_evaluation=private_evaluation,
        )
