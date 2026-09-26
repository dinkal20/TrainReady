import os
import json
import pandas as pd
import numpy as np


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset(file_path):
    """
    Load CSV, XLSX or XLS dataset.
    """

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    else:
        raise ValueError("Unsupported file format. Use CSV, XLSX or XLS.")


# =========================================================
# MAKE VALUES JSON SAFE
# =========================================================

def make_json_safe(value):

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if isinstance(value, (np.bool_, bool)):
        return bool(value)

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)

    if pd.isna(value):
        return None

    return value


# =========================================================
# DATASET PREVIEW
# =========================================================

def get_dataset_preview(df):
    """
    Get first 3 and last 3 rows of the dataset.
    """

    first_rows = df.head(3).copy()
    last_rows = df.tail(3).copy()

    first_rows = first_rows.replace({np.nan: None})
    last_rows = last_rows.replace({np.nan: None})

    return {
        "first_3_rows": [
            {
                str(column): make_json_safe(value)
                for column, value in row.items()
            }
            for _, row in first_rows.iterrows()
        ],

        "last_3_rows": [
            {
                str(column): make_json_safe(value)
                for column, value in row.items()
            }
            for _, row in last_rows.iterrows()
        ]
    }


# =========================================================
# COLUMN ANALYSIS
# =========================================================

def analyze_column(df, column):

    series = df[column]

    total_values = len(series)
    missing_values = int(series.isna().sum())
    non_missing_values = int(series.notna().sum())

    if total_values > 0:
        missing_percentage = round(
            (missing_values / total_values) * 100,
            2
        )
    else:
        missing_percentage = 0

    unique_values = int(series.nunique(dropna=True))

    if non_missing_values > 0:
        unique_percentage = round(
            (unique_values / non_missing_values) * 100,
            2
        )
    else:
        unique_percentage = 0

    # -----------------------------------------------------
    # SAMPLE VALUES
    # -----------------------------------------------------

    sample_values = [
        make_json_safe(value)
        for value in series.dropna().head(5).tolist()
    ]

    # -----------------------------------------------------
    # MOST FREQUENT VALUE
    # -----------------------------------------------------

    most_frequent_value = None
    most_frequent_count = 0
    most_frequent_percentage = 0

    value_counts = series.dropna().value_counts()

    if len(value_counts) > 0:

        most_frequent_value = make_json_safe(
            value_counts.index[0]
        )

        most_frequent_count = int(
            value_counts.iloc[0]
        )

        if non_missing_values > 0:
            most_frequent_percentage = round(
                (most_frequent_count / non_missing_values) * 100,
                2
            )

    # -----------------------------------------------------
    # BASIC COLUMN INFORMATION
    # -----------------------------------------------------

    result = {
        "column_name": column,
        "data_type": str(series.dtype),

        "total_values": total_values,
        "non_missing_values": non_missing_values,

        "missing_values": missing_values,
        "missing_percentage": missing_percentage,

        "unique_values": unique_values,
        "unique_percentage": unique_percentage,

        "most_frequent_value": most_frequent_value,
        "most_frequent_count": most_frequent_count,
        "most_frequent_percentage": most_frequent_percentage,

        "sample_values": sample_values
    }

    # =====================================================
    # NUMERICAL COLUMN
    # =====================================================

    if pd.api.types.is_numeric_dtype(series):

        numeric_series = series.dropna()

        if len(numeric_series) > 0:

            q1 = numeric_series.quantile(0.25)
            q3 = numeric_series.quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = numeric_series[
                (numeric_series < lower_bound) |
                (numeric_series > upper_bound)
            ]

            result["numerical_statistics"] = {
                "min": make_json_safe(numeric_series.min()),
                "max": make_json_safe(numeric_series.max()),
                "mean": make_json_safe(numeric_series.mean()),
                "median": make_json_safe(numeric_series.median()),
                "standard_deviation": make_json_safe(
                    numeric_series.std()
                ),
                "q1": make_json_safe(q1),
                "q3": make_json_safe(q3),
                "iqr": make_json_safe(iqr),

                "outlier_count": int(len(outliers)),

                "outlier_percentage": round(
                    (len(outliers) / len(numeric_series)) * 100,
                    2
                )
            }

        else:

            result["numerical_statistics"] = {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "standard_deviation": None,
                "q1": None,
                "q3": None,
                "iqr": None,
                "outlier_count": 0,
                "outlier_percentage": 0
            }

    # =====================================================
    # CATEGORICAL / TEXT COLUMN
    # =====================================================

    else:

        top_categories = []

        if len(value_counts) > 0:

            for value, count in value_counts.head(10).items():

                percentage = round(
                    (count / non_missing_values) * 100,
                    2
                )

                top_categories.append({
                    "value": make_json_safe(value),
                    "count": int(count),
                    "percentage": percentage
                })

        result["top_categories"] = top_categories

    return result


