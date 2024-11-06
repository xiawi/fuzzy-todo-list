import numpy as np
from skfuzzy import control as ctrl
from skfuzzy import membership as mf

class FuzzyPriorityScorer:
    def __init__(self):
        # antecedents
        urgency = ctrl.Antecedent(np.arange(0,10.1,.1), "urgency")
        importance = ctrl.Antecedent(np.arange(0,11), "importance")

        # consequent
        priority_score = ctrl.Consequent(np.arange(0,10.1,.1), "priority score")

        # fit vector definitions
        urgency['very low'] = mf.trimf(urgency.universe, [0,0,3])
        urgency['low'] = mf.trimf(urgency.universe, [1,3,5])
        urgency['medium'] = mf.trimf(urgency.universe, [3,5,7])
        urgency['high'] = mf.trimf(urgency.universe, [5,7,9])
        urgency['very high'] = mf.trimf(urgency.universe, [7,10,10])

        importance['very low'] = mf.trimf(importance.universe, [0,0,3])
        importance['low'] = mf.trimf(importance.universe, [1,3,5])
        importance['medium'] = mf.trimf(importance.universe, [3,5,7])
        importance['high'] = mf.trimf(importance.universe, [5,7,9])
        importance['very high'] = mf.trimf(importance.universe, [7,10,10])

        priority_score['very low'] = mf.trimf(priority_score.universe, [0,0,3])
        priority_score['low'] = mf.trimf(priority_score.universe, [1,3,5])
        priority_score['medium'] = mf.trimf(priority_score.universe, [3,5,7])
        priority_score['high'] = mf.trimf(priority_score.universe, [5,7,9])
        priority_score['very high'] = mf.trimf(priority_score.universe, [7,10,10])

        # rule definitions
        rule1 = ctrl.Rule(urgency['very low'] & importance['very low'], priority_score['very low'])
        rule2 = ctrl.Rule(urgency['very low'] & importance['low'], priority_score['low'])
        rule3 = ctrl.Rule(urgency['very low'] & importance['medium'], priority_score['low'])
        rule4 = ctrl.Rule(urgency['very low'] & importance['high'], priority_score['medium'])
        rule5 = ctrl.Rule(urgency['very low'] & importance['very high'], priority_score['medium'])

        rule6 = ctrl.Rule(urgency['low'] & importance['very low'], priority_score['low'])
        rule7 = ctrl.Rule(urgency['low'] & importance['low'], priority_score['medium'])
        rule8 = ctrl.Rule(urgency['low'] & importance['medium'], priority_score['medium'])
        rule9 = ctrl.Rule(urgency['low'] & importance['high'], priority_score['high'])
        rule10 = ctrl.Rule(urgency['low'] & importance['very high'], priority_score['high'])

        rule11 = ctrl.Rule(urgency['medium'] & importance['very low'], priority_score['low'])
        rule12 = ctrl.Rule(urgency['medium'] & importance['low'], priority_score['medium'])
        rule13 = ctrl.Rule(urgency['medium'] & importance['medium'], priority_score['medium'])
        rule14 = ctrl.Rule(urgency['medium'] & importance['high'], priority_score['high'])
        rule15 = ctrl.Rule(urgency['medium'] & importance['very high'], priority_score['high'])

        rule16 = ctrl.Rule(urgency['high'] & importance['very low'], priority_score['medium'])
        rule17 = ctrl.Rule(urgency['high'] & importance['low'], priority_score['high'])
        rule18 = ctrl.Rule(urgency['high'] & importance['medium'], priority_score['high'])
        rule19 = ctrl.Rule(urgency['high'] & importance['high'], priority_score['very high'])
        rule20 = ctrl.Rule(urgency['high'] & importance['very high'], priority_score['very high'])

        rule21 = ctrl.Rule(urgency['very high'] & importance['very low'], priority_score['high'])
        rule22 = ctrl.Rule(urgency['very high'] & importance['low'], priority_score['very high'])
        rule23 = ctrl.Rule(urgency['very high'] & importance['medium'], priority_score['very high'])
        rule24 = ctrl.Rule(urgency['very high'] & importance['high'], priority_score['very high'])
        rule25 = ctrl.Rule(urgency['very high'] & importance['very high'], priority_score['very high'])

        rules = [
            rule1, rule2, rule3, rule4, rule5, 
            rule6, rule7, rule8, rule9, rule10,
            rule11, rule12, rule13, rule14, rule15, 
            rule16, rule17, rule18, rule19, rule20,
            rule21, rule22, rule23, rule24, rule25
            ]

        # fuzzy System
        priority_scorer_ctrl = ctrl.ControlSystem(rules=rules)
        self.priority_scorer = ctrl.ControlSystemSimulation(control_system=priority_scorer_ctrl)
        
    def getPriorityScore(self, importance, urgency):
        self.priority_scorer.input["importance"] = importance
        self.priority_scorer.input["urgency"] = urgency
        self.priority_scorer.compute()
        return self.priority_scorer.output["priority score"]
        
    

# for testing

# if __name__ == "__main__":
#     priority_scorer.input["importance"] = 10
#     priority_scorer.input["urgency"] = 10
#     priority_scorer.compute()
#     print(priority_scorer.output)