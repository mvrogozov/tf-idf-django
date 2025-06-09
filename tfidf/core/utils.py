# import math
# import re
import heapq

# import chardet
# import pymorphy2
# from django.contrib.sessions.models import Session
# from django.db.models.query import QuerySet


# def delete_user_session(user_id: int):
#     sessions = Session.objects.all()
#     for session in sessions:
#         session_data = session.get_decoded()
#         if str(user_id) == session_data.get('_auth_user_id', None):
#             session.delete()


# def count_tf(
#     data: str,
#     min_word_len: int,
#     normalize: bool = False
# ) -> dict[str, float]:
#     freq = {}
#     text_length = 0
#     morph = pymorphy2.MorphAnalyzer()
#     for word in data.split():
#         word = re.sub(r'[^\w\s-]', '', word)
#         if len(word) < min_word_len:
#             continue
#         text_length += 1
#         if normalize:
#             word = morph.parse(word)[0].normal_form
#         freq.setdefault(word, 0)
#         freq[word] += 1
#     for word, amount in freq.items():
#         freq[word] = round(amount / text_length, 6)
#     return freq


# def count_idfs(tfs: dict[str, float], docs: QuerySet) -> dict[str, float]:
#     idfs = {}
#     docs_amount = docs.count()
#     for word, tf in tfs.items():
#         amount_docs_with_word = docs.filter(
#             word_frequency__has_key=word
#         ).count()
#         try:
#             idfs[word] = math.log(docs_amount / (amount_docs_with_word))
#         except ZeroDivisionError:
#             continue
#     return idfs


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


def print_node(node: Node):
    if not node:
        print(None)
        return
    print(node.weight)
    print(node.value)
    print('left >> ', end='')
    print_node(node.left)
    print('right >> ', end='')
    print_node(node.right)
    print('***')


def get_code(node: Node, cur: str, res: dict[str, str]):
    if node.value:
        res[node.value] = cur
        return
    get_code(node.left, cur=cur + '0', res=res)
    if node.right:
        get_code(node.right, cur=cur + '1', res=res)


def create_huffman_keys(data: dict[str, float]):
    # data = [Node(value=k, weight=v) for k, v in sorted(
    #     data.items(), key=lambda x: -x[1]
    # )]
    heap = []
    for k, v in data.items():
        heapq.heappush(heap, Node(value=k, weight=v))
    while len(heap) > 1:
        # node1 = data.pop()
        # node2 = data.pop()
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        sum_node = Node(
            weight=node1.weight + node2.weight,
            left=node2,
            right=node1
        )
        #data = [sum_node] + data
        heapq.heappush(heap, sum_node)
    if heap:
        root = heap[0]
    else:
        root = None
    # print(init_data)
    # print_node(root)
    return root


def main():
    data = {
        "тут": 0.090909,
        "ухо": 0.090909,
        "ключ": 0.272727,
        "банан": 0.090909,
        "батон": 0.090909,
        "дверь": 0.181818,
        "зверь": 0.090909,
        "поезд": 0.090909
    }

    root = create_huffman_keys(data)
    result = {}
    get_code(root, '', result)
    print(result)


if __name__ == '__main__':
    main()
