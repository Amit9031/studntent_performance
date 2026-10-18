"""
Intelligent Academic Risk Prediction Service.

Provides two-tier academic risk analysis:
1. Transparent, deterministic rule-based evaluation based on attendance and average marks.
2. Supervised Machine Learning model (Random Forest / Logistic Regression) using Scikit-Learn
   trained on engineered student performance features.

Maintains strict separation between database CRUD operations and predictive analytics.
"""

import logging
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from database.connection import get_database

logger = logging.getLogger(__name__)


class AcademicRiskPredictor:
    """Predictive service for identifying students requiring academic interventions."""

    def __init__(self, db=None):
        self._db = db
        self.model = None
        self.feature_names = ["attendance", "avg_marks", "semester", "num_courses", "num_skills"]
        self.metrics = None
        self.is_trained = False

    @property
    def db(self):
        return self._db if self._db is not None else get_database()

    # ==============================================================
    # 1. TRANSPARENT RULE-BASED EVALUATION
    # ==============================================================
    @staticmethod
    def evaluate_rule_based_risk(attendance, avg_marks, semester=1):
        """
        Transparent academic risk tiering:
        - High Risk: attendance < 60% OR avg_marks < 40
        - Moderate Risk: 60% <= attendance < 75% OR 40 <= avg_marks < 55
        - Low Risk (Good Standing): attendance >= 75% AND avg_marks >= 55
        """
        attendance = float(attendance)
        avg_marks = float(avg_marks)

        reasons = []
        if attendance < 60.0:
            reasons.append("Critical attendance shortage (<60%)")
        elif attendance < 75.0:
            reasons.append("Borderline attendance (<75% University norm)")

        if avg_marks < 40.0:
            reasons.append("Critical academic failure (Average < 40%)")
        elif avg_marks < 55.0:
            reasons.append("Below-average academic standing (<55%)")

        if attendance < 60.0 or avg_marks < 40.0:
            risk_level = "High Risk"
            recommendation = "Immediate faculty mentoring and academic counseling required."
        elif attendance < 75.0 or avg_marks < 55.0:
            risk_level = "Moderate Risk"
            recommendation = "Monitor attendance and schedule remedial tutoring."
        else:
            risk_level = "Low Risk"
            recommendation = "Satisfactory progress. Eligible for advanced electives."

        return {
            "risk_level": risk_level,
            "is_at_risk": risk_level in ["High Risk", "Moderate Risk"],
            "reasons": reasons if reasons else ["Consistent attendance and satisfactory marks."],
            "recommendation": recommendation
        }

    # ==============================================================
    # 2. MACHINE LEARNING MODEL (Scikit-Learn)
    # ==============================================================
    def _extract_features_and_labels(self):
        """
        Extracts feature vectors and target labels from MongoDB student documents.
        Ground truth label: 1 if at-risk (attendance < 75 or avg_marks < 45), else 0.
        """
        students = list(self.db["students"].find({}))
        if len(students) < 10:
            return None, None

        X = []
        y = []

        for s in students:
            attendance = float(s.get("attendance", 0.0))
            marks = s.get("marks", {})
            marks_vals = list(marks.values()) if isinstance(marks, dict) else []
            avg_marks = float(np.mean(marks_vals)) if marks_vals else 0.0
            semester = int(s.get("semester", 1))
            num_courses = len(marks_vals)
            skills = s.get("skills", [])
            num_skills = len(skills) if isinstance(skills, list) else 0

            # Target definition: 1 if student requires academic intervention
            target = 1 if (attendance < 75.0 or avg_marks < 45.0) else 0

            X.append([attendance, avg_marks, semester, num_courses, num_skills])
            y.append(target)

        return np.array(X), np.array(y)

    def train_model(self):
        """
        Trains a Random Forest classifier using an 80/20 train/test split.
        Evaluates metrics on the held-out test split.
        """
        X, y = self._extract_features_and_labels()
        if X is None or len(X) < 10:
            logger.warning("Insufficient data to train machine learning model.")
            return {
                "success": False,
                "message": "Insufficient student records (minimum 10 required) to train model."
            }

        # Check class balance
        unique_classes = np.unique(y)
        if len(unique_classes) < 2:
            # Need at least two classes to train classifier
            return {
                "success": False,
                "message": "Dataset must contain both at-risk and regular students to train classifier."
            }

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        model = RandomForestClassifier(
            n_estimators=50,
            max_depth=4,
            random_state=42
        )
        model.fit(X_train, y_train)

        # Predictions on held-out test set
        y_pred = model.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))

        # Feature importances
        importances = dict(zip(self.feature_names, [round(float(v), 4) for v in model.feature_importances_]))

        self.model = model
        self.is_trained = True
        self.metrics = {
            "training_samples": len(X_train),
            "testing_samples": len(X_test),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "feature_importances": importances,
            "algorithm": "RandomForestClassifier",
            "limitation_note": (
                "Note: Trained on synthetic academic dataset for CSE494 coursework demonstration. "
                "Real-world deployments require longitudinal semester cohorts and ethical safeguards."
            )
        }

        logger.info("Academic risk ML model trained successfully. Test Accuracy: %s", self.metrics["accuracy"])
        return {"success": True, "metrics": self.metrics}

    def predict_for_student(self, student_doc):
        """
        Combines rule-based reasoning and ML prediction for a given student record.
        """
        attendance = float(student_doc.get("attendance", 0.0))
        marks = student_doc.get("marks", {})
        marks_vals = list(marks.values()) if isinstance(marks, dict) else []
        avg_marks = float(np.mean(marks_vals)) if marks_vals else 0.0
        semester = int(student_doc.get("semester", 1))
        num_courses = len(marks_vals)
        skills = student_doc.get("skills", [])
        num_skills = len(skills) if isinstance(skills, list) else 0

        # 1. Rule-based assessment
        rule_eval = self.evaluate_rule_based_risk(attendance, avg_marks, semester)

        # 2. ML Prediction (if trained)
        ml_prediction = None
        if not self.is_trained:
            self.train_model()

        if self.is_trained and self.model is not None:
            features = np.array([[attendance, avg_marks, semester, num_courses, num_skills]])
            prob = self.model.predict_proba(features)[0]
            # Probability of class 1 (At Risk)
            at_risk_prob = round(float(prob[1]) if len(prob) > 1 else 0.0, 3)
            ml_prediction = {
                "predicted_label": "At Risk" if at_risk_prob >= 0.5 else "Normal",
                "risk_probability": at_risk_prob,
                "confidence_score": round(max(prob) * 100, 1)
            }

        return {
            "student_id": student_doc.get("_id"),
            "name": student_doc.get("name"),
            "attendance": attendance,
            "avg_marks": round(avg_marks, 2),
            "rule_evaluation": rule_eval,
            "ml_prediction": ml_prediction,
            "features_used": {
                "attendance": attendance,
                "avg_marks": round(avg_marks, 2),
                "semester": semester,
                "num_courses": num_courses,
                "num_skills": num_skills
            }
        }
