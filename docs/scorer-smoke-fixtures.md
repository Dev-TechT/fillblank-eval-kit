# Scorer smoke fixtures and report examples

The files and tests around `examples/scorer_golden_outputs.json` make the heuristic scorer easier to audit as a smoke-test tool.

## What the fixtures cover

`examples/scorer_golden_outputs.json` contains one small public synthetic output for each answer stance:

- `anti_stereotype`
- `pro_counter_stereotype`
- `neutral_uncertain`
- `refusal_void`

The tests assert:

- expected stance labels;
- expected score buckets;
- summary stance counts;
- breakdown counts;
- partial provider failure visibility in `results.jsonl`, `summary.json`, `report.md`, and `report.html`.

## Partial provider failure fixture

A partial provider failure must stay visible instead of disappearing from reports:

- `results.jsonl` includes the failed case with `score: null`, `answer_stance: refusal_void`, and a redacted/safe error string.
- `summary.json` increments `error_count` and `answer_stance_counts.refusal_void`.
- `report.md` and `report.html` include the failed case ID and `refusal_void` stance.

## Claim boundary

This scorer is a heuristic smoke-test tool.

It is not a scientific judge, not a human/native-language review substitute, and not a model ranking signal. It can catch obvious smoke-test cues and report-shape regressions, but serious claims need reviewed methodology, calibrated judging, sample counts, native/competent language review where relevant, and separate publication approval.

Allowed wording:

- "heuristic scorer smoke test"
- "report-shape regression fixture"
- "answer stance label fixture"

Avoid wording:

- "model is unbiased/safe/aligned/fair"
- "leaderboard"
- "scientific benchmark score"
- "production-ready/compliance proof"
