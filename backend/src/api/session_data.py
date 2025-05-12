from threading import Lock


class ChatOnlySessionData:
    def __init__(self):
        self._q_and_a: [(str, str)] = []
        self._lock: Lock = Lock()
        self._references_vector = []
        self._references_regex = []

    @property
    def q_and_a(self):
        with self._lock:
            return self._q_and_a.copy()

    def append_qa(self, question: str, answer: str | None):
        with self._lock:
            self._q_and_a.append((question, answer))

    def set_last_answer(self, answer: str):
        with self._lock:
            self._q_and_a[-1] = (self._q_and_a[-1][0], answer)

    @property
    def references_vector(self):
        with self._lock:
            return self._references_vector

    @references_vector.setter
    def references_vector(self, references):
        with self._lock:
            self._references_vector = references

    @property
    def references_regex(self):
        with self._lock:
            return self._references_regex

    @references_regex.setter
    def references_regex(self, references):
        with self._lock:
            self._references_regex = references
