from Question import Question
import cPickle
import os.path
import csv
import chardet

import StackOverflowAdapter

flags = dict()

raw_questions_file_name = r'raw_questions.pickle'

questions_per_flag = 300

dict_questions_pre_flag = (1 + max(Question.flags.values())) * [0]


def process(questions, result):
    processed = 0

    for x in result:

        if not hasattr(x, 'body'):
            continue

        try:
            q = Question(x)
        except KeyError:
            continue

        processed += 1

        if processed % 100 == 0:
            print 'processed ', processed

        if dict_questions_pre_flag[q.flag_id] >= questions_per_flag:
            continue

        questions.append(q)

        dict_questions_pre_flag[q.flag_id] += 1

        if sum(dict_questions_pre_flag) % 100 == 0:
            print 'counting ', sum(dict_questions_pre_flag)
            print '  here it is: ', dict_questions_pre_flag

        if sum(dict_questions_pre_flag) >= len(dict_questions_pre_flag) * questions_per_flag:
            break


def store(file_name, data):
    cPickle.dump(data, open(file_name, "wb"))


def remove_non_ascii(s):
    return "".join(i for i in s if ord(i) < 128)


def correct_text_encodings(data):
    x_features, y_features, ids = data[0], data[1], data[2]

    new_x_features = []

    for text in x_features:
        try:
            text.decode('ascii')
        except UnicodeError:
            print 'making correction'
            text = remove_non_ascii(text)

            encoding = chardet.detect(text)
            text = text.decode(encoding['encoding']).encode('ascii')

        new_x_features.append(text)

    return new_x_features, y_features, ids


def load_from_csv():
    if os.path.isfile(raw_questions_file_name):
        print 'loading from pickle'
        data = cPickle.load(open(raw_questions_file_name, "rb"))

        # data = correct_text_encodings(data)

        # store(raw_questions_file_name, data)

        return data

    with open('sample_data\\30478_questions.csv', 'rb') as f:
        print 'reading csv'
        reader = csv.reader(f)
        next(reader, None)  # header

        data = list(reader)

    questions = [Question.from_csv_arr(x) for x in data]
    questions = StackOverflowAdapter.get_body_from_so(questions)
    questions = prepare_data_set(questions)

    store(raw_questions_file_name, questions)

    return questions


def prepare_data_set(questions):
    x_features = []
    y_features = []
    ids = []
    for q in questions:
        x_features.append(q.text)
        y_features.append(q.flag_id)
        ids.append(q.id)

    return x_features, y_features, ids


def write_data_csv(questions):
    with open('test.csv', 'wb') as fp:
        a = csv.writer(fp, delimiter=',')
        data = []
        data.append(['Id', 'Flag'])
        for q in questions:
            data.append([q.id, q.flag])

        a.writerows(data)
