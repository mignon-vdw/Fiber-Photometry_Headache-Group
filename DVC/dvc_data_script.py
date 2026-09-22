# ============================================================
# This script runs DVC distance and locomotion files to 
# put data into 5 minute bins
# ============================================================


import pandas as pd
import numpy as np

# ============================================================
# USER SETTINGS
# ============================================================

input_file = r"D:\DVC\Data.xlsx"
output_file = r"D:\DVC\Data_Binned_5min.xlsx"

# Options:
# "distance"
# "locomotion"
file_type = "distance"

# ============================================================
# INJECTION TIMES
# ============================================================

injection_windows = {
    "HCRT16_2b": [
        ("08:53", "09:15"),
        ("10:24", "10:42")
    ],
    "HCRT16_2d": [
        ("08:53", "09:15"),
        ("10:25", "10:42")
    ],
    "HCRT16_2h": [
        ("08:55", "09:13"),
        ("10:25", "10:42")
    ],
    "HCRT16_2i": [
        ("08:55", "09:13"),
        ("10:25", "10:42")
    ]
}

# ============================================================
# FUNCTIONS
# ============================================================

def overlaps_injection(bin_start, bin_end, mouse):
    """
    Returns True if a bin overlaps any injection period.
    """

    if mouse not in injection_windows:
        return False

    for start_str, end_str in injection_windowsinj_start = pd.Timestamp(
            f"{bin_start.date()} {start_str}"
        )

        inj_end = pd.Timestamp(
            f"{bin_start.date()} {end_str}"
        )

        if max(bin_start, inj_start) <= min(bin_end, inj_end):
            return True

    return False


# ============================================================
# LOAD EXCEL FILE
# ============================================================

xls = pd.ExcelFile(input_file)

# ============================================================
# PROCESS SHEETS
# ============================================================

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

    for sheet in xls.sheet_names:

        print(f"Processing sheet: {sheet}")

        df = pd.read_excel(
            xls,
            sheet_name=sheet
        )

        # ----------------------------------------------------
        # Parse timestamps
        # Example:
        # 2026-08-08T08:00:00.000+0100
        # ----------------------------------------------------

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df = df.dropna(subset=["timestamp"])

        # ----------------------------------------------------
        # Restrict to 08:00-13:00
        # ----------------------------------------------------

        start_time = pd.to_datetime("08:00").time()
        end_time = pd.to_datetime("13:00").time()

        df = df[
            (df["timestamp"].dt.time >= start_time)
            &
            (df["timestamp"].dt.time < end_time)
        ].copy()

        if df.empty:
            print(f"No data found in {sheet}")
            continue

        # ----------------------------------------------------
        # Mouse ID
        # ----------------------------------------------------

        mouse = str(df["mouse"].dropna().iloc[0])

        # ----------------------------------------------------
        # Select measurement
        # ----------------------------------------------------

        if file_type.lower() == "distance":

            df["measurement"] = pd.to_numeric(
                df["v_1"],
                errors="coerce"
            )

        elif file_type.lower() == "locomotion":

            locomotion_cols = [
                f"v_{i}"
                for i in range(1, 13)
                if f"v_{i}" in df.columns
            ]

            df["measurement"] = (
                df[locomotion_cols]
                .apply(pd.to_numeric, errors="coerce")
                .fillna(0)
                .sum(axis=1)
            )

        else:

            raise ValueError(
                "file_type must be 'distance' or 'locomotion'"
            )

        # ----------------------------------------------------
        # Create 5-minute bins
        # ----------------------------------------------------

        df["bin_start"] = (
            df["timestamp"]
            .dt.floor("5min")
        )

        summary = (
            df.groupby("bin_start")["measurement"]
            .agg(
                N_Samples="count",
                Sum="sum",
                Mean="mean"
            )
            .reset_index()
        )

        # ----------------------------------------------------
        # QC Flag
        # ----------------------------------------------------

        summary["QC_Flag"] = np.where(
            summary["N_Samples"] < 5,
            "Missing_Data",
            "Complete"
        )

        # ----------------------------------------------------
        # Injection labels
        # ----------------------------------------------------

        conditions = []

        for _, row in summary.iterrows():

            bin_start = row["bin_start"]

            bin_end = (
                bin_start
                + pd.Timedelta(minutes=5)
                - pd.Timedelta(seconds=1)
            )

            if overlaps_injection(
                bin_start,
                bin_end,
                mouse
            ):
                conditions.append("Injection")
            else:
                conditions.append("Normal")

        summary["Condition"] = conditions

        # --------