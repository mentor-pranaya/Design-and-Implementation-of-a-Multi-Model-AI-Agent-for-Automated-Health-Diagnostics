from models.model1_parameter_interpreter import interpret_parameter
from models.model2_health_analysis import analyze_health_patterns
from models.model3_contextual_analysis import apply_context

def run_pipeline(data, age, gender):
    interpretations = {}
    for p, v in data.items():
        interpretations[p] = interpret_parameter(p, v, age, gender)

    patterns, risk, recommendations = analyze_health_patterns(data)
    final_risk = apply_context(risk, age)

    return interpretations, patterns, final_risk, recommendations