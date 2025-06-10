import math
import re
import heapq

import pymorphy2
from django.contrib.sessions.models import Session
from django.db.models.query import QuerySet


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
        word = re.sub(r'[^\w\s-]', '', word).lower()
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


class Node:
    def __init__(
        self,
        left: 'Node' = None,
        right: 'Node' = None,
        value: str | None = None,
        weight: float | None = None
    ):
        self.left = left
        self.right = right
        self.value = value
        self.weight = weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __repr__(self):
        return f'<Node {self.value}: {self.weight}>'


def get_code(node: Node, cur: str, res: dict[str, str]):
    if node.value:
        res[node.value] = cur
        return
    get_code(node.left, cur=cur + '0', res=res)
    if node.right:
        get_code(node.right, cur=cur + '1', res=res)


def create_huffman_tree(data: dict[str, float]):
    heap = []
    for k, v in data.items():
        heapq.heappush(heap, Node(value=k, weight=v))
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        sum_node = Node(
            weight=node1.weight + node2.weight,
            left=node2,
            right=node1
        )
        heapq.heappush(heap, sum_node)
    if heap:
        root = heap[0]
    else:
        root = None
    return root


def huffman_encode(
        text: str, tf: dict[str, float]) -> tuple[str, dict[str, str]]:
    root = create_huffman_tree(tf)
    codes = {}
    out_code = []
    get_code(root, '', codes)
    for word in text.split():
        word = re.sub(r'[^\w\s-]', '', word).lower()
        out_code.append(codes.get(word, ''))
    return ''.join(out_code), codes


def huffman_decode(text: str, code: dict[str, str]) -> str:
    code_word = {v: k for k, v in code.items()}
    cword = ''
    result = ''
    for letter in text:
        cword += letter
        word = code_word.get(cword)
        if word:
            result += f' {word}'
            cword = ''
    return result.strip()
