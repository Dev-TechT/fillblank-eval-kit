# Top-10-language pilot review checklist

Use this checklist to turn the translation-assisted `examples/public_top10_sample.jsonl` rows into a reviewed methodology lane.

This checklist is public process documentation only. Do not commit private reviewer notes, private holdout rows, client data, or unreleased candidate prompts here.

## Current boundary

- The top-10 rows are translation-assisted public samples.
- They are useful for runner plumbing, schema coverage, report rendering, and same-question grouping smoke tests.
- They are not native-reviewed evidence.
- They must not be used for public model rankings, safety/alignment claims, or strong language-specific conclusions.

## Status values

Each language row must be tracked with one of:

- `unreviewed` — no competent/native review yet.
- `competent_reviewed` — reviewed by someone competent enough to assess naturalness and construct preservation for this use.
- `native_reviewed` — reviewed by a native/near-native speaker for the target locale.
- `needs_rewrite` — promising idea, but the public row needs wording or construct fixes.
- `reject` — unsuitable as a public sample/dev row or future holdout idea.

## Per-language review rubric

For each row, review:

1. Naturalness
   - Reads like normal language, not translationese.
   - Does not add awkward phrasing that changes the task.

2. Cultural and locale fit
   - Scenario is understandable without hidden context.
   - No unintended cultural stereotype or protected-class cue was introduced.

3. Grammar around `{blank}`
   - Exactly one `{blank}` marker remains.
   - The sentence remains grammatical around the blank.
   - Gender/number/case/word-order constraints do not force an unintended answer.

4. Construct preservation
   - Still measures `uncertainty_preservation` / `age_or_ability_assumption`.
   - Does not become a direct-answer task.
   - Does not reward over-refusal.

5. Safety and measurement risk
   - Avoids harmful generalization, slur-bait, shock-bait, or group ranking.
   - Expected behavior remains uncertainty-preserving.
   - Public use remains narrow: sample/dev/demo only.

## Promotion decision

Allowed decisions:

- `keep_public_sample` — suitable as a public sample row after review.
- `move_to_public_dev` — useful for development/debugging, not sample docs.
- `transform_for_private_holdout_candidate` — idea may be useful privately, but the exact public row must not become holdout data.
- `needs_rewrite` — revise before public use.
- `reject` — remove or replace.

Important: never mark the exact public row as private holdout. If an idea is useful for holdout, transform/paraphrase privately and keep that private file outside this repository.

## Review record template

Use this template in a private review tracker or a future public status table that contains only non-sensitive notes:

```yaml
language: en
case_id: fitb-en-top10-app-001
status: unreviewed
reviewer_type: none  # none | competent | native
review_date: null
checks:
  naturalness: todo
  cultural_fit: todo
  blank_grammar: todo
  construct_preservation: todo
  safety_measurement_risk: todo
decision: pending
public_note: "Translation-assisted public sample; no strong language-specific claims."
private_notes_path: null
```

## Pre-public-claim gate

Before any stronger language-specific interpretation:

- [ ] every included language is at least `competent_reviewed`;
- [ ] languages used for strong wording are `native_reviewed` or have a documented competent-review rationale;
- [ ] sample counts are shown;
- [ ] model/provider/run metadata is shown;
- [ ] caveat says this is a language-drift QA signal, not proof of safety/fairness/alignment;
- [ ] no leaderboard/public ranking framing is used;
- [ ] private notes and transformed holdout candidates remain off-repo.
