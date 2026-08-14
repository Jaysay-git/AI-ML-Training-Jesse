# AI-ML-Training-Jesse
Projects and assignments for my 12-week AI/ML Engineering training.
A Python utility that calculates a person's Body Mass Index (BMI)
using their weight and height, and assigns a BMI category.

## BMI Categories
| BMI | Category |
|---|---|
| Below 18.5 | Underweight |
| 18.5 – 24.9 | Normal weight |
| 25.0 – 29.9 | Overweight |
| 30.0 and above | Obese |

## Requirements
- Python 3
- pytest

## Installation
Clone the repository and install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
The calculator requires:

- Weight in kilograms (kg)
- Height in centimetres (cm)

### Example
```text
Enter your weight in kg: 70
Enter your height in cm: 175

Your BMI is 22.86
Category: Normal weight
```

## Error Handling
The calculator rejects zero or negative values for weight and height by raising a `ValueError`.

For example:
- Weight of 0 kg → Error
- Negative weight → Error
- Height of 0 cm → Error
- Negative height → Error

## Testing
The project uses pytest for automated testing.
The test suite covers:

- BMI calculations
- BMI categories
- Zero and negative weight
- Zero and negative height
- BMI category boundaries at 18.5, 25.0, and 30.0
Run the test suite with:

```bash
pytest