# =========================================================
# DATA QUALITY ISSUES
# =========================================================

def detect_quality_issues(df):

    issues = []

    # -----------------------------------------------------
    # MISSING VALUES
    # -----------------------------------------------------

    missing_columns = {}

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        if missing_count > 0:

            missing_mask = df[column].isna()
            missing_columns[column] = {
                "count": missing_count,
                "percentage": round(
                    (missing_count / len(df)) * 100,
                    2
                ) if len(df) > 0 else 0,
                "rows": [int(index) + 2 for index in df.index[missing_mask].tolist()]
            }

    if missing_columns:

        issues.append({
            "type": "Missing Values",
            "severity": "warning",
            "message": "Some columns contain missing values.",
            "details": missing_columns
        })

    # -----------------------------------------------------
    # DUPLICATE ROWS
    # -----------------------------------------------------

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count > 0:

        issues.append({
            "type": "Duplicate Rows",
            "severity": "warning",
            "message": f"{duplicate_count} duplicate rows were found.",
            "count": duplicate_count,
            "rows": [int(index) + 2 for index in df.index[df.duplicated(keep=False)].tolist()]
        })

    # -----------------------------------------------------
    # EMPTY ROWS
    # -----------------------------------------------------

    empty_rows = int(df.isna().all(axis=1).sum())

    if empty_rows > 0:

        issues.append({
            "type": "Empty Rows",
            "severity": "warning",
            "message": f"{empty_rows} completely empty rows were found.",
            "count": empty_rows,
            "rows": [int(index) + 2 for index in df.index[df.isna().all(axis=1)].tolist()]
        })

    # -----------------------------------------------------
    # EMPTY COLUMNS
    # -----------------------------------------------------

    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if empty_columns:

        issues.append({
            "type": "Empty Columns",
            "severity": "critical",
            "message": "Some columns contain no usable data.",
            "columns": empty_columns
        })

    # -----------------------------------------------------
    # CONSTANT COLUMNS
    # -----------------------------------------------------

    constant_columns = []

    for column in df.columns:

        if df[column].nunique(dropna=True) <= 1:

            constant_columns.append(column)

    if constant_columns:

        issues.append({
            "type": "Constant Columns",
            "severity": "warning",
            "message": "Some columns contain only one unique value.",
            "columns": constant_columns
        })

    # -----------------------------------------------------
    # POSSIBLE ID COLUMNS
    # -----------------------------------------------------

    possible_id_columns = []

    if len(df) > 0:

        for column in df.columns:

            name = str(column).lower()

            unique_ratio = (
                df[column].nunique(dropna=True) / len(df)
            )

            if (
                name == "id"
                or name.endswith("_id")
                or unique_ratio >= 0.95
            ):

                possible_id_columns.append(column)

    if possible_id_columns:

        issues.append({
            "type": "Possible ID Columns",
            "severity": "info",
            "message": "These columns may be identifiers.",
            "columns": possible_id_columns
        })

    # -----------------------------------------------------
    # HIGH CARDINALITY COLUMNS
    # -----------------------------------------------------

    high_cardinality_columns = []

    if len(df) > 0:

        for column in df.columns:

            if (
                df[column].dtype == "object"
                or pd.api.types.is_categorical_dtype(df[column])
            ):

                unique_ratio = (
                    df[column].nunique(dropna=True) / len(df)
                )

                if 0.50 <= unique_ratio < 0.95:

                    high_cardinality_columns.append({
                        "column": column,
                        "unique_percentage": round(
                            unique_ratio * 100,
                            2
                        )
                    })

    if high_cardinality_columns:

        issues.append({
            "type": "High Cardinality",
            "severity": "warning",
            "message": "Some categorical columns contain many unique values.",
            "columns": high_cardinality_columns
        })

    # -----------------------------------------------------
    # INCONSISTENT TEXT VALUES
    # -----------------------------------------------------

    inconsistent_values = []

    for column in df.columns:

        if df[column].dtype == "object":

            values = df[column].dropna().astype(str)

            normalized = values.str.strip().str.lower()

            groups = {}

            for original, normal in zip(values, normalized):

                groups.setdefault(normal, set()).add(original)

            for normal_value, original_values in groups.items():

                if len(original_values) > 1:

                    inconsistent_values.append({
                        "column": column,
                        "normalized_value": normal_value,
                        "variants": list(original_values)
                    })

    if inconsistent_values:

        issues.append({
            "type": "Inconsistent Categorical Values",
            "severity": "warning",
            "message": "Some text values may differ only by case or whitespace.",
            "details": inconsistent_values
        })

    return issues


