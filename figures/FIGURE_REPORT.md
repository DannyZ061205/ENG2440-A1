# Figure report

Process: `paper-figure` skill. House style in `helpers/paper_plot_style.py` (verbatim, constants edited: `VENUE = "report"`;
backend line guarded so figures still display inline in Jupyter). Every figure is saved through `save_fig`, which runs the
automatic audit and writes a vector PDF, a preview PNG and a grayscale preview.

**Assumptions.** Width 6.30 in (A4 report, ~2.5 cm margins, 11 pt body) from the skill's `report` entry, *not measured*:
the LaTeX report does not exist yet. Re-measure `\textwidth` when it does and set `TEXT_WIDTH_OVERRIDE`; only the
constants change. Body font assumed Times (serif stack Times New Roman / STIX), so the report should use a Times-like font
(e.g. `newtx`) to match.

**Privacy.** Until 2026-09-27 figures that contain radiographs were inspected only as layout previews in which every
radiograph was replaced by a synthetic placeholder (course rule at the time). After the rule was changed in class, the real
figures were viewed on 2026-09-27 and their captions/answers corrected (marked CHECKED below).

**Palette (changed 2026-09-27).** The skill's muted default (coral / dusty blue / sky, pastel fills, light-grey ticks)
looked flat, so the author chose palette A ("editorial") from a three-option mock-up: signal red `#D7301F` for the claim
series and the positive class, petrol `#16425B` for the main rival and the negative class, slate `#7FA3B3` and oxblood
`#8C1C13` (Platt, a transform of the same CNN) for context series, gold `#FFB000` for boxes on radiographs; ink
`#161616`, ticks `#505050`, spines `#9A9A9A`. Confusion-matrix cells are solid tints scaled by row share with white
numbers on dark cells. Grad-CAM keeps `inferno` (perceptually uniform, readable over grey radiographs). The review scores
below were given to the earlier palette; the layouts are unchanged.

## Status

