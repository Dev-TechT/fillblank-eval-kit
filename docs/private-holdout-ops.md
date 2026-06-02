# Private holdout operations guide

This guide is for maintainers. Do not put actual private rows in this public repo.

## Suggested private directory

```text
private/
  private_holdout.jsonl
  private_answer_key_or_rubrics.jsonl
  private_qa_reports/
  quarantine_candidates/
  retired_holdout/
```

The public `.gitignore` blocks these paths.

## Holdout growth target

For credible private use, aim higher than 30 cases:

- v0.2 private: 60 reviewed cases.
- v0.3 private: 150 reviewed cases.
- v1.0 private: 300+ reviewed cases, with enough per-language/per-construct counts to report meaningful aggregates.

Public examples can be numerous, but official comparisons should use private holdout plus clear methodology.

## Review requirements

Every private case needs:

- construct clarity;
- language quality review;
- provenance/license note;
- duplicate/near-duplicate check with `fillblank_eval.duplicates`;
- safety review;
- positive/negative control balance.

## Rotation

Retire or transform cases that leak, become overfit, or receive methodology objections.

See also: `docs/private-holdout-review-checklist.md` for the detailed promotion checklist.