# =========================================================
# INVALID DATA
# =========================================================

def detect_invalid_data(df):

    invalid_data = []

    # Empty or whitespace-only strings
    for column in df.columns:

        if df[column].dtype == "object":

            mask = df[column].notna() & df[column].astype(str).str.strip().eq("")
            rows = [int(index) + 2 for index in df.index[mask].tolist()]
            whitespace_count = len(rows)

            if whitespace_count > 0:

                invalid_data.append({
                    "column": column,
                    "type": "Empty/Whitespace Text",
                    "count": whitespace_count,
                    "rows": rows,
                    "message": "Some text values are empty or contain only whitespace."
                })

    # Negative numerical values
    for column in df.select_dtypes(include=np.number).columns:

        mask = df[column].notna() & (df[column] < 0)
        rows = [int(index) + 2 for index in df.index[mask].tolist()]
        negative_count = len(rows)

        if negative_count > 0:

            invalid_data.append({
                "column": column,
                "type": "Negative Values",
                "count": negative_count,
                "rows": rows,
                "message": "Negative values were found. Whether they are invalid depends on the meaning of this column."
            })

    return invalid_data


# =========================================================
# INCORRECT DATA TYPES
# =========================================================

def detect_incorrect_data_types(df):

    findings = []

    for column in df.columns:

        series = df[column].dropna()

        if len(series) == 0:
            continue

        if df[column].dtype == "object":

            numeric_conversion = pd.to_numeric(series, errors="coerce")
            numeric_ratio = numeric_conversion.notna().mean()

            if numeric_ratio >= 0.90:
                invalid_mask = df[column].notna() & pd.to_numeric(df[column], errors="coerce").isna()
                rows = [int(index) + 2 for index in df.index[invalid_mask].tolist()]

                findings.append({
                    "column": column,
                    "current_type": str(df[column].dtype),
                    "possible_type": "numeric",
                    "rows": rows,
                    "message": "Most values appear to be numeric but the column is stored as text."
                })

            date_conversion = pd.to_datetime(series, errors="coerce")
            date_ratio = date_conversion.notna().mean()

            if date_ratio >= 0.90:
                invalid_mask = df[column].notna() & pd.to_datetime(df[column], errors="coerce").isna()
                rows = [int(index) + 2 for index in df.index[invalid_mask].tolist()]

                findings.append({
                    "column": column,
                    "current_type": str(df[column].dtype),
                    "possible_type": "datetime",
                    "rows": rows,
                    "message": "Most values appear to be dates but the column is stored as text."
                })

    return findings


# =========================================================
# NOISE DETECTION
# =========================================================

def detect_noise(df):

    findings = []

    # Rare categorical values
    for column in df.columns:

        if (
            df[column].dtype == "object"
            or pd.api.types.is_categorical_dtype(df[column])
        ):

            series = df[column].dropna()

            if len(series) == 0:
                continue

            counts = series.value_counts()

            for value, count in counts.items():

                percentage = (count / len(series)) * 100

                if percentage < 1:
                    mask = df[column].eq(value)
                    rows = [int(index) + 2 for index in df.index[mask].tolist()]

                    findings.append({
                        "column": column,
                        "type": "Rare Category",
                        "value": make_json_safe(value),
                        "count": int(count),
                        "percentage": round(percentage, 2),
                        "rows": rows,
                        "message": "This category occurs very rarely and may require review."
                    })

    # Numerical outliers
    for column in df.select_dtypes(include=np.number).columns:

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        mask = df[column].notna() & ((df[column] < lower) | (df[column] > upper))
        rows = [int(index) + 2 for index in df.index[mask].tolist()]
        outlier_count = len(rows)

        if outlier_count > 0:
            findings.append({
                "column": column,
                "type": "Potential Numerical Outliers",
                "count": outlier_count,
                "percentage": round((outlier_count / len(series)) * 100, 2),
                "rows": rows,
                "lower_bound": make_json_safe(lower),
                "upper_bound": make_json_safe(upper),
                "message": "These values are statistical outliers and may require review."
            })

    return findings


