import numpy as np
import pandas as pd

class periodOfLife:
    def __init__(self):
        # @marcoferrante estimation
        self._period_of_life_list = [
            "nursery", "nursery school", "elementary school", "middle school",
            "high school", "university/work", "work", "work", "work", "work",
            "retired", "retired", "retired"
        ]
        df = pd.DataFrame(
            {
                "Age_first": [0, 3, 6, 11, 14, 19, 26, 36, 46, 56, 66, 76, 86],
                "Age_last": [2, 5, 10, 13, 18, 25, 35, 45, 55, 65, 75, 85, 95],
                "Period_of_life": self._period_of_life_list,
                "Days": [3, 5, 6, 6, 7, 7, 6, 5, 5, 5, 4, 3, 2]
            }
        )
        # Adjustment by author
        df["Types"] = df["Period_of_life"].replace(
            {
                "nursery": "school",
                "nursery school": "school",
                "elementary school": "school",
                "middle school": "school",
                "high school": "school",
                "university/work": "school/work"
            }
        )
        df["School"] = df[["Types", "Days"]].apply(lambda x: x[1] if "school" in x[0] else 0, axis=1)
        df["Office"] = df[["Types", "Days"]].apply(lambda x: x[1] if "work" in x[0] else 0, axis=1)
        df["Others"] = df["Days"] - df[["School", "Office"]].sum(axis=1)
        df.loc[df["Others"] < 0, "Others"] = 0
        df.loc[df.index[1:5], "School"] -= 1
        df.loc[df.index[1:5], "Others"] += 1
        df.loc[df.index[5], ["School", "Office", "Others"]] = [3, 3, 1]
        df[["School", "Office", "Others"]] = df[["Days", "School", "Office", "Others"]].apply(
            lambda x: x[1:] / sum(x[1:]) * x[0], axis=1
        ).astype(np.int64)
        df.loc[df.index[6:10], "Others"] += 1
        df = df.drop(["Days", "Types"], axis=1)
        # Show dataset
        self.life_out_df = df.copy()
    
    def get_life_outside(self):
        return self.life_out_df
