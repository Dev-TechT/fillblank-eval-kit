## Summary

## Type of change

- [ ] Documentation
- [ ] Validator/scorer code
- [ ] Public sample/dev data
- [ ] Adapter/tooling
- [ ] Other

## Benchmark/data checklist

- [ ] No private holdout rows, prompts, answer keys, model outputs, or logs are included.
- [ ] Any new case has exactly one `{blank}` marker.
- [ ] Any new case names one primary construct.
- [ ] Any new case includes provenance/license/review notes.
- [ ] Public claims remain narrow: no model-safety, alignment, or unbiasedness proof claims.

## Verification

Paste commands and results:

```bash
uv run --with pytest python -m pytest -q
uv run python -m fillblank_eval.validator examples/public_sample.jsonl examples/public_dev.jsonl
uv run python -m fillblank_eval.leak_scan .
```