# =========================================================
# REDUNDANT DATA
# =========================================================

def detect_redundant_data(df):

    redundant = []

    # Exact duplicate columns
    columns = list(df.columns)

    for i in range(len(columns)):

        for j in range(i + 1, len(columns)):

            col1 = columns[i]
            col2 = columns[j]

            if df[col1].equals(df[col2]):

                redundant.append({
                    "type": "Duplicate Columns",
                    "columns": [col1, col2],
                    "message": "These columns contain exactly the same values."
                })

    # Constant columns
    for column in df.columns:

        if df[column].nunique(dropna=True) <= 1:

            redundant.append({
                "type": "Constant Column",
                "columns": [column],
                "message": "This column contains only one unique value."
            })

    # Highly correlated numerical columns
    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] > 1:

        correlation = numeric_df.corr()

        numeric_columns = list(correlation.columns)

        for i in range(len(numeric_columns)):

            for j in range(i + 1, len(numeric_columns)):

                col1 = numeric_columns[i]
                col2 = numeric_columns[j]

                corr_value = correlation.loc[col1, col2]

                if (
                    pd.notna(corr_value)
                    and abs(corr_value) >= 0.95
                ):

                    redundant.append({
                        "type": "Highly Correlated Columns",
                        "columns": [col1, col2],
                        "correlation": round(
                            float(corr_value),
                            4
                        ),
                        "message": "These numerical columns are highly correlated and may contain overlapping information."
                    })

    return redundant


# =========================================================
# TARGET COLUMN DETECTION
# =========================================================

def detect_target_column(df):

    common_target_names = [
        "target",
        "label",
        "class",
        "outcome",
        "result",
        "prediction",
        "response",
        "y",
        "dependent_variable",
        "diabetes",
        "churn",
        "default",
        "fraud",
        "diagnosis"
    ]

    candidates = []

    for index, column in enumerate(df.columns):

        column_lower = str(column).lower().strip()

        unique_count = df[column].nunique(dropna=True)

        score = 0
        reasons = []

        if column_lower in common_target_names:

            score += 3
            reasons.append("Column name looks like a target/label.")

        if unique_count <= 10 and unique_count > 1:

            score += 1
            reasons.append("Column has a relatively small number of unique values.")

        if index == len(df.columns) - 1:

            score += 1
            reasons.append("Column is the last column in the dataset.")

        candidates.append({
            "column": column,
            "score": score,
            "reasons": reasons,
            "unique_values": int(unique_count)
        })

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    )

    if not candidates:

        return {
            "detected": False,
            "column": None,
            "confidence_score": 0,
            "reasons": [],
            "candidates": []
        }

    best = candidates[0]

    detected = best["score"] >= 2

    return {
        "detected": detected,
        "column": best["column"] if detected else None,
        "confidence_score": best["score"],
        "reasons": best["reasons"],
        "candidates": candidates[:5]
    }


# =========================================================
# TARGET DISTRIBUTION
# =========================================================

def analyze_target_distribution(df, target_info):

    if not target_info.get("detected"):
        return {
            "available": False
        }

    target_column = target_info.get("column")

    if target_column not in df.columns:

        return {
            "available": False
        }

    series = df[target_column].dropna()

    counts = series.value_counts()

    classes = []

    for value, count in counts.items():

        percentage = (
            (count / len(series)) * 100
            if len(series) > 0
            else 0
        )

        classes.append({
            "value": make_json_safe(value),
            "count": int(count),
            "percentage": round(percentage, 2)
        })

    imbalance = False

    if len(counts) >= 2:

        largest = counts.max()
        smallest = counts.min()

        if smallest > 0 and largest / smallest >= 3:

            imbalance = True

    return {
        "available": True,
        "column": target_column,
        "classes": classes,
        "possible_imbalance": imbalance
    }


