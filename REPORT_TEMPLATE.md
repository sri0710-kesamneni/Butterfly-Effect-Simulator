# Butterfly Effect Simulator for Human Systems
## Real-data project report

**Dataset:** Demircioglu, M. (2026). *Service Capacity Optimization Data*, Mendeley Data, Version 1. DOI: 10.17632/79zt3t734g.1.  
**Source:** https://data.mendeley.com/datasets/79zt3t734g/1  
**Licence listed by repository:** CC BY 4.0.

## Abstract
This project studies sensitivity in a human-facing service system using a published campus-restaurant dataset. The repository describes 173 respondents observed during peak lunch, with recorded order-placement and meal-delivery timestamps, actual elapsed duration, perceived waiting duration, and satisfaction measures. Python, Pandas, NumPy, Matplotlib, and Streamlit are used for data validation, descriptive analysis, sensitivity experiments, and visualization. Hypothetical perturbations of observed durations are separated from measured data. A counter-capacity what-if model is included only as a counterfactual demonstration because order-to-delivery duration is not equivalent to pure queue waiting time or service time.

## 1. Problem and objectives
Investigate how small changes in observed service-system duration affect performance indicators, describe the relationship between actual and perceived duration where available, and demonstrate the sensitivity of hypothetical capacity scenarios without misrepresenting assumptions as observations.

## 2. Dataset and provenance
Describe the source, author, version, DOI, licence, collection setting, observation window, and exact workbook/sheet used. The repository describes 173 respondents at a campus restaurant during peak lunch (12:00–13:00). Cite the source.

## 3. Variables and interpretation
Use the actual column names from the workbook. The repository description mentions `ordertime`, `servicetime`, `duration`, `durmin`, `perception_duration`, `time_satisfactiongeneral`, and satisfaction items. Verify these names in the downloaded workbook.
**Critical limitation:** the dataset describes `durmin` as system time. Do not label it as pure queue wait or service duration without additional evidence.

## 4. Methodology
1. Import the published workbook without altering the original.
2. Inspect sheet names, columns, missingness, duplicates, and duration ranges.
3. Clean only invalid/missing values required for each analysis and document exclusions.
4. Summarize the observed duration distribution.
5. Explore associations between observed duration and survey variables, where present.
6. Run clearly labelled hypothetical +5%, +10%, and +15% duration perturbations.
7. Run optional counterfactual capacity experiments with the proxy assumption stated explicitly.
8. Save code, seed, parameters, and generated output files.

## 5. Results
Insert real values generated from `outputs/observed_duration_summary.csv`, `outputs/data_quality.csv`, `outputs/duration_sensitivity.csv`, and `outputs/correlations.csv`. Insert the corresponding plots. Do not copy values from a web page as if they were calculated from your local workbook; explain any difference.

## 6. Sensitivity analysis
The percentage-increase experiments are what-if perturbations, not newly observed records. Explain the effect on the mean, median, 95th percentile, and share exceeding selected duration thresholds.

## 7. Capacity what-if and its limitations
The capacity experiment uses system duration as a proxy in a simplified queue model because the workbook does not establish a separate service-time field and known counter count. It demonstrates how assumptions affect results; it is not a prediction of the observed restaurant. To make it empirically predictive, obtain service-start or service-completion timestamps, observed arrivals, and actual counter count.

## 8. Conclusion
Summarize results from the downloaded workbook. Distinguish observations, calculated statistics, and model assumptions. Do not claim the model proves a causal effect.

## 9. Future work
Collect validated arrival, queue-entry, service-start, and service-completion timestamps; record active counters by time interval; calibrate the queue model; compare predictions with held-out observations; and evaluate AI recommendations through preregistered experiments.

## References
Demircioglu, M. (2026). *Service Capacity Optimization Data* (Version 1). Mendeley Data. https://doi.org/10.17632/79zt3t734g.1
