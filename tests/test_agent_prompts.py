from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "src" / "trustroom" / "agents" / "prompts"
ENVELOPE_DOC = ROOT / "docs" / "agent-task-envelopes.md"
EXPECTED_PROMPTS = {
    "orchestrator.md",
    "requirement_decomposer.md",
    "evidence_retriever.md",
    "answer_drafter.md",
    "compliance_reviewer.md",
    "workflow_improvement.md",
    "challenge_generator.md",
}
REQUIRED_SECTIONS = [
    "## Role",
    "## Enterprise Job",
    "## Input Contract",
    "## Output JSON Schema",
    "## Refusal / No-Overclaim Boundary",
    "## Band Handoff Instruction",
]
HANDOFF_TERMS = ["@mention", "handoff", "evidence", "human approval", "request_changes"]
FORBIDDEN_PROMISE_TERMS = [
    "production deployment",
    "legal advice",
    "certification",
    "fully compliant",
]


def prompt_files() -> list[Path]:
    return sorted(PROMPT_DIR.glob("*.md"))


def test_expected_agent_prompt_files_exist() -> None:
    assert {path.name for path in prompt_files()} == EXPECTED_PROMPTS


def test_each_prompt_has_required_contract_sections_and_handoff_terms() -> None:
    for path in prompt_files():
        text = path.read_text(encoding="utf-8")

        for section in REQUIRED_SECTIONS:
            assert section in text, f"{path.name} missing {section}"
        for term in HANDOFF_TERMS:
            assert term in text, f"{path.name} missing {term}"


def test_prompts_mark_overclaim_terms_as_forbidden_not_promised() -> None:
    for path in prompt_files():
        text = path.read_text(encoding="utf-8").lower()

        assert "forbidden claims" in text
        for term in FORBIDDEN_PROMISE_TERMS:
            assert term in text, f"{path.name} missing forbidden term {term}"


def test_task_envelope_doc_preserves_mode_and_safety_boundaries() -> None:
    text = ENVELOPE_DOC.read_text(encoding="utf-8").lower()

    for term in ["task_id", "run_id", "sender", "receiver", "task_state", "mode"]:
        assert term in text
    for term in ["replay", "human approval", "request_changes", "@mention"]:
        assert term in text
    for term in FORBIDDEN_PROMISE_TERMS:
        assert term in text
