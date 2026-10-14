"""
Train + evaluate the InfoShield text classifier.
Run:  python train_model.py
Outputs: models/model.pkl, models/metrics.json, models/confusion_matrix.png
"""
import json
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_auc_score

HERE = Path(__file__).parent
OUT = HERE / "models"
OUT.mkdir(exist_ok=True)


def features():
    return FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=3, sublinear_tf=True)),
    ])


def make(clf):
    return Pipeline([("features", features()), ("clf", clf)])


CANDIDATES = {
    "Logistic Regression": lambda: make(LogisticRegression(max_iter=2000, C=3.0, class_weight="balanced")),
    "Linear SVM (calibrated)": lambda: make(CalibratedClassifierCV(LinearSVC(class_weight="balanced"), cv=3)),
    "Multinomial Naive Bayes": lambda: make(MultinomialNB(alpha=0.3)),
}


def scores(y_true, y_pred, proba=None):
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", pos_label=1, zero_division=0)
    d = {"accuracy": round(accuracy_score(y_true, y_pred), 4), "precision": round(p, 4),
         "recall": round(r, 4), "f1": round(f, 4)}
    if proba is not None:
        d["roc_auc"] = round(roc_auc_score(y_true, proba), 4)
    return d


def main():
    df = pd.read_csv(HERE / "data" / "dataset.csv")
    X, y, g = df["text"].values, df["label"].values, df["group"].values
    print(f"Dataset: {len(df)} rows | fake={int(y.sum())} genuine={int((1-y).sum())} | groups={len(set(g))}")

    # group-aware split: all variants of one template stay on the same side
    gss = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=7)
    tr, te = next(gss.split(X, y, g))
    print(f"Train={len(tr)}  Test={len(te)}  (test has {len(set(g[te]))} unseen groups)")

    comparison, models = {}, {}
    for name, ctor in CANDIDATES.items():
        m = ctor().fit(X[tr], y[tr])
        proba = m.predict_proba(X[te])[:, 1]
        pred = (proba >= 0.5).astype(int)
        s = scores(y[te], pred, proba)
        # grouped 5-fold CV on the whole set
        cv_pred = cross_val_predict(ctor(), X, y, groups=g, cv=GroupKFold(n_splits=5), method="predict")
        s["cv5_accuracy"] = round(accuracy_score(y, cv_pred), 4)
        s["cv5_f1"] = round(precision_recall_fscore_support(y, cv_pred, average="binary", zero_division=0)[2], 4)
        comparison[name] = s
        models[name] = (m, proba, pred)
        print(f"{name:26s} {s}")

    best = "Logistic Regression"   # chosen for explainability (coefficients -> top terms)
    model, proba, pred = models[best]
    cm = confusion_matrix(y[te], pred, labels=[0, 1])
    tn, fp, fn, tp = [int(v) for v in cm.ravel()]

    # most influential words (explainability)
    feats = model.named_steps["features"].get_feature_names_out()
    coefs = model.named_steps["clf"].coef_[0]
    word_idx = [i for i, f in enumerate(feats) if f.startswith("word__")]
    order = sorted(word_idx, key=lambda i: coefs[i])
    top_fake = [(feats[i][6:], round(float(coefs[i]), 3)) for i in order[::-1][:12]]
    top_genuine = [(feats[i][6:], round(float(coefs[i]), 3)) for i in order[:12]]

    # final model: refit on ALL data for deployment
    final = CANDIDATES[best]().fit(X, y)
    joblib.dump(final, OUT / "model.pkl")

    metrics = {
        "model": best, "dataset_rows": int(len(df)), "fake_rows": int(y.sum()), "genuine_rows": int((1 - y).sum()),
        "train_rows": int(len(tr)), "test_rows": int(len(te)), "split": "group-aware 75/25 (unseen templates in test)",
        "test_metrics": comparison[best], "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "comparison": comparison, "top_fake_terms": top_fake, "top_genuine_terms": top_genuine,
        "note": "Synthetic/hand-written starter dataset. Metrics describe this dataset, not real-world traffic.",
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4.2, 3.8))
        ax.imshow(cm, cmap="Blues")
        for (i, j), v in np.ndenumerate(cm):
            ax.text(j, i, str(v), ha="center", va="center", fontsize=16, color="white" if v > cm.max() / 2 else "black")
        ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
        ax.set_xticklabels(["Genuine", "Fake"]); ax.set_yticklabels(["Genuine", "Fake"])
        ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.set_title("Confusion matrix (test set)")
        fig.tight_layout(); fig.savefig(OUT / "confusion_matrix.png", dpi=150)
    except Exception as e:
        print("Could not draw confusion matrix:", e)

    print("\nSaved model + metrics. Confusion matrix:", dict(tn=tn, fp=fp, fn=fn, tp=tp))
    print("Top 'fake' words:", [w for w, _ in top_fake])
    print("Top 'genuine' words:", [w for w, _ in top_genuine])


if __name__ == "__main__":
    main()
