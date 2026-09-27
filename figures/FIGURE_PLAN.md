# Figure plan

Venue: `report` (A4 article, assumed text width 6.30 in, 11 pt body; to be re-measured once the LaTeX report exists).
All figures are generated inside `25011189_ENG2440_A1.ipynb` (the brief requires them in the executed notebook); each
figure cell is the "script" and computes its numbers from the data prepared earlier in the notebook.
Radiograph figures are sample grids (layout audit only). Hero figures get 2–3 design variants.

| ID | Claim (one sentence) | Focus series | Form | Width | Hero? |
|----|----------------------|--------------|------|-------|-------|
| A2_dataset_overview | Only 22% of exams are positive, and 38% of patients contribute more than one exam, so classes are imbalanced and exams are not independent. | positive class; multi-exam patients | 2 panels: class bars, exams-per-patient histogram (log); boxes per exam printed | full | |
| A3_representative_images | The data contain hard cases: a 0.3% opacity, an unusually dark film, impossible metadata. | — | 2 × 4 radiograph grid | full | |
| A4_acquisition_metadata | AP films are four times as often positive as PA films (37.5% vs 9.0%); age and sex differ little between classes. | AP prevalence | 3 panels: prevalence by projection and by sex (shared axis), age share by class | full | |
| B4_splits | Patient-grouped splits keep the prevalence within 21.6–22.8% in train, validation and test. | — | 100% stacked bars, positive share from zero, overall line | full | |
| C2_augmentation_panel | Augmented training images stay anatomically plausible. | — | 2 × 4 radiograph grid (original + 3 draws, sampled parameters printed) | full | |
| D2_logistic_baseline | Weight decay up to 0.01 barely changes the baseline (val AUROC 0.713–0.715); stronger penalties underfit; weights mix correlated features. | selected weight decay | line (a) + diverging bars of weights (b) | full | |
| E2_lr_selection | All three fine-tuning learning rates reach the same best validation AUROC (0.855–0.858); only 1e-4 then overfits. | selected lr 1e-4 | 2 panels: val AUROC and losses per epoch | full | |
| E4_learning_curves | Fine-tuning lifts validation AUROC from 0.83 to ≈ 0.86 within 1–3 epochs; afterwards training loss keeps falling while validation loss rises (overfitting). | validation curves | 2 panels: loss, val AUROC; seed bands | full | yes |
| C4_imbalance_effect | Weighted BCE moves the operating point (sensitivity at t = 0.5: 0.56 → 0.82) but not the ranking (AUROC 0.861 for both). | weighted BCE | dot plot of metrics (mean ± SD) + probability histograms | full | |
| F1_confusion_matrices | At the screening threshold the CNN finds 727 of 815 positives with 1,059 false alarms; the high-specificity threshold reverses the trade-off. | — | 2 annotated 2 × 2 matrices, errors coral / correct blue | full | |
| F3_roc_pr_curves | The fine-tuned CNN beats the logistic baseline at every operating point (AUROC 0.857 vs 0.689; AUPRC 0.655 vs 0.335). | CNN, fine-tuned | ROC + PR, shared legend below (curves meet at both ends), operating points | full | yes |
| F5_reliability | The weighted CNN over-predicts (ECE 0.195); Platt scaling fixes calibration (ECE 0.011) without changing AUROC. | CNN, fine-tuned (+ Platt) | reliability curves + count strips | full | |
| G1_error_examples | The most confident mistakes are made with near certainty (FP p = 0.99, FN p = 0.01). | — | 2 × 4 radiograph grid | full | |
| G2_subgroups | Within each projection AUROC (0.82) is lower than overall (0.86): part of the ranking comes from AP-versus-PA differences. | view subgroups | forest (dot + CI) plot | full | yes |
| G3_gradcam | True-positive heat overlaps the boxes; correct negatives have ~10× weaker maps. | — | 2 × 4 radiograph grid + colour bar | full | |
| G4_gradcam_summary | On positives the heat concentrates on annotated opacities (ratio > 1 for 76%); negatives have little heat, mostly near the edges. | positives | 2 mean maps + ratio histogram | full | |
| X1_prevalence_shift | Moving prevalence from 40% to 10% leaves sensitivity, specificity and AUROC unchanged but cuts PPV from 0.62 to 0.22. | PPV and F1 | 3 panels: stable metrics, PPV, F1 (+ Bayes curves) | full | |
| X2_masks | The border mask and the lung-field control cover the same 29.6% of the image. | — | 3 image panels | full | |
| X2_delta_p | Masking the lung fields moves predictions about five times more than masking the border (median abs Δp 0.237 vs 0.045). | border mask | histogram + ECDF | full | |
| X2_gradcam_top3 | The three largest border-mask changes are all increases of ~0.5, two on negatives. | — | 2 × 3 radiograph grid + colour bar | full | |
