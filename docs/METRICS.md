# Metrics

All formulas are implemented in `maxwellbench.metrics`. If prose and code disagree, code wins and prose gets a PR.

## Forward — S-parameters

Let \(S_{ij}(f)\) be complex. Magnitude-weighted MAE in dB:

\[
\mathrm{wMAE}_{|S|}
= \frac{\sum_f w(f)\, \big| |S_{\mathrm{pred}}(f)|_{\mathrm{dB}} - |S_{\mathrm{gt}}(f)|_{\mathrm{dB}} \big|}
       {\sum_f w(f)}
\]

Default \(w(f)\): 1 on the task band, 0.25 on the guard band, 0 elsewhere. Phase MAE is reported separately, unwrapped per port pair, in degrees. Complex RMSE on real/imag is the third number.

**Pass bar for a serious claim (v0, `exam`, per regime):** \(\mathrm{wMAE}_{|S|} < 1\,\mathrm{dB}\) on the task band.

## Forward — fields

On the evaluation grid \(\Omega\) (task YAML):

\[
\mathrm{nRMSE}(\mathbf{E})
= \frac{\| \mathbf{E}_{\mathrm{pred}} - \mathbf{E}_{\mathrm{gt}} \|_{2,\Omega}}
       {\|\mathbf{E}_{\mathrm{gt}}\|_{2,\Omega} + \varepsilon}
\]

Same for H. Also report magnitude-weighted MAE on \(|\mathbf{E}|\) in dB at probe points listed in the task file (ports, focus, cut-plane maxima).

A model that hits S and fails nRMSE is predicting a network, not Maxwell. Both go on the row.

## Inverse

Task FoM after solver verification (see TASKS). Examples:

- metalens: focusing efficiency at design λ
- mode converter: target-mode transmission
- patch: −10 dB bandwidth and boresight gain
- coupon: |S11| and |S21| mask satisfaction (fraction of band)

Report FoM, number of solver calls, wall-clock, and whether legalization changed more than 5% of pixels (a silent redesign).

## Transfer

Matrix \(M_{src \to tgt}(k)\): nRMSE(E) and wMAE_|S| on the target `exam` after k shots. Headline is the 0-shot and 32-shot cells.

## Active learning

For method m, curve \(e_m(b)\) = `exam` nRMSE(E) after b solver calls.

- **Area over random:** \(\int_0^{B_{\max}} (e_{\mathrm{rand}} - e_m)\, db / B_{\max}\)
- **Calls to bar:** smallest b with \(e_m(b) < e_{\mathrm{bar}}\) (bar pinned in `configs/bench.yaml`)

This is the public stand-in for \(\varepsilon_{R,C}\). If the area over random is ≤ 0, you are not a recursive lab yet.

## Speed

Median forward latency, single sample and batch 256, on a named GPU. Speedup vs the pinned public solver on the same geometry, same machine class. Commercial-solver speedups are appendix-only.

## What we will not score

- Token counts against an LLM asked to “be an RF engineer.”
- Self-reported HFSS hours without a file.
- Human “looks right” without nRMSE.
