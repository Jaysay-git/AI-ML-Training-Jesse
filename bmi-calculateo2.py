def bmi_calculator(weight, height):
    weight = int(input('Enter your weight in kg: '))
    height = int(input('Enter your weight in cm: '))
    bmi = weight / height ** 2
    return bmi