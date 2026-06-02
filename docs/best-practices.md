# Best practices for fill-in-the-blank QA canary benchmarks

1. Name the construct before writing the prompt.
2. Keep one `{blank}` marker per case.
3. Include positive controls so models are not rewarded for refusing everything.
4. Avoid shockbait and ranking protected groups.
5. Treat public examples as training-visible.
6. Keep private holdout rows out of git history, packages, logs, Spaces, and CI artifacts.
7. Do not use one judge model as the only official scorer.
8. Report sample counts with every aggregate.
9. Separate data version, scorer version, and runner version.
10. Make public claims narrow and caveated.

Safe public wording:

> A small open-source kit for building and validating fill-in-the-blank QA canaries around unsupported assumptions, harmful generalization, and uncertainty preservation.

Unsafe wording:

> This benchmark proves which AI is unbiased or aligned.
