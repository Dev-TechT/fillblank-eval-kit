# Dataset Card: Fillblank Eval Kit public examples

## Dataset summary

This public dataset contains synthetic fill-in-the-blank QA canary cases in English, German, and Greek.

It is intended for development, documentation, and regression testing. It is not a hidden benchmark and should not be used for public model rankings.

## Languages

- English (`en`)
- German (`de`)
- Greek (`el`)

## Data tiers included

- `public_sample`
- `public_dev`

No private holdout rows are included.

## Intended use

- Validate runners/adapters.
- Demonstrate schema and rubric patterns.
- Build private holdout processes safely.
- Run local QA/regression smoke checks.

## Out-of-scope use

- Broad model ranking.
- Claims that a model is unbiased, aligned, safe, compliant, or production-ready.
- Training models to pass private holdout items.

## Known limitations

- Public examples are synthetic and visible.
- Heuristic scoring is incomplete.
- Multilingual examples need ongoing native/competent review.
- The public set is not statistically representative of social harms.

## Data construction

Rows are synthetic examples designed to illustrate constructs such as uncertainty preservation, unsupported role assumptions, false-premise resistance, and positive controls.

## License

MIT for repository content unless otherwise noted.
