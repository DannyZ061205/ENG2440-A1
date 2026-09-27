"""
Offline requirement audit for ENG2440 Assignment 1.

Run it from a terminal after executing the notebook:

    python -m helpers.checklist 25011189_ENG2440_A1.ipynb

It re-reads the saved .ipynb file and checks that
* the notebook was executed top to bottom in one run, without errors,
* every requirement of the brief (Sections 3 and 4) has its evidence in the notebook: a printed output, a piece
  of code, or a written answer (found by the bold phrase that starts the paragraph),
* both bonus answers are about 150-250 words,
* every expected figure was saved and passed the automatic figure audit, and
* decimal numbers quoted in the markdown also appear in some code output (a guard against stale numbers).
"""

import json
import re
import sys
from pathlib import Path

# (id, marks, requirement, [evidence]); evidence items are ("md" | "code" | "out", text that must appear there)
RUBRIC = [
    ("A1", 2, "Input, output and clinical question", [("md", "**Input:**"), ("md", "**Output:**"), ("md", "**Clinical question:**")]),
    ("A2", 3, "Exams, source patients, class counts and proportions", [("out", "unique examinations"), ("out", "unique source patients")]),
    ("A3", 2, ">= 6 representative images incl. difficult/unusual", [("md", "**Why these examples.**"), ("fig", "A3_representative_images")]),
    ("A4", 1, "Image size, photometric interpretation, projection", [("out", "photometric interpretation"), ("out", "view position")]),
    ("B1", 3, "Split grouped by NIH patient id", [("code", 'groupby("nih_patient_id")'), ("code", "patient_split")]),
    ("B2", 1, "Test set untouched until final evaluation", [("code", "assert len(earlier_cells) == 1")]),
    ("B3", 2, "Assertions: patient sets are disjoint", [("code", "isdisjoint")]),
    ("B4", 2, "Size and positive proportion of every split", [("out", "Patient-grouped splits")]),
    ("B5", 2, "Further multi-site leakage route + test", [("md", "site leakage")]),
    ("C1", 3, "DICOM -> tensor, resize, intensity scaling", [("md", "**Preprocessing summary.**")]),
    ("C2", 3, "Training-only augmentation, panel, justification", [("md", "**Why these are safe.**"), ("fig", "C2_augmentation_panel")]),
    ("C3", 2, "No meaning-changing transforms; flip justified", [("md", "**What we did not use.**"), ("md", "Horizontal flip")]),
    ("C4", 4, "Imbalance strategy evaluated with and without", [("md", "**Effect of the weighted loss.**"), ("fig", "C4_imbalance_effect")]),
    ("D1", 2, "Trivial majority-class baseline", [("out", "Trivial majority-class baseline")]),
    ("D2", 5, "nn.Linear baseline on >= 4 stated features", [("code", "nn.Linear(X.shape[1], 1)"), ("md", "**Reading the baseline.**")]),
    ("D3", 3, "Baseline: train on train, select on val, test once", [("code", "predict_logistic(logistic_models[s], X_test_feat)")]),
    ("E1", 4, "1-channel adaptation + binary head, stated exactly", [("out", "replicated grey image: True"), ("md", "**Input channels.**")]),
    ("E2", 5, "Fixed feature extractor, then fine-tune final block", [("code", 'blocks=["fc"]'), ("code", 'blocks=["layer4", "fc"]')]),
    ("E3", 2, "Controlled comparison with the baseline", [("md", "**A controlled comparison.**")]),
    ("E4", 3, "Loss curves + under/overfitting discussion", [("md", "**Under- or overfitting?**"), ("fig", "E4_learning_curves")]),
    ("E5", 6, "Seeds, >= 3 runs, mean +/- SD, gap vs noise", [("md", "**Seeds and run-to-run variation.**"), ("out", "Primary metric: test AUROC")]),
    ("F1", 3, "Confusion matrix and threshold metrics", [("out", "at the two frozen thresholds"), ("fig", "F1_confusion_matrices")]),
    ("F2", 3, "One comparison table: trivial, baseline, CNN", [("out", "Test-set comparison")]),
    ("F3", 3, "ROC + PR curves with areas; which is more informative", [("md", "**Which curve is more informative here?**"), ("fig", "F3_roc_pr_curves")]),
    ("F4", 3, "Two thresholds from validation, frozen, applied to test", [("md", "**The two thresholds**"), ("out", "Frozen thresholds of the headline CNN")]),
    ("F5", 3, "Reliability diagram; discrimination vs calibration", [("md", "**Discrimination versus calibration.**"), ("fig", "F5_reliability")]),
    ("G1", 2, "TP, TN, FP, FN examples", [("out", "Examples shown in Figure G1"), ("fig", "G1_error_examples")]),
    ("G2", 2, "Subgroups with sizes, cautious interpretation", [("md", "**Interpreting the subgroups.**"), ("out", "by subgroup")]),
    ("G3", 3, "Grad-CAM >= 4 images; layer named and justified", [("md", "**Layer: `model.layer4`.**"), ("fig", "G3_gradcam")]),
    ("G4", 3, "Lung focus vs shortcuts; Grad-CAM is not causal", [("md", "**Lungs or shortcuts?**")]),
    ("X1", 5, "BONUS 1: prevalence shift with frozen threshold", [("md", "**What changed and why.**"), ("fig", "X1_prevalence_shift")]),
    ("X2", 5, "BONUS 2: border mask with equal-area lung control", [("md", "**What the control is for and what we can conclude.**"), ("fig", "X2_gradcam_top3")]),
]
BONUS_ANSWERS = {"X1": "**What changed and why.**", "X2": "**What the control is for and what we can conclude.**"}

