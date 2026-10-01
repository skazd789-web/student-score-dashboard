from pathlib import Path
import pandas as pd
DATA_PATH=Path(__file__).parent/"data"/ "scores.csv"
SCORE_COLUMNS =["attendance","assignment","midterm","final"]
def load_scores()->pd.DataFrame:
    df=pd.read_csv(DATA_PATH)
    required ={"student_id", "full_name","class_name",*SCORE_COLUMNS}
    missing=required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns:{sorted(missing)}")
    df[SCORE_COLUMNS]= df[SCORE_COLUMNS].apply(
    pd.to_numeric, errors="coerce"
    )
    return df

def clean_scores(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["student_id"] = data["student_id"].astype(str).str.strip()
    data["full_name"] = data["full_name"].astype(str).str.strip()
    data["class_name"] = data["class_name"].astype(str).str.strip()

    data = data.drop_duplicates(
        subset="student_id",
        keep="last"
    )

    data = data.dropna(subset=SCORE_COLUMNS)

    valid = data[SCORE_COLUMNS].apply(
        lambda column: column.between(0, 10)
    ).all(axis=1)

    return data.loc[valid].reset_index(drop=True)

def enrich_scores(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["total_score"] = (
        0.10 * data["attendance"]
        + 0.20 * data["assignment"]
        + 0.30 * data["midterm"]
        + 0.40 * data["final"]
    ).round(2)

    bins = [-0.01, 4.0, 5.5, 7.0, 8.5, 10.01]

    labels = [
        "Kem",
        "Yeu",
        "Trungbinh",
        "Kha",
        "Gioi"
    ]

    data["classification"] = pd.cut(
        data["total_score"],
        bins=bins,
        labels=labels,
        right=False
    )

    data["status"] = data["total_score"].ge(4.0).map(
        {
            True: "Dat",
            False: "Khongdat"
        }
    )

    return data

def filter_scores(
    df: pd.DataFrame,
    class_name: str | None
) -> pd.DataFrame:

    if not class_name:
        return df.copy()

    return df.loc[
        df["class_name"] == class_name
    ].copy()


def summarize(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "student_count": 0,
            "mean_score": 0,
            "highest_score": 0,
            "pass_rate": 0
        }

    return {
        "student_count": int(len(df)),
        "mean_score": round(
            float(df["total_score"].mean()),
            2
        ),
        "highest_score": round(
            float(df["total_score"].max()),
            2
        ),
        "pass_rate": round(
            float(df["total_score"].ge(4).mean() * 100),
            2
        ),
    }