| Figure | Claim (short) | Audit | Status | Notes / decisions |
|---|---|---|---|---|
| A2_dataset_overview | 22% positive; 38% of patients have ≥ 2 exams | PASS, 0 notes | FIXED | 2 panels; multi-exam patients in accent, single-exam grey; x-axis trimmed to data |
| A3_representative_images | examples by fixed rules | PASS | CHECKED | real images read well; "darkest" film is a child framed by black background (text fixed); negative PA example is visibly abnormal (added) |
| A4_acquisition_metadata | AP 37.5% vs PA 9.0% positive | PASS, 0 notes | FIXED | panels projection · sex · age; shared 0–40% axis for (a, b); direct labels in (c); counts in the caption |
| B4_splits | prevalence 21.6–22.8% in every split | PASS, 1 taste | FIXED | 100% stacked bars with the positive share drawn from zero; negative share as a pale petrol tint (context, so the red claim leads); aspect note (line rule on a bar chart) justified |
| C2_augmentation_panel | augmentation stays plausible | PASS | CHECKED | augmentations plausible; black rotation corners explained in [C2] |
| D2_logistic_baseline | weight decay barely matters | PASS, 1 taste | FIXED | taste note "15 ticks" is the 15 feature names on a category axis: justified |
| E2_lr_selection | the three learning rates tie; only 1e-4 overfits | PASS, 0 notes | FIXED | ordered values: selected lr in accent, others petrol/slate with distinct dashes |
| E4_learning_curves (hero) | fine-tuning helps for 1–3 epochs, then overfits | PASS, 0 notes | FIXED | **variant A (mean ± SD band) chosen over B (one line per seed)**: B turns into spaghetti and hides the takeaway; the seed spread is small enough for a quiet band |
| C4_imbalance_effect | weighting moves the operating point, not the ranking | PASS, 0 notes | FIXED | grouped bars replaced by a dot plot (close values); neutral panel titles, claim in the caption |
| F1_confusion_matrices | screening finds 727/815 with 1,059 false alarms | PASS, 0 notes | FIXED | errors red, correct calls petrol, solid tint = row share; number colour chosen by WCAG contrast with the cell (white on dark cells). 6 audit taste notes ('too light to read') are false alarms: the audit compares text with the white page, not with the dark cell behind it |
| F3_roc_pr_curves (hero) | CNN beats logistic at every operating point | PASS, 0 notes | FIXED | **variant A (one shared legend below the panels) chosen over B (legends inside the axes)**: B failed the audit (legend covered 2,424 data points) and ROC curves meet at both ends, so end-of-line labels are impossible |
| F5_reliability | weighted CNN over-predicts; Platt fixes calibration | PASS, 0 notes | FIXED | shared legend below; hollow markers for bins with < 30 exams; strips in the same 10 bins |
| G1_error_examples | TP/TN/FP/FN examples | PASS | CHECKED | caption now describes the most confident miss and false alarm |
| G2_subgroups (hero) | within-projection AUROC below overall | PASS, 2 taste | FIXED | **variant A (forest plot + table column) chosen over B (counts in the row labels)**: only A shows the sens/spec shift between AP and PA, the key evidence. Taste notes "8 ticks" = the 8 subgroup rows on a category axis: justified |
| G3_gradcam | Grad-CAM, 4 correct + 4 incorrect | PASS | CHECKED | column titles: errors red, correct calls petrol (as F1); heat overlaps boxes but also the heart/mediastinum; negatives' faint heat at corners (caption fixed) |
| G4_gradcam_summary | heat concentrates on annotated boxes | PASS, 0 notes | CHECKED | mean positive map is one central blob over heart + medial bases (caution added to [G4]) |
| X1_prevalence_shift | PPV/F1 move with prevalence, the rest do not | PASS, 1 taste | FIXED | 3 panels; changing metrics in accent, stable ones in petrol/slate/grey; equal-weight note justified (all context) |
| X2_masks | equal-area border mask and lung control | PASS | CHECKED | masks sit where intended on the average image |
| X2_delta_p | lung masking moves predictions ~5× more | PASS, 0 notes | FIXED | legend and callouts replaced by direct labels with the medians |
| X2_gradcam_top3 | largest border-mask changes, before/after | PASS | CHECKED | after masking the heat moves to the centre, not onto the frame (caption extended) |

