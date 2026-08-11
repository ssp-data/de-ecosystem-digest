"""ML is not a separate dialect — it's the same four parts of speech.

  fit(...)     attaches a MODIFIER: the fitted model rides along as metadata
               (xorq tracks a training_hash) without changing what the
               expression computes — exactly Part 1's definition of a modifier
               ("this expression also represents a fitted model").
  predict(...) is a VERB: it returns an Ibis Table expression, so the whole
               train -> predict chain stays deferred, cacheable, and buildable
               with `xorq build` just like any metric.
"""
import pandas as pd
import xorq.api as xo
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from xorq.expr.ml import Pipeline as XorqPipeline
from de_ecosystem.ml.features import build_feature_matrix
from de_ecosystem.ml.splits import make_splits
from de_ecosystem.config import DE_TOOLS, DE_REPOS, TOOL_REPOS
from de_ecosystem.settings import settings

FEATURE_COLS = ["star_count", "pypi_downloads", "article_mentions", "buzz_score"]
TARGET_COL = "label"


def build_xorq_pipeline() -> XorqPipeline:
    """Build a xorq-native ML pipeline wrapping scikit-learn."""
    sklearn_pipe = SklearnPipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=200, random_state=42)),
    ])
    return XorqPipeline.from_instance(sklearn_pipe)


def train_and_predict(
    con: object = None,
    tool_repo_pairs: list[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """
    Build features → split → fit xorq Pipeline → predict → return results.
    Uses settings backend by default.
    """
    if con is None:
        con = settings.backend()
        settings.load_tables_to_backend(con)
    if tool_repo_pairs is None:
        tool_repo_pairs = list(TOOL_REPOS.items())

    matrix = build_feature_matrix(con, tool_repo_pairs)

    # LogisticRegression needs two classes; with no ingested signals every
    # tool gets the same label, so return the trivial baseline instead.
    matrix_df = matrix.execute()
    if matrix_df[TARGET_COL].nunique() < 2:
        return pd.DataFrame({
            "tool": matrix_df["tool"],
            "prediction": matrix_df[TARGET_COL],
        })

    train, test = make_splits(matrix, test_size=0.2)

    # LogisticRegression needs both classes; small demo splits can end up
    # empty or single-class, so fall back to the full matrix.
    train_df = train.execute()
    if len(train_df) < 2 or train_df[TARGET_COL].nunique() < 2:
        train = matrix
    test_df = test.execute()
    if test_df.empty:
        test = matrix

    xorq_pipe = build_xorq_pipeline()
    fitted = xorq_pipe.fit(train, features=FEATURE_COLS, target=TARGET_COL)

    predictions = fitted.predict(test).execute()
    predictions = predictions.rename(columns={"predict": "prediction"})
    return predictions[["tool", "prediction"]]
