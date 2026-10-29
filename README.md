# Butterfly Effect Simulator for Human Systems — Real-Data Edition

## Dataset selected
**Service Capacity Optimization Data**, Mert Demircioglu (2026), Mendeley Data, Version 1, DOI: 10.17632/79zt3t734g.1  
Landing page: https://data.mendeley.com/datasets/79zt3t734g/1  
Licence stated on record: CC BY 4.0.

The repository description reports observations and a concurrent survey for 173 respondents at a campus restaurant during peak lunch (12:00–13:00). Observers recorded order-placement and meal-delivery timestamps. The dataset includes actual elapsed duration (`duration`/`durmin`) and perceived waiting/satisfaction fields.

## Important interpretation limitation
The dataset describes `durmin` as *system time*, not pure queue waiting time. Order-to-delivery duration may include queueing, order preparation, and handoff. Do not rename it as “queue waiting time” or “service duration.” This project keeps the measured outcome labelled **order-to-delivery duration** and separates it from the queue model.

The counter-capacity experiment is a **counterfactual scenario model**, not a reconstruction of the observed restaurant's actual service process: the dataset does not directly provide a validated per-customer service-time variable or confirmed counter count. Any proxy parameters must be reported as assumptions.

## 1. Download the real dataset
1. Open https://data.mendeley.com/datasets/79zt3t734g/1
2. Click **Download All**.
3. Extract the downloaded archive if needed.
4. Place `data.xlsx` in this project's `data/` folder. Keep the original workbook unchanged.
5. If the downloaded workbook has a different filename, rename a copy to `data.xlsx`.

This package intentionally does not include a fabricated replacement dataset. It will stop with a clear message until you add the actual downloaded workbook.

## 2. Install and run (Windows / VS Code)
```powershell
python -m venv .venv1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe analyze_real_data.py
```
The script prints available sheets and columns on its first run if it cannot automatically find the expected data. It writes CSVs and figures to `outputs/`.

## 3. Dashboard
```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard.py
```
Use the dashboard for data quality, descriptive statistics, duration sensitivity, and a clearly labelled theoretical capacity experiment.

## 4. Analyses
- Validate rows, columns, missing values, duplicates, and duration ranges.
- Summarize actual order-to-delivery duration.
- Compare actual duration with perceived duration and satisfaction where columns are available.
- Sensitivity test: scale observed elapsed duration by 0%, +5%, +10%, and +15%. These are perturbation scenarios, not new observations.
- Queue-capacity what-if: theoretical M/M/s-style simulation uses an explicit proxy service rate inferred from observed system duration. This is only a scenario analysis because system duration is not service time. Do not present it as a validated prediction.

## 5. Reproducibility and ethics
Record workbook filename, sheet name, column mapping, package versions, and seed. Dataset author and source must be cited in the report. Do not publish respondent-level demographic data or identifying information. Prefer aggregated charts and tables.