Audit limitations found (documented, not patched, because the audit is the skill's verbatim code):
* markers without lines (errorbar dots) are treated as if joined by straight segments, so text between rows was flagged;
  worked around by drawing one point per call;
* a callout's leader line is part of its bounding box, so any callout pointing at a curve is flagged as "text on data";
  worked around by labels without leaders;
* vertical reference lines drawn with `axvline` are checked in the wrong coordinates, so a label sitting on one is missed
  (found by eye in G2 and fixed).

## Independent review (round 1) and what changed

A separate reviewer saw only the rendered previews (radiographs replaced by placeholders), the captions and a short data
summary. Scores (1–5: Focus / Economy / Hierarchy / Labeling / Typography / Composition / Family) and the change made:

| Figure | Round-1 scores | Main finding | Change made (round 2) |
|---|---|---|---|
| A2 | 4 4 4 5 4 4 5 | panel (c) did not serve the claim | (c) removed, (b) widened, minor log ticks removed |
| A3 | 3 3 4 4 4 4 4 | chips repeated the titles; smallest box invisible | chips only on the bottom row; 3× zoom inset; claim-type caption |
| A4 | 4 4 4 3 3 3 3 | cryptic axis labels, bar panels separated | order projection · sex · age; "share of exams positive"; counts in the caption |
| B4 | 3 3 4 4 4 **2** 5 | bars showed counts, the claim is about shares | 100% stacked bars, positive share from zero, overall line |
| C2 | 3 3 4 3 4 4 4 | "small" not checkable by eye | 2 × 4 grid; sampled parameters printed under each draw and in a table |
| C4 | 4 4 4 3 4 4 **2** | purple outside the family | plain BCE = grey context series (registry); AUROC "both 0.861" note |
| D2 | 3 4 4 3 3 4 4 | **caption contradicted the plot** (drop at 1e-1, 1) | claim limited to ≤ 0.01; tick naming unified; hist bins defined; r(p25, p50) = 0.85 in caption |
| E2 | 4 4 5 4 4 4 3 | 3e-5 looks as good; training lines colour-only | best-epoch dots; training lines dashed; rule and tie stated in the caption |
| E4 (hero) | 5 4 5 5 4 4 **3** | style and AUROC range differ from E2 | training = thin dashed (as E2); same AUROC axis as E2; baseline as a note |
| F1 | 3 3 3 4 4 3 4 | darkest cell was the least interesting | errors coral, correct calls blue; "of row" removed; shared y label |
| F3 (hero) | 4 **3** 4 **3** 4 **3** 4 | legend = 3-seed mean but bold curve = seed 2; recall-0 artefact; legend too tall | legend gives the plotted seed's values; recall = 0 point dropped; legend halved (markers explained in caption) |
| F5 | 3 3 4 3 4 3 **2** | sparse bins at full weight; off-family colours | hollow markers for bins with < 30 exams; strips use the same 10 bins; AUROC note; grey plain BCE |
| G1 | 3 4 4 4 4 4 4 | repeated labels | column titles and row labels once; claim-type caption |
| G2 (hero) | 4 4 4 4 4 4 4 | AP/PA sens/spec buried in the table | projection rows of the table in the accent colour |
| G3 | 3 3 3 3 4 3 4 | amber boxes vanish in inferno; per-image scaling hides weak maps | white boxes; raw peak heat printed per image; claim-type caption |
| G4 | 4 4 4 3 4 4 4 | "much weaker" not measurable | shared colour bar in raw units; ratio-0 spike counted (82 exams) |
| X1 | 5 3 5 4 3 4 4 | three near-empty panels; invisible error bars | 3 panels (stable metrics merged); caption says the SDs are smaller than the markers |
| X2a | 4 4 4 4 4 4 4 | tints looked brown | grey fill as the model saw it + coloured outlines |
| X2b | 5 4 5 4 4 4 5 | zero bins drew a floor line | histogram stops at the last non-empty bin; labels next to the curves |
| X2c | 3 3 4 **2** 4 3 4 | no colour bar; finding not stated | 2 × 3 layout, colour bar, printed table, claim-type caption |

## Independent review (round 2)

The same reviewer re-scored the eight figures that were below threshold or had a correctness issue:

| Figure | Round-2 scores | Threshold | Remaining note → action |
|---|---|---|---|
| B4 | 5 4 4 4 4 4 4 | ≥ 3 met | reference line black/unlabelled → grey, labelled "overall 22.0%" |
| C4 | 4 4 4 4 4 4 4 | ≥ 3 met | "both 0.861" touched a marker → nudged |
| D2 | 4 4 4 4 3 4 4 | ≥ 3 met | mixed 0.7 / 0.71 ticks → two decimals |
| E2 | 4 4 5 4 4 4 4 | ≥ 3 met | — |
| E4 (hero) | 5 4 5 4 4 4 5 | ≥ 4 met | dots unlabeled → "dots: selected epochs" |
| F3 (hero) | 4 4 4 4 4 4 4 | ≥ 4 met | logistic seed value = mean → explained in the caption (convex fit) |
| F5 | 4 3 4 4 4 3 3 | ≥ 3 met | **must-fix:** top Platt bin (n = 17) looked filled → it was clipped at 1.0; axis headroom added, sparse bins printed |
| X2c | 4 4 4 4 4 4 4 | ≥ 3 met | — |

All figures pass the automatic audit after round 2 (0 errors, 0 warnings). Remaining taste notes are justified: tick counts on
category axes (D2: 15 feature names; G2: 8 subgroup rows), the line-aspect rule on the B4 bar chart, and equal line
weights for the three context series in X1(a).

**Radiograph check (2026-09-27):** A3, C2, G1, G3, G4(a–b), X2a and X2c viewed with the real radiographs; all
NEEDS-HUMAN items closed (see Status).
