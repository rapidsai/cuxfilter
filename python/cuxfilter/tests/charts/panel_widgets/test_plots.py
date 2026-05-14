# SPDX-FileCopyrightText: Copyright (c) 2019-2026, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os

import pandas as pd
import pytest

from cuxfilter.charts.panel_widgets.plots import (
    NumberChart,
    _evaluate_number_chart_expression,
)


def test_number_chart_expression_allows_dataframe_arithmetic():
    data = pd.DataFrame({"key": [1, 2, 3], "val": [10, 20, 30]})

    result = _evaluate_number_chart_expression("(key * val) + 1", data)

    assert result.tolist() == [11, 41, 91]


def test_number_chart_rejects_python_call_expressions(monkeypatch):
    data = pd.DataFrame({"key": [1, 2, 3]})
    system_called = False

    def fake_system(command):
        nonlocal system_called
        system_called = True
        return 0

    monkeypatch.setattr(os, "system", fake_system)
    chart = NumberChart(
        expression="__import__('os').system('echo exploited') or key",
        aggregate_fn="mean",
    )

    with pytest.raises(ValueError, match="only supports arithmetic"):
        chart.generate_chart(data)

    assert system_called is False
