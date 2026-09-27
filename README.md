# ENG2440 Assignment 1: Pneumonia Classification Challenge

Zichen Zhao · 25011189 · ENG 2440 Medical Imaging & AI in Healthcare, Fall 2026

An end-to-end PyTorch pipeline that classifies frontal chest radiographs from the RSNA Pneumonia Detection
Challenge (stage-1 training set, 25,684 exams) as *lung opacity consistent with possible pneumonia* vs *no such
opacity*. It compares a trivial baseline, a logistic baseline on image-summary features and an ImageNet-pretrained
ResNet-18, and includes calibration, subgroup, Grad-CAM, prevalence-shift and shortcut stress-test analyses.

**This repository contains no DICOM files, dataset tables or image files.** The executed notebook displays a few example radiographs (downsampled to 224–512 px), as the assignment requires. The RSNA data must be downloaded separately (see below).

## Files

| file | what it is |
|---|---|
| `25011189_ENG2440_A1.ipynb` | the fully executed notebook (all code, outputs, figures and written answers) |
| `helpers/paper_plot_style.py` | figure house style + automatic figure audit (print size, overlapping/clipped text, text on data, grayscale, fonts); code copied from Appendix A of the *paper-figure* figure-style skill, with the venue and palette constants edited |
| `helpers/plotting.py` | project figure helpers: radiograph panel, Grad-CAM overlay, collision-free label placement, notebook tables |
| `helpers/checklist.py` | offline audit: checks that the executed notebook contains the evidence for every requirement of the brief |
| `figures/methods.json` | one label / colour / line style per model, used by every figure and table |
| `figures/FIGURE_PLAN.md`, `figures/FIGURE_REPORT.md` | the one-sentence claim of every figure, and its audit / review status |
| `figures/latex_includes.tex` | ready-to-use LaTeX figure environments with the captions (figure PDFs themselves are not in git) |
| `report/main.tex` | LaTeX source of the report (compile with `tectonic main.tex` after running the notebook, which writes the figure PDFs it uses) |
| `requirements.txt` | exact package versions used |

## Reproduce

1. Download `pneumonia-challenge-dataset-original_2018.zip` from the
   [RSNA challenge page](https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018)
   and extract it to `data/images/`. Put `assignment1_labels.csv` and `rsna_to_nih_mapping.csv` next to the notebook.
2. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. Run the notebook top to bottom. The first run needs internet access once, to download the ImageNet ResNet-18
   weights (about 45 MB, via torchvision). It takes about 1 hour on an Apple M4 Max (MPS); a CUDA GPU is similar, a
   CPU would take many hours. The first run also builds a 1.3 GB image cache in `data/cache/`. Trained models are
   stored in `outputs/runs/` with their configuration, and a saved run is reused only if its configuration matches
   the current code exactly (set `RETRAIN = True` to force retraining). With the same hardware and package versions,
   retraining reproduces the saved runs bit for bit.
4. Check that every requirement is covered: `python -m helpers.checklist 25011189_ENG2440_A1.ipynb`
   (this also fails if any saved figure has an error in its automatic figure audit).

## Data attribution

Radiological Society of North America, RSNA Pneumonia Detection Challenge (2018); Shih et al., *Radiology: AI* 2019
(doi:10.1148/ryai.2019180041). The NIH Clinical Center is acknowledged as the provider of the source chest
radiographs (Wang et al., ChestX-ray8, CVPR 2017).
