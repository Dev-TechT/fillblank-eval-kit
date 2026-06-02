# Multilingual Bias Drift Benchmark roadmap

## v0.1

- Public schema and validator.
- Public sample/dev examples.
- Heuristic scorer for local smoke tests.
- Data-tier and release policies.
- Adapter stubs.
- Basic same-question language grouping through `translation_group`.

## v0.2

- Inspect AI runner with documented command.
- Near-duplicate detector for contributed cases.
- More human-reviewed German and Greek examples.
- More Spanish and top-language pilot examples for same-question drift checks.
- Stronger scorer fixtures and report format.
- First-class stance labels: `anti_stereotype`, `pro_counter_stereotype`, `neutral_uncertain`, `refusal_void`.
- Better drift summaries by `translation_group`, including stance diversity and drift signal.
- More positive controls to avoid over-refusal reward.

## v0.3

- Private holdout governance template.
- Maintainer-only official scoring workflow.
- Optional lm-evaluation-harness task integration.

## Not planned until methodology improves

- Public model leaderboard.
- Claims about model safety/alignment/fairness.
- Claims that a model is biased or unbiased from public sample/dev rows alone.
- Publishing private holdout rows.
