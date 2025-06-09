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

    def __repr__(self):
        return f'<Node {self.value}: {self.weight}>'


def get_code(node: Node, cur: str, codes: dict[str, str]):
    if node.value:  # Если это лист (символ)
        codes[node.value] = cur  # Записываем код для символа
        return
    get_code(node.left, cur + '0', codes)  # Рекурсивно идём влево (0)
    if node.right:
        get_code(node.right, cur + '1', codes)  # Рекурсивно идём вправо (1)


def create_huffman_keys(data: dict[str, float]):
    # Создаём узлы и сортируем по возрастанию веса
    nodes = [Node(value=k, weight=v) for k, v in sorted(data.items(), key=lambda x: x[1])]
    
    while len(nodes) > 1:
        # Берём два узла с наименьшими весами
        left = nodes.pop(0)
        right = nodes.pop(0)
        
        # Создаём родительский узел
        parent = Node(
            weight=left.weight + right.weight,
            left=left,
            right=right
        )
        
        # Вставляем новый узел в отсортированный список
        # (можно оптимизировать через heapq)
        nodes.append(parent)
        nodes.sort(key=lambda x: x.weight)
    
    root = nodes[0] if nodes else None
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
    codes = {}
    get_code(root, '', codes)  # Начинаем с пустой строки
    print(codes)


if __name__ == '__main__':
    main()