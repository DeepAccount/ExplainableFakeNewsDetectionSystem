from allennlp.predictors.predictor import Predictor
predictor = Predictor.from_path("/home/deepk/AllenNLP/decomposable-attention-elmo-2020.04.09.tar.gz")

"""
p = predictor.predict(
    premise="Two women are wandering along the shore drinking iced tea.",
    hypothesis="Two women are sitting on a blanket near some rocks talking about politics."
)
print("True Prob " + str(p.get('label_probs')[0]))
print("False Prob " + str(p.get('label_probs')[1]))

p = predictor.predict(
    premise="Disha ravi was arrested in bangalore by Delhi police",
    hypothesis="Disha  was arrested in bangalore"
)
print("True Prob " + str(p.get('label_probs')[0]))
print("False Prob " + str(p.get('label_probs')[1]))
"""

def fake_entailment ( premise , hypothesis):
    print(premise)
    print(hypothesis)
    prediction = predictor.predict(premise=premise, hypothesis=hypothesis)
    print("True Prob " + str(prediction.get('label_probs')[0]))
    print("False Prob " + str(prediction.get('label_probs')[1]))
    if prediction.get('label_probs')[0] > prediction.get('label_probs')[1]:
        return "NOT FAKE "
    else:
        return "FAKE "
