# Demo that the bench exists to enable

This is the four-minute room. The harness should make it cheap to record, not a one-off notebook.

1. **Spec → geometry.** Type a target pattern or an S-mask. Geometry appears in < 1 s.
2. **Live fields.** E (and H) on a cut plane, interactive. Drag a trace, fields update.
3. **Verify.** Public solver overlay. Live or cached with the recipe hash visible.
4. **ε plot.** Active-learn curve vs random / Sobol / expert grid, same solver budget, `exam` on the y-axis.
5. **Object (optional, lethal).** One fabricated coupon next to the prediction.

Do not lead with an agent slideshow. Do not lead with a commercial-solver multiplier. Do not call it superintelligence on slide one. The three claims in SPEC.md *are* the sentence.

## What this repo will ship to support that

- `scripts/evaluate.py` — frozen metrics on a prediction directory.
- `scripts/active_learn.py` — budget-matched curves, required baselines.
- `scripts/generate_corpus.py` — factory entry point.
- A viewer is out of scope for v0.1 of the harness; fields are written as arrays a notebook can plot.

## Protocol reminder

Compare to Meep / openEMS first. One HFSS appendix on a named public board, project file included, or do not mention HFSS.
