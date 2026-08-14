from __future__ import annotations

from typing import Any

from .predictive import (
    PredictionTarget,
    PredictivePrediction,
    PredictiveRow,
    verify_predictive_receipt_binding,
)


def verify_predictive_prediction_binding(
    prediction: PredictivePrediction,
    row: PredictiveRow,
    model: Any,
) -> None:
    """Fully bind a prediction to its receipts, row, and model artifact.

    `verify_predictive_receipt_binding` proves provenance for one receipt. This
    verifier adds the missing aggregate invariant: each receipt's value must
    equal the corresponding value carried by the `PredictivePrediction`.
    """

    if prediction.logical_operation_id != row.logical_operation_id:
        raise ValueError("prediction logical operation does not match row")
    if prediction.model_id != model.model_id:
        raise ValueError("prediction model_id does not match model")

    receipt_by_target = {
        receipt.prediction_target: receipt for receipt in prediction.receipts
    }
    expected_targets = {
        PredictionTarget.FUTURE_NET_EDGE_BPS,
        PredictionTarget.SURVIVAL_PROBABILITY,
        PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY,
    }
    if set(receipt_by_target) != expected_targets:
        raise ValueError("prediction receipts do not cover the canonical target set")

    expected_values = {
        PredictionTarget.FUTURE_NET_EDGE_BPS: prediction.predicted_future_net_edge_bps,
        PredictionTarget.SURVIVAL_PROBABILITY: prediction.survival_probability,
        PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY: (
            prediction.positive_realized_pnl_probability
        ),
    }

    for target in (
        PredictionTarget.FUTURE_NET_EDGE_BPS,
        PredictionTarget.SURVIVAL_PROBABILITY,
        PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY,
    ):
        receipt = receipt_by_target[target]
        verify_predictive_receipt_binding(receipt, row, model)
        if receipt.prediction_value != expected_values[target]:
            raise ValueError(
                f"receipt prediction value does not match prediction for {target.value}"
            )
