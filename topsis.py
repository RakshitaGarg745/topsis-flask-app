import numpy as np
import pandas as pd

def topsis(df, weights, impacts):
    data = df.copy()

    matrix = data.iloc[:, 1:].values.astype(float)
    weights = np.array(weights)
    impacts = np.array(impacts)

    # Step 1: Normalize
    norm = np.sqrt((matrix ** 2).sum(axis=0))
    norm_matrix = matrix / norm

    # Step 2: Weighted normalized matrix
    weighted = norm_matrix * weights

    # Step 3: Ideal best and worst
    ideal_best = []
    ideal_worst = []

    for i in range(weighted.shape[1]):
        if impacts[i] == '+':
            ideal_best.append(weighted[:, i].max())
            ideal_worst.append(weighted[:, i].min())
        else:
            ideal_best.append(weighted[:, i].min())
            ideal_worst.append(weighted[:, i].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    # Step 4: Distances
    d_pos = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))

    # Step 5: TOPSIS score
    score = d_neg / (d_pos + d_neg)

    # ✅ FIX IS HERE
    score_series = pd.Series(score)

    data["Topsis Score"] = score_series.round(2)
    data["Rank"] = score_series.rank(ascending=False, method="dense").astype(int)

    return data
