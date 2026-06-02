# Data Tiers

The project uses explicit data tiers to keep public collaboration useful without destroying private evaluation value.

## Public tiers

### `public_sample`

Small, readable examples for documentation and smoke tests.

Dataset files currently using this tier:

- `examples/public_sample.jsonl`: core English/German/Greek examples.
- `examples/public_top10_sample.jsonl`: one translation-assisted smoke row per top-10 total-speaker language; all rows share `translation_group: top10-app-001` so maintainers can compare the same underlying question across languages. Use for multilingual plumbing/diagnostic coverage only, not native-reviewed language claims.

Use for:

- README examples;
- CLI demos;
- tests;
- tutorials.

Do not use for official model claims.

### `public_dev`

A larger public development set.

Use for:

- community testing;
- contribution review;
- checking runner compatibility;
- debugging scoring behavior.

Do not use as a hidden benchmark. Models and prompt authors can see it.

## Private tiers

### `private_holdout`

Hidden cases for internal or official evaluation.

Rules:

- never commit to public repo;
- never include in public package/wheel/Docker image;
- never publish to Hugging Face dataset viewer;
- never expose through public Spaces logs;
- never return per-sample public feedback.

### `quarantine_candidates`

New candidate items from drafts or public PRs.

Rules:

- review for provenance, safety, duplicate/near-duplicate status, construct clarity, and language quality;
- transform/paraphrase before possible future holdout use;
- do not reveal which candidates enter private holdout.

### `retired_holdout`

Old holdout cases no longer used for official scoring.

Retire cases when:

- leaked;
- overfit/gamed;
- methodology changed;
- quality review finds ambiguity or cultural/language issues.

`quarantine_candidates` and `retired_holdout` are named in the public schema so maintainers can validate private/off-repo files with `--allow-private`, but actual rows in those tiers must stay outside the public repository.

## Public contribution rule

Public PRs may propose sample/dev examples or candidate ideas. They do not directly become private holdout cases.

Maintainers decide privately whether any idea should be transformed into future holdout data.
