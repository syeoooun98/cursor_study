def calc_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "저체중"
    elif bmi < 25:
        return "정상체중"
    elif bmi < 30:
        return "비만"
    else:
        return "고도비만"
