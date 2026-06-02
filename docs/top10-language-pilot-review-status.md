# Public top-10-language pilot review status

This public table tracks non-sensitive review status for `examples/public_top10_sample.jsonl`.

Boundary: all rows are currently translation-assisted public samples. They are not native-reviewed evidence and must not be used for public model rankings, safety/alignment claims, fairness claims, or strong language-specific conclusions.

Review checklist: [`docs/top10-language-pilot-review-checklist.md`](top10-language-pilot-review-checklist.md)

Allowed statuses: `unreviewed`, `competent_reviewed`, `native_reviewed`, `needs_rewrite`, `reject`.

| Language | Case ID | Status | Public note | Next action |
| --- | --- | --- | --- | --- |
| English (`en`) | `fitb-en-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Mandarin Chinese (`zh`) | `fitb-zh-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Hindi (`hi`) | `fitb-hi-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Spanish (`es`) | `fitb-es-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Standard Arabic (`ar`) | `fitb-ar-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| French (`fr`) | `fitb-fr-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Bengali (`bn`) | `fitb-bn-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Portuguese (`pt`) | `fitb-pt-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Indonesian (`id`) | `fitb-id-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |
| Urdu (`ur`) | `fitb-ur-top10-app-001` | `unreviewed` | Translation-assisted public sample; no strong language-specific claims. | Competent/native review for naturalness, blank grammar, and construct preservation. |

## Decision boundary

The current default decision for every row is `pending`. A row should only move out of `unreviewed` after review using the checklist. If a row becomes a private holdout candidate, transform/paraphrase it privately and keep the private candidate outside this repository.
