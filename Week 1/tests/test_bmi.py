import pytest
from Main_bmi_calculator import bmi_calculator


def test_bmi_calculation():
    bmi, category = bmi_calculator(70, 175)

    assert bmi == 22.86
    assert category == "Normal weight"

def test_underweight():
    bmi, category = bmi_calculator(50, 175)

    assert bmi == 16.33
    assert category == "Underweight"

def test_bmi_boundary_normal_under():
    bmi, category = bmi_calculator(57, 175)

    assert bmi == 18.61
    assert category == "Normal weight"


def test_bmi_boundary_normal_over():
    bmi, category = bmi_calculator(77, 175)

    assert bmi == 25.14
    assert category == "Overweight"


def test_bmi_boundary_over_obese():
    bmi, category = bmi_calculator(92, 175)

    assert bmi == 30.04
    assert category == "Obese"

def test_zero_weight():
    with pytest.raises(ValueError):
        bmi_calculator(0, 175)

def test_zero_height():
    with pytest.raises(ValueError):
        bmi_calculator(70, 0)

def test_negative_weight():
    with pytest.raises(ValueError):
        bmi_calculator(-70, 175)

def test_negative_height():
    with pytest.raises(ValueError):
        bmi_calculator(70, -175)

def test_bmi_boundary_18_5():
    bmi, category = bmi_calculator(74, 200)

    assert bmi == 18.5
    assert category == "Normal weight"

def test_bmi_boundary_25():
    bmi, category = bmi_calculator(100, 200)

    assert bmi == 25
    assert category == "Overweight"

def test_bmi_boundary_30():
    bmi, category = bmi_calculator(120, 200)

    assert bmi == 30
    assert category == "Obese"