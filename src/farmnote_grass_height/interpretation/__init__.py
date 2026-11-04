"""SHAP-based global interpretation."""

from .shap_analysis import ShapImportance, compute_shap_importance, consolidate_top_features

__all__ = ["ShapImportance", "compute_shap_importance", "consolidate_top_features"]
