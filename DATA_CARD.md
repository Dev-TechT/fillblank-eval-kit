# Dataset Card: Multilingual Bias Drift Benchmark public examples

## Dataset summary

This public dataset contains synthetic fill-in-the-blank QA cases in English, German, Greek, plus a small translation-assisted 10-language pilot sample.

It is intended for development, documentation, runner smoke tests, and regression testing of language-driven answer drift. It is not a hidden benchmark and should not be used for public model rankings.

## What the data is for

The dataset groups equivalent prompts with `translation_group` so the same model can be tested across language versions of the same underlying question.

The target signal is answer-stance drift, for example:

- anti/stereotype in English;
- pro/counter-stereotype in Spanish;
- neutral/uncertain in German;
- refusal/void in another language.

## Languages

Core public sample/dev languages:

- English (`en`)
- German (`de`)
- Greek (`el`)

10-language pilot sample:

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

Source note: this top-10 list follows total-speaker rankings such as Statista's 2026 worldwide language-usage summary and Ethnologue's 2026 total-usage framing. It counts native plus second-language speakers and is used here only to prioritize pilot coverage.

## Public dataset files included

- `examples/public_sample.jsonl` (`public_sample` tier)
- `examples/public_dev.jsonl` (`public_dev` tier)
- `examples/public_top10_sample.jsonl` (`public_sample` tier; translation-assisted same-question pilot rows)

No private holdout rows are included.

## Intended use

- Validate runners/adapters.
- Demonstrate schema and rubric patterns.
- Exercise multilingual prompt plumbing across widely spoken languages.
- Compare same-question `translation_group` rows for drift diagnostics.
- Build private holdout processes safely.
- Run local QA/regression smoke checks.

## Out-of-scope use

- Broad model ranking.
- Claims that a model is biased, unbiased, aligned, safe, compliant, fair, or production-ready.
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