EXPECTED_FIGURES = [
    "A2_dataset_overview", "A3_representative_images", "A4_acquisition_metadata",
    "B4_splits", "C2_augmentation_panel", "D2_logistic_baseline",
    "E2_lr_selection", "E4_learning_curves", "C4_imbalance_effect", "F1_confusion_matrices",
    "F3_roc_pr_curves", "F5_reliability", "G1_error_examples", "G2_subgroups",
    "G3_gradcam", "G4_gradcam_summary", "X1_prevalence_shift", "X2_masks", "X2_delta_p", "X2_gradcam_top3",
]
NUMBER_RE = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w.])")      # numbers with 3+ decimals, e.g. 0.853


def _text(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def _outputs(cell):
    chunks = []
    for out in cell.get("outputs", []):
        if "text" in out:
            chunks.append("".join(out["text"]) if isinstance(out["text"], list) else out["text"])
        for key in ("text/plain", "text/html", "text/markdown"):
            data = out.get("data", {}).get(key)
            if data:
                chunks.append("".join(data) if isinstance(data, list) else data)
    return "\n".join(chunks)


def _paragraph(markdown, lead):
    """The paragraph block (up to the next heading) that starts with the bold phrase `lead`."""
    start = markdown.find(lead)
    if start < 0:
        return ""
    end = markdown.find("\n#", start)
    return markdown[start:end if end > 0 else None]


def audit(nb_path, fig_dir="figures"):
    cells = json.loads(Path(nb_path).read_text())["cells"]
    code = [c for c in cells if c["cell_type"] == "code"]
    md = "\n\n".join(_text(c) for c in cells if c["cell_type"] == "markdown")
    src = "\n\n".join(_text(c) for c in code)
    out = "\n\n".join(_outputs(c) for c in code)
    figs = {n for n in EXPECTED_FIGURES if (Path(fig_dir) / f"{n}.pdf").exists()}
    problems, warnings = [], []

    # 1. one clean top-to-bottom execution
    counts = [c.get("execution_count") for c in code if _text(c).strip()]
    if any(n is None for n in counts):
        problems.append("some code cells were never executed")
    elif counts != list(range(1, len(counts) + 1)):
        problems.append("execution counts are not 1..N: the notebook was not run top to bottom in one go")
    for c in code:
        for o in c.get("outputs", []):
            if o.get("output_type") == "error":
                problems.append(f"error output: {o.get('ename')}: {o.get('evalue', '')[:120]}")

    # 2. evidence for every requirement
    where = {"md": md, "code": src, "out": out}
    met = 0
    for rid, marks, desc, evidence in RUBRIC:
        missing = [text for kind, text in evidence
                   if (kind == "fig" and text not in figs) or (kind != "fig" and text not in where[kind])]
        if missing:
            problems.append(f"[{rid}] {desc}: missing {missing}")
        else:
            met += 1

    # 3. bonus answers ~150-250 words
    for rid, lead in BONUS_ANSWERS.items():
        n = len(re.findall(r"[A-Za-z][A-Za-z'-]*", _paragraph(md, lead)))
        if not 140 <= n <= 260:
            problems.append(f"[{rid}] answer has {n} words (brief: about 150-250)")

    # 4. figures saved and without figure-audit errors
    for name in EXPECTED_FIGURES:
        if name not in figs:
            problems.append(f"missing figure {fig_dir}/{name}.pdf")
        log = Path(fig_dir) / "_audit" / f"{name}.json"
        if log.exists():
            errors = [i for i in json.loads(log.read_text())["issues"] if i["severity"] == "error"]
            if errors:
                problems.append(f"figure {name}: {len(errors)} figure-audit error(s)")

    # 5. numbers in the markdown must appear in some output
    for num in sorted(set(NUMBER_RE.findall(re.sub(r"doi:\S+", "", md)))):     # DOIs are not results
        if num not in out:
            warnings.append(f"number {num} in the markdown was not found in any code output")
    for placeholder in ("TODO", "TBD", "XXX", "???"):
        if placeholder in md:
            problems.append(f"markdown still contains placeholder {placeholder!r}")

    print(f"Audit of {nb_path}")
    print(f"  code cells executed : {len(counts)}")
    print(f"  requirements with evidence : {met}/{len(RUBRIC)}")
    print(f"  figures present     : {len(figs)}/{len(EXPECTED_FIGURES)}")
    for w in warnings:
        print("  WARN ", w)
    for p in problems:
        print("  FAIL ", p)
    print("RESULT:", "PASS" if not problems else f"FAIL ({len(problems)} problems)")
    return not problems


if __name__ == "__main__":
    ok = audit(sys.argv[1] if len(sys.argv) > 1 else "25011189_ENG2440_A1.ipynb")
    sys.exit(0 if ok else 1)