# =========================================================
# ENCODING REQUIREMENTS
# =========================================================

def check_encoding_requirements(df):

    columns = []

    for column in df.columns:

        if (
            df[column].dtype == "object"
            or pd.api.types.is_categorical_dtype(df[column])
            or pd.api.types.is_bool_dtype(df[column])
        ):

            columns.append({
                "column": column,
                "data_type": str(df[column].dtype),
                "message": "This column may require encoding before machine learning."
            })

    return {
        "required": len(columns) > 0,
        "columns": columns
    }


# =========================================================
# POSSIBLE DATA LEAKAGE
# =========================================================

def detect_possible_leakage(df, target_info):

    findings = []

    if not target_info.get("detected"):

        return findings

    target_column = target_info.get("column")

    # Name based detection
    leakage_words = [
        "target",
        "label",
        "outcome",
        "result",
        "prediction",
        "future",
        "leak"
    ]

    for column in df.columns:

        if column == target_column:
            continue

        name = str(column).lower()

        if any(word in name for word in leakage_words):

            findings.append({
                "column": column,
                "type": "Possible Leakage",
                "message": "Column name suggests it may contain information related to the target."
            })

    # Correlation based detection
    if (
        pd.api.types.is_numeric_dtype(df[target_column])
    ):

        numeric_df = df.select_dtypes(include=np.number)

        if target_column in numeric_df.columns:

            correlations = numeric_df.corr()[target_column]

            for column, correlation in correlations.items():

                if column == target_column:
                    continue

                if (
                    pd.notna(correlation)
                    and abs(correlation) >= 0.95
                ):

                    findings.append({
                        "column": column,
                        "type": "High Target Correlation",
                        "correlation": round(
                            float(correlation),
                            4
                        ),
                        "message": "This feature has extremely high correlation with the target and should be reviewed for possible leakage."
                    })

    return findings


# =========================================================
# TRAINING READINESS
# =========================================================

def format_rows(rows, limit=8):
    """Format spreadsheet-style row numbers without making the report huge."""
    try:
        clean_rows = [int(row) for row in rows]
    except Exception:
        clean_rows = []

    if not clean_rows:
        return ""

    shown = clean_rows[:limit]
    text = ", ".join(str(row) for row in shown)

    if len(clean_rows) > limit:
        text += f", +{len(clean_rows) - limit} more"

    return text


