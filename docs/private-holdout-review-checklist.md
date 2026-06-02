# Private holdout review checklist

Use this checklist for maintainers reviewing private/off-repo `quarantine_candidates` before they become `private_holdout` rows.

Do not copy actual private rows into public issues, PRs, screenshots, logs, or docs.

## 1. Intake

For every candidate, verify:

- [ ] Synthetic or properly licensed/provenance-cleared source.
- [ ] No client, personal, scraped-sensitive, or secret data.
- [ ] Exactly one primary construct.
- [ ] Exactly one `{blank}` marker.
- [ ] Language is tagged correctly.
- [ ] Protected classes list is explicit, even when empty.
- [ ] `scoring.no_single_correct_answer=true`.
- [ ] Expected behavior describes behavior, not one rigid answer.

## 2. Duplicate and contamination review

Run locally/off-repo:

```bash
uv run python -m fillblank_eval.duplicates --allow-private /path/to/quarantine_candidates.jsonl
```

Review:

- [ ] Duplicate IDs: must be fixed.
- [ ] Exact normalized prompt duplicates: must be fixed or intentionally retired.
- [ ] Near-duplicate warnings: review as a family; avoid over-weighting one template.
- [ ] Public sample/dev overlap: transform or reject if too similar.
- [ ] Known public benchmark overlap: document or reject if it copies existing benchmark items.

## 3. Language and culture review

For each language/locale:

- [ ] Native or competent language review done.
- [ ] Prompt is natural and not translationese where that matters.
- [ ] Cultural reference is understandable without extra hidden context.
- [ ] No slur-bait, shock-bait, or protected-group ranking prompt.
- [ ] Greek/German examples preserve grammar around `{blank}`.

## 4. Safety and measurement review

- [ ] The case measures one named behavior.
- [ ] It does not reward over-refusal unless that is the explicit construct.
- [ ] It has a plausible good answer and plausible bad failure mode.
- [ ] Rubric distinguishes harmful assumption, weak hedge, good uncertainty preservation, and strong helpful framing.
- [ ] Positive/negative/contrast controls remain balanced across language and construct.

## 5. Promotion decision

Allowed decisions:

- `accept_public_sample`: safe educational example only.
- `accept_public_dev`: public development/debug row only.
- `transform_for_private_holdout`: idea is useful, but exact public row must not be reused.
- `accept_private_holdout`: reviewed private row, never public.
- `quarantine_more_review`: potentially useful but not ready.
- `reject`: unsafe, duplicative, unclear, or not measuring the intended construct.
- `retire`: leaked, overfit, stale, or methodology changed.

## 6. Private holdout storage

Keep private files outside the public repo, for example:

```text
~/.hermes/private/fillblank-eval-kit/private_holdout.jsonl
~/.hermes/private/fillblank-eval-kit/quarantine_candidates.jsonl
~/.hermes/private/fillblank-eval-kit/retired_holdout.jsonl
```

The public repo may document the process, but not the private rows.

## 7. Before reporting aggregate results

- [ ] Enough rows per language/construct to make the aggregate meaningful.
- [ ] Sample counts printed with every score.
- [ ] Data version, scorer version, runner version recorded.
- [ ] No per-sample private feedback leaked.
- [ ] Claim remains narrow: private QA signal, not alignment/safety/unbiasedness proof.
