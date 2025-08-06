import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from api.main import calculate_tax_details, calculate_gross_from_net


def test_calculate_tax_details_example():
    result = calculate_tax_details(100000)
    assert result["salaire_net"] == 92400
    assert result["total_prelevements"] == result["total_cotisations"] + result["total_impot"]


def test_calculate_gross_from_net_example():
    desired_net = 92400
    result = calculate_gross_from_net(desired_net)
    assert abs(result["salaire_brut_requis"] - 100000) < 1000
    assert result["total_prelevements"] == result["total_cotisations"] + result["total_impot"]
    net_from_gross = calculate_tax_details(result["salaire_brut_requis"])["salaire_net"]
    assert net_from_gross == pytest.approx(desired_net, abs=500)
