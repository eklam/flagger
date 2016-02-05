import stackexchange as stackex
from Question import Question
import webbrowser
import BaseHTTPServer
import threading
from time import sleep
import SocketServer
from urlparse import parse_qs, urlparse
import StackOverflowConfig as config


class StackOverflowAdapter:
    def __init__(self):
        self._load_config()

        self.access_token = None
        self.so = stackex.Site(stackex.StackOverflow, self.app_key)

    def _load_config(self):
        self.app_key = config.app_key
        self.client_id = config.client_id
        self.auth_expiry_scope = config.auth_expiry_scope
        self.auth_return_uri = config.auth_return_uri
        self.auth_access_token_file_path = config.auth_access_token_file_path

    def get_body_from_so(self, questions):
        page_size = 100
        start = 0
        end = page_size

        page = questions[start:end]
        while page and len(page) > 0:

            ids = [q.id for q in page]

            sleep(1)
            all_questions = self.so.questions(ids=ids, filter='withbody')

            for soq in all_questions:
                q = filter(lambda x: x.id == soq.id, page)
                if q and q[0]:
                    q[0].set_text(soq)

            start += page_size
            end += page_size

            page = questions[start:end]

        return questions

    def get_recent_questions(self, number_of_questions=100, filter='withbody'):
        questions = []
        for api_question in self.so.questions(order=stackex.DESC,
                                              sort=stackex.Sort.Creation,
                                              pagesize=number_of_questions,
                                              page=1,
                                              filter=filter,
                                              tagged='javascript'):
            if not self.is_question_already_closed(api_question):
                try:
                    question = Question.from_api(api_question)
                    questions.append(question)
                except KeyError:
                    # This flag don't interest to us
                    pass

            if len(questions) >= number_of_questions:
                break

        return questions

    @staticmethod
    def is_question_already_closed(api_question):
        return u'closed_reason' in api_question.json

    def add_flag(self, question_id, flag):
        if self.access_token is None:
            self.authenticate_app()

        import json
        import requests
        params = {
            'site': 'stackoverflow',
            'key': self.app_key,
            'access_token': self.access_token,
            'filter': 'default'
        }
        url_params = self.get_string_url_params_from_map(params)
        resp = requests.get(url='https://api.stackexchange.com/2.2/questions/%(question_id)s/flags/options' % locals(),
                            params=params)

        print json.loads(resp.text)

    def authenticate_app(self):
        access_token_file_path = self.auth_access_token_file_path
        try:
            self.access_token = self.read_access_token_from_file(access_token_file_path)
            raise 'test'
        except Exception:
            self.start_web_server()

            so_auth_params = {
                'client_id': self.client_id,
                'scope': self.auth_expiry_scope,
                'redirect_uri': self.auth_return_uri
            }
            self.access_token = self.read_access_token_from_webbrowser(so_auth_params)

        self.store_access_token_in_file(access_token_file_path)

    @staticmethod
    def read_access_token_from_file(access_token_file_path):
        with open(access_token_file_path, "r") as access_token_file:
            return access_token_file.read()

    @staticmethod
    def start_web_server():
        thread = threading.Thread(target=StackOverfowAdapter.run_web_server, args=())
        thread.daemon = True
        thread.start()

        sleep(5)

    @staticmethod
    def run_web_server():
        port = 8000
        httpd = SocketServer.TCPServer(("", port), OAuthRequestHandler)
        httpd.serve_forever()

    def read_access_token_from_webbrowser(self, so_auth_params):
        webbrowser.open('https://stackexchange.com/oauth/dialog?' + self.get_string_url_params_from_map(so_auth_params))

        while self.access_token is None:
            sleep(1)

        return self.access_token

    @staticmethod
    def get_string_url_params_from_map(map_params):
        return '&'.join([key + '=' + value for key, value in map_params.iteritems()])

    def store_access_token_in_file(self, access_token_file_path):
        with open(access_token_file_path, "w") as access_token_file:
            access_token_file.write(self.access_token)

    def set_access_token(self, access_token):
        if type(access_token) is not str or len(access_token) == 0:
            raise ValueError('access_token is invalid')
        self.access_token = access_token


adapter = StackOverfowAdapter()


class OAuthRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            query = urlparse(self.path).query
            params = parse_qs(query)
            access_token = params['access_token'][0]
            adapter.set_access_token(access_token)

            self.render_ok_page()

        except KeyError:
            self.render_redirect_page()

    def render_redirect_page(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            "<html><head><title>Title goes here.</title><script>window.location.href = window.location.hash.replace('#', '?');</script></head>")
        self.wfile.write("<body>You will be redirected soon...")
        self.wfile.write("</body></html>")

    def render_ok_page(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title><script>window.close();</script></head>")
        self.wfile.write("<body>Everything went okay")
        self.wfile.write("</body></html>")
