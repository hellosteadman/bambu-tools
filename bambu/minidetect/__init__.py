from threading import local
from os import path

SEARCH_STRINGS_FILENAME = path.join(path.dirname(__file__), 'fixtures', 'search_strings.txt')

_thread_locals = local()
def get_current_request():
	return getattr(_thread_locals, 'request', None)