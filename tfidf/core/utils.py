from django.contrib.sessions.models import Session
from django.db.models.query import QuerySet
import pymorphy2
import chardet
import re
import math


def delete_user_session(user_id: int):
    sessions = Session.objects.all()
    for session in sessions:
        session_data = session.get_decoded()
        if str(user_id) == session_data.get('_auth_user_id', None):
            session.delete()


def count_tf(
    data: str,
    min_word_len: int,
    normalize: bool = False
) -> dict[str, float]:
    freq = {}
    text_length = 0
    morph = pymorphy2.MorphAnalyzer()
    for word in data.split():
        word = re.sub(r'[^\w\s-]', '', word)
        if len(word) < min_word_len:
            continue
        text_length += 1
        if normalize:
            word = morph.parse(word)[0].normal_form
        freq.setdefault(word, 0)
        freq[word] += 1
    for word, amount in freq.items():
        freq[word] = round(amount / text_length, 6)
    return freq


def count_idfs(tfs: dict[str, float], docs: QuerySet) -> dict[str, float]:
    idfs = {}
    docs_amount = docs.count()
    for word, tf in tfs.items():
        amount_docs_with_word = docs.filter(
            word_frequency__has_key=word
        ).count()
        try:
            idfs[word] = math.log(docs_amount / (amount_docs_with_word))
        except ZeroDivisionError:
            continue
    return idfs
