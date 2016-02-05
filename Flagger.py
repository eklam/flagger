import numpy
from Question import Question


class Flagger(object):

    def __init__(self, vectorizer, clf):
        self.vectorizer = vectorizer
        self.clf = clf

    def predict_class(self, questions):

        ids = []
        texts = []
        classes = []
        for q in questions:
            ids.append(q.id)
            texts.append(q.text)
            classes.append(q.flag_id)

        x_features = self.vectorizer.transform(numpy.array(texts))
        predictions = self.clf.predict(x_features.toarray())

        return [Question.flag_from_id(p) for p in predictions]