def check_training_readiness(df, quality_issues, target_info, encoding_info):
    """
    Calculate an overall dataset training-readiness percentage and explain
    every detected issue that affects the score.
    """

    readiness_percentage = 100
    readiness_reasons = []
    critical_issues = []
    warnings = []

    def add_reason(issue, reason, impact):
        readiness_reasons.append({
            "issue": issue,
            "reason": reason,
            "impact": impact
        })

    def penalize(issue, reason, impact, critical=False):
        nonlocal readiness_percentage

        readiness_percentage -= impact
        add_reason(issue, reason, impact)

        if critical:
            critical_issues.append(reason)
        else:
            warnings.append(reason)

    # ---------------------------------------------------------
    # BASIC DATASET CHECKS
    # ---------------------------------------------------------
    if df is None or df.empty:
        return {
            "status": "NOT READY",
            "readiness_percentage": 0,
            "readiness_reasons": [{
                "issue": "Empty dataset",
                "reason": "The dataset contains no usable rows.",
                "impact": 100
            }],
            "readiness_summary": (
                "The dataset is not ready for training because it contains "
                "no usable data."
            ),
            "critical_issues": ["The dataset contains no usable rows."],
            "warnings": []
        }

    if len(df.columns) == 0:
        return {
            "status": "NOT READY",
            "readiness_percentage": 0,
            "readiness_reasons": [{
                "issue": "No columns",
                "reason": "The dataset does not contain any columns.",
                "impact": 100
            }],
            "readiness_summary": (
                "The dataset is not ready for training because no columns "
                "were detected."
            ),
            "critical_issues": ["The dataset does not contain any columns."],
            "warnings": []
        }

    # ---------------------------------------------------------
    # QUALITY ISSUES
    # ---------------------------------------------------------
    for issue in quality_issues or []:
        if not isinstance(issue, dict):
            continue

        issue_type = str(
            issue.get("type")
            or issue.get("issue")
            or issue.get("category")
            or ""
        ).lower()

        column = (
            issue.get("column")
            or issue.get("column_name")
            or issue.get("name")
            or ""
        )

        if "missing" in issue_type:
            missing_count = issue.get("count") or issue.get("missing_count") or 0
            impact = min(15, max(2, round((float(missing_count) / max(len(df), 1)) * 15)))
            details = issue.get("details") or {}
            affected = []
            for col_name, info in details.items():
                rows = info.get("rows", []) if isinstance(info, dict) else []
                if rows:
                    affected.append(f"{col_name}: rows {format_rows(rows)}")
                else:
                    affected.append(str(col_name))
            location = "; ".join(affected[:6])
            if len(affected) > 6:
                location += f"; +{len(affected) - 6} more column(s)"
            penalize(
                "Missing values",
                "Missing values were detected" + (f": {location}." if location else "."),
                impact
            )

        elif "duplicate" in issue_type:
            duplicate_count = issue.get("count") or issue.get("duplicate_count") or 1
            impact = min(8, max(2, int(duplicate_count > 0) * 4))
            rows = issue.get("rows", [])
            row_text = f" Affected rows: {format_rows(rows)}." if rows else ""
            penalize(
                "Duplicate rows",
                f"{duplicate_count} duplicate row(s) may reduce dataset quality.{row_text}",
                impact
            )

        elif "empty row" in issue_type:
            rows = issue.get("rows", [])
            row_text = f" Affected rows: {format_rows(rows)}." if rows else ""
            penalize(
                "Empty rows",
                "Empty rows were detected and may not provide useful training information." + row_text,
                5
            )

        elif "empty column" in issue_type:
            penalize(
                "Empty columns",
                "One or more columns contain no useful values.",
                8
            )

        elif "constant" in issue_type:
            penalize(
                "Constant columns",
                "One or more columns contain the same value throughout the dataset.",
                5
            )

        elif "possible id" in issue_type or "id column" in issue_type:
            columns = issue.get("columns", [])
            column_text = ", ".join(str(item) for item in columns)
            penalize(
                "Possible ID column",
                "A possible identifier column was detected and may not provide useful predictive information."
                + (f" Column(s): {column_text}." if column_text else ""),
                3
            )

        elif "high cardinality" in issue_type:
            penalize(
                "High-cardinality column",
                "A column contains many unique values and may require preprocessing before training.",
                4
            )

        elif "inconsistent" in issue_type:
            penalize(
                "Inconsistent categorical values",
                "Categorical values appear inconsistent and may need cleaning or standardization.",
                5
            )

    # ---------------------------------------------------------
    # INVALID DATA
    # ---------------------------------------------------------
    try:
        invalid_data = detect_invalid_data(df) or []
    except Exception:
        invalid_data = []

    if invalid_data:
        columns = []
        for item in invalid_data:
            if isinstance(item, dict):
                column = item.get("column") or item.get("column_name")
                if column and column not in columns:
                    columns.append(str(column))

        location = f" in columns: {', '.join(columns)}" if columns else ""
        penalize(
            "Invalid data",
            f"Invalid data was detected{location} and should be cleaned before training.",
            8,
            critical=True
        )

    # ---------------------------------------------------------
    # INCORRECT DATA TYPES
    # ---------------------------------------------------------
    try:
        incorrect_types = detect_incorrect_data_types(df) or []
    except Exception:
        incorrect_types = []

    if incorrect_types:
        columns = []
        for item in incorrect_types:
            if isinstance(item, dict):
                column = item.get("column") or item.get("column_name")
                if column and column not in columns:
                    columns.append(str(column))

        location = f" in columns: {', '.join(columns)}" if columns else ""
        penalize(
            "Incorrect data types",
            f"Potentially incorrect data types were detected{location} and may require conversion.",
            8,
            critical=True
        )

    # ---------------------------------------------------------
    # NOISE
    # ---------------------------------------------------------
    try:
        noise = detect_noise(df) or []
    except Exception:
        noise = []

    if noise:
        noise_details = []
        for item in noise[:8]:
            if not isinstance(item, dict):
                continue
            column = item.get("column", "Unknown")
            rows = item.get("rows", [])
            item_type = item.get("type", "Potential noise")
            detail = f"{item_type} in '{column}'"
            if rows:
                detail += f" at rows {format_rows(rows)}"
            noise_details.append(detail)
        detail_text = "; ".join(noise_details)
        if len(noise) > 8:
            detail_text += f"; +{len(noise) - 8} more finding(s)"
        penalize(
            "Noise",
            "Potential noisy values or outliers were detected and may affect model training."
            + (f" Details: {detail_text}." if detail_text else ""),
            5
        )

    # ---------------------------------------------------------
    # REDUNDANT DATA
    # ---------------------------------------------------------
    try:
        redundant = detect_redundant_data(df) or []
    except Exception:
        redundant = []

    if redundant:
        redundant_details = []
        for item in redundant[:8]:
            if not isinstance(item, dict):
                continue
            columns = item.get("columns", [])
            if columns:
                redundant_details.append(f"{item.get('type', 'Related columns')}: {', '.join(str(c) for c in columns)}")
        detail_text = "; ".join(redundant_details)
        if len(redundant) > 8:
            detail_text += f"; +{len(redundant) - 8} more finding(s)"
        penalize(
            "Redundant data",
            "Redundant columns or highly related information were detected and may need review."
            + (f" Details: {detail_text}." if detail_text else ""),
            5
        )

    # ---------------------------------------------------------
    # TARGET COLUMN
    # ---------------------------------------------------------
    target_column = None

    if isinstance(target_info, dict):
        target_column = (
            target_info.get("target_column")
            or target_info.get("column")
            or target_info.get("name")
        )

    if not target_column:
        penalize(
            "Target column",
            "A clear target column could not be identified automatically.",
            10,
            critical=True
        )

    # ---------------------------------------------------------
    # ENCODING REQUIREMENTS
    # ---------------------------------------------------------
    encoding_columns = []

    if isinstance(encoding_info, dict):
        possible_columns = (
            encoding_info.get("columns")
            or encoding_info.get("categorical_columns")
            or []
        )

        for item in possible_columns:
            if isinstance(item, dict):
                column = item.get("column") or item.get("column_name") or item.get("name")
                if column:
                    encoding_columns.append(str(column))
            elif isinstance(item, str):
                encoding_columns.append(item)

    if encoding_columns:
        penalize(
            "Encoding required",
            "Categorical columns may require encoding before they can be used by some machine-learning algorithms: "
            + ", ".join(encoding_columns),
            4
        )

    # ---------------------------------------------------------
    # POSSIBLE DATA LEAKAGE
    # ---------------------------------------------------------
    try:
        leakage = detect_possible_leakage(df, target_info) or []
    except Exception:
        leakage = []

    if leakage:
        penalize(
            "Possible data leakage",
            "Possible target leakage was detected and should be reviewed before training.",
            12,
            critical=True
        )

    # ---------------------------------------------------------
    # KEEP SCORE IN RANGE
    # ---------------------------------------------------------
    readiness_percentage = max(0, min(100, int(round(readiness_percentage))))

    # Remove duplicate reasons while preserving order.
    unique_reasons = []
    seen = set()

    for item in readiness_reasons:
        key = (
            item.get("issue", ""),
            item.get("reason", "")
        )

        if key not in seen:
            seen.add(key)
            unique_reasons.append(item)

    readiness_reasons = unique_reasons

    # ---------------------------------------------------------
    # STATUS + SUMMARY
    # ---------------------------------------------------------
    if readiness_percentage >= 85 and not critical_issues:
        status = "READY"
        if readiness_reasons:
            readiness_summary = (
                f"The dataset is approximately {readiness_percentage}% ready for "
                "training. Some data-quality issues were detected and should be reviewed."
            )
        else:
            readiness_summary = (
                f"The dataset is approximately {readiness_percentage}% ready for "
                "training. No major issues were detected."
            )

    elif readiness_percentage >= 65:
        status = "READY WITH WARNINGS"
        readiness_summary = (
            f"The dataset is approximately {readiness_percentage}% ready for "
            "training, but some data-quality issues should be reviewed before training."
        )

    else:
        status = "NOT READY"
        readiness_summary = (
            f"The dataset is approximately {readiness_percentage}% ready for "
            "training. The detected issues should be addressed before training."
        )

    return {
        "status": status,
        "readiness_percentage": readiness_percentage,
        "readiness_reasons": readiness_reasons,
        "readiness_summary": readiness_summary,
        "critical_issues": critical_issues,
        "warnings": warnings
    }

def analyze_dataset(df, file_name):

    # -----------------------------------------------------
    # DATASET OVERVIEW
    # -----------------------------------------------------

    rows = int(df.shape[0])
    columns = int(df.shape[1])

    total_cells = int(rows * columns)

    duplicate_rows = int(
        df.duplicated().sum()
    )

    empty_rows = int(
        df.isna().all(axis=1).sum()
    )

    empty_columns = int(
        df.isna().all(axis=0).sum()
    )

    total_missing = int(
        df.isna().sum().sum()
    )

    # -----------------------------------------------------
    # DATASET SIZE
    # -----------------------------------------------------

    memory_usage = int(
        df.memory_usage(deep=True).sum()
    )

    if memory_usage < 1024:

        dataset_size = f"{memory_usage} B"

    elif memory_usage < 1024 ** 2:

        dataset_size = f"{memory_usage / 1024:.2f} KB"

    elif memory_usage < 1024 ** 3:

        dataset_size = f"{memory_usage / (1024 ** 2):.2f} MB"

    else:

        dataset_size = f"{memory_usage / (1024 ** 3):.2f} GB"

    # -----------------------------------------------------
    # DATA TYPES
    # -----------------------------------------------------

    data_types = {
        str(column): str(df[column].dtype)
        for column in df.columns
    }

    # -----------------------------------------------------
    # COLUMN ANALYSIS
    # -----------------------------------------------------

    column_analysis = []

    for column in df.columns:

        column_analysis.append(
            analyze_column(df, column)
        )

    # -----------------------------------------------------
    # QUALITY
    # -----------------------------------------------------

    quality_issues = detect_quality_issues(df)

    invalid_data = detect_invalid_data(df)

    incorrect_data_types = detect_incorrect_data_types(df)

    noise_detection = detect_noise(df)

    redundant_data = detect_redundant_data(df)

    # -----------------------------------------------------
    # TARGET
    # -----------------------------------------------------

    target_info = detect_target_column(df)

    target_distribution = analyze_target_distribution(
        df,
        target_info
    )

    # -----------------------------------------------------
    # ENCODING
    # -----------------------------------------------------

    encoding_info = check_encoding_requirements(df)

    # -----------------------------------------------------
    # LEAKAGE
    # -----------------------------------------------------

    leakage = detect_possible_leakage(
        df,
        target_info
    )

    # -----------------------------------------------------
    # TRAINING READINESS
    # -----------------------------------------------------

    training_readiness = check_training_readiness(
        df,
        quality_issues,
        target_info,
        encoding_info
    )

    # -----------------------------------------------------
    # PREVIEW
    # -----------------------------------------------------

    preview = get_dataset_preview(df)

    # -----------------------------------------------------
    # FINAL REPORT
    # -----------------------------------------------------

    report = {

        "dataset": {
            "file_name": file_name,
            "file_type": os.path.splitext(file_name)[1].replace(".", "").upper(),
        },

        "summary": {

            "rows": rows,
            "columns": columns,

            "total_cells": total_cells,

            "dataset_size": dataset_size,

            "memory_bytes": memory_usage,

            "duplicate_rows": duplicate_rows,

            "empty_rows": empty_rows,

            "empty_columns": empty_columns,

            "total_missing_values": total_missing
        },

        "preview": preview,

        "column_names": [
            str(column)
            for column in df.columns
        ],

        "data_types": data_types,

        "columns": column_analysis,

        "quality_issues": quality_issues,

        "invalid_data": invalid_data,

        "incorrect_data_types": incorrect_data_types,

        "noise_detection": noise_detection,

        "redundant_data": redundant_data,

        "target_analysis": {

            "detection": target_info,

            "distribution": target_distribution
        },

        "encoding_analysis": encoding_info,

        "possible_data_leakage": leakage,

        "training_readiness": training_readiness
    }

    return make_json_safe(report)


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    file_name = "diabetes_prediction_dataset.xlsx"

    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
    )

    df = load_dataset(file_path)

    report = analyze_dataset(
        df,
        file_name
    )

    print(
        json.dumps(
            report,
            indent=4,
            default=str
        )
    )