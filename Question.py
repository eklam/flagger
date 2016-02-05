import text_helper


class Question(object):
    flags = {
        'no-flag': 0,

        'duplicate': 1,
        'exact duplicate': 1,

        'off topic': 2,
        'off-topic': 2,

        'unclear': 3,

        'too broad': 4,
        'too-broad': 4,

        'primarily opinion-based': 5,
        'opinion-based': 5,
    }
    inv_map = {}

    def __init__(self):
        self.id = 0
        self.text = ''
        self.flag = ''
        self.flag_id = -1

    def set_text(self, question):
        self.text = text_helper.prepare_text(question.body.encode('ascii', errors='replace'))

    @staticmethod
    def from_api(api_question):
        q = Question()
        q.id = api_question.id
        q.set_text(api_question)

        try:
            q.flag = api_question.json[u'closed_reason']
        except KeyError:
            q.flag = 'no-flag'

        q.flag_id = Question.flags[q.flag]

        return q

    @staticmethod
    def from_csv_arr(csv_question):
        q = Question()

        q.id = int(csv_question[1])
        q.text = csv_question[2]  # Text must be retrieved from API
        q.flag = csv_question[0]
        q.flag_id = Question.flags[q.flag]

        return q

    @staticmethod
    def flag_from_id(flag_id):
        if len(Question.inv_map) <= 0:
            for k, v in Question.flags.iteritems():
                Question.inv_map[v] = Question.inv_map.get(v, [])
                Question.inv_map[v].append(k)
        return Question.inv_map[flag_id][0]
