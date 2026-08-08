from typing import Tuple

def bmi_calculator(w:int, h_cm:int) -> Tuple[float, str]:
    if w <= 0:
        raise ValueError("Weight must be greater than zero.")

    if h_cm <= 0:
        raise ValueError("Height must be greater than zero.")
    
    height_m = h_cm/100
    bmi = w / height_m ** 2
    bmi_round = round(bmi, 2)
    if bmi < 18.5:
        category = 'Underweight'
    elif bmi >= 18.5 and bmi <= 24.9:
        category = 'Normal weight'
    elif bmi >= 25.0 and bmi <= 29.9:
        category = 'Overweight'
    else:
        category = 'Obese'
    return bmi_round, category

if __name__ == "__main__": #tells python to Only run the input section if I'm directly running this file.
    weight = int(input('Enter your weight in kg: '))
    height = int(input('Enter your weight in cm: '))
    bmi_round, category = bmi_calculator(weight, height)
    print(f'Your BMI is {bmi_round}')
    print(f'You are {category}')

