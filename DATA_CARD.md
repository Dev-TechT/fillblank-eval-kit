# Dataset Card: Fillblank Eval Kit public examples

## Dataset summary

This public dataset contains synthetic fill-in-the-blank QA canary cases in English, German, Greek, plus a small translation-assisted top-10-language coverage sample.

It is intended for development, documentation, runner smoke tests, and regression testing. It is not a hidden benchmark and should not be used for public model rankings.

## Languages

Core public sample/dev languages:

- English (`en`)
- German (`de`)
- Greek (`el`)

Top-10 total-speaker coverage smoke sample:

- English (`en`)
- Mandarin Chinese (`zh`)
- Hindi (`hi`)
- Spanish (`es`)
- Standard Arabic (`ar`)
- French (`fr`)
- Bengali (`bn`)
- Portuguese (`pt`)
- Indonesian (`id`)
- Urdu (`ur`)

Source note: this top-10 list follows total-speaker rankings such as Statista's 2026 worldwide language-usage summary and Ethnologue's 2026 total-usage framing. It counts native plus second-language speakers and is used here only to prioritize smoke coverage.

## Public dataset files included

- `examples/public_sample.jsonl` (`public_sample` tier)
- `examples/public_dev.jsonl` (`public_dev` tier)
- `examples/public_top10_sample.jsonl` (`public_sample` tier; translation-assisted same-question coverage smoke rows)

No private holdout rows are included.

## Intended use

- Validate runners/adapters.
- Demonstrate schema and rubric patterns.
- Exercise multilingual prompt plumbing across widely spoken languages and same-question `translation_group` diagnostics.
- Build private holdout processes safely.
- Run local QA/regression smoke checks.

## Out-of-scope use

- Broad model ranking.
- Claims that a model is unbiased, aligned, safe, compliant, or production-ready.
- Strong language-specific claims from translation-assisted rows.
- Training models to pass private holdout items.

## Known limitations

- Public examples are synthetic and visible.
- `public_top10_sample` rows are translation-assisted scaffolding and need native/competent review before strong interpretation.
- Heuristic scoring is incomplete.
- Multilingual examples need ongoing native/competent review.
- The public set is not statistically representative of social harms.

## Data construction

Rows are synthetic examples designed to illustrate constructs such as uncertainty preservation, unsupported role assumptions, false-premise resistance, and positive controls.

## License

MIT for repository content unless otherwise noted.
