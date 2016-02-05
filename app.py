from time import sleep
from Question import Question
import main
import webbrowser

from StackOverflowAdapter import adapter as soAdapter


def process(question, predicted_flag):
    if predicted_flag == 'no flag':
        pass
    if predicted_flag == 'no-flag':
        pass
    else:
        webbrowser.open('http://stackoverflow.com/questions/' + str(question.id) + '#' + predicted_flag)
        raw_input('press to get next')
        #soAdapter.add_flag(question.id, predicted_flag)


def do():
    while True:
        recent_questions = soAdapter.get_recent_questions()
        predicted_flags = flagger.predict_class(recent_questions)
        for q, f in zip(recent_questions, predicted_flags):
            process(q, f)

        sleep(60)


flagger = main.get_trained_classifier()
do()
