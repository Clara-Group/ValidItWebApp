import yaml
import numpy as np

class QuestionsSource:
    questions_count = 1

    def __init__(self, file='data/Questions.yml') -> None:
        with open(file) as f:
            questions = yaml.load(f, Loader=yaml.FullLoader)
        
        self.irrelevantQuestions = np.array(questions['Irrelevant']).tolist()
        self.controlQuestions = np.array(questions['ControlQuestions']).tolist()
        np.random.shuffle(self.irrelevantQuestions)
        np.random.shuffle(self.controlQuestions)        

    def getNextQuestion(self):
        count = self.questions_count
        self.questions_count = self.questions_count + 1
        if count % 3 == 0:
            return self.controlQuestions.pop(0)
        
        return self.irrelevantQuestions.pop(0)