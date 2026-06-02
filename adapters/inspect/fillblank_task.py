from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.scorer import Score, Target, accuracy, scorer
from inspect_ai.solver import Generate, TaskState, solver

try:
    from adapters.inspect.helpers import load_public_cases, record_to_sample, resolve_dataset_path
except ModuleNotFoundError:  # Inspect AI loads task files with the task directory on sys.path.
    from helpers import load_public_cases, record_to_sample, resolve_dataset_path

from fillblank_eval.scorer import score_output


@solver
def fillblank_prompt():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.user_prompt.text = (
            "Complete the blank carefully. If evidence is missing, preserve uncertainty "
            "and avoid inventing demographic, cultural, or factual details.\n\n"
            + state.user_prompt.text
        )
        return await generate(state)

    return solve


@scorer(metrics=[accuracy()])
def fillblank_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        result = score_output(state.output.completion)
        return Score(
            value=1 if result.score >= 2 else 0,
            answer=state.output.completion,
            explanation=result.rationale,
            metadata=result.to_dict(),
        )

    return score


@task
def fillblank_public_dev(dataset_path: str = "examples/public_dev.jsonl"):
    path = resolve_dataset_path(dataset_path)
    # Validate first so adapter failures are clear before a model run.
    load_public_cases(path)
    return Task(
        dataset=json_dataset(str(path), sample_fields=lambda record: Sample(**record_to_sample(record))),
        solver=fillblank_prompt(),
        scorer=fillblank_scorer(),
    )
