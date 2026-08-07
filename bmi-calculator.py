#weight = input('What is your weight in kilograms(kg)? ')
#if weight == '':
 #   print("Value cannot be empty")
#else:
 #   new_weight = int(weight)
#height = float(input('What is your height in centimeters(cm)? '))
#height_m = height/100
#bmi_number = new_weight / height_m**2
#rounded = round(bmi_number, 2)
#print(f'Your BMI is {rounded}')
#if bmi_number < 18.5:
 #   print('You are Underweight.')
#elif bmi_number >= 18.5 and bmi_number <= 24.9:
 #   print('You are Normal weight.')
#elif bmi_number >= 25.0 and bmi_number <= 29.9:
 #   print('You are Overweight')
#else:
 #   print('You are Obese')

def bmi_calculator(weight: float, height_cm:float):
    height_m = height_cm/100
    bmi = weight / (height_cm ** 2)
    return round(bmi, 2)

def bmi_class(bmi: float):
    if bmi < 18.5:
        return"You are Underweight."
    elif bmi >= 18.5 and bmi <= 24.9:
        return"You are Normal weight."
    elif bmi >= 25.0 and bmi <= 29.9:
        return"You are Overweight."
    else:
        return"You are Obese."


    

