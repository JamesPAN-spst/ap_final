"""生成 15 套 AP2 模拟卷。

新版生成器不再从少量模板中随机抽题,而是按每套卷的考点蓝图
固定安排 24 个题位,再用可复现随机参数生成具体数据。
"""

import json
import math
import os
import random
from collections import deque


CH1, CH2, CH3, CH4 = 1, 2, 3, 4
QUESTIONS_PER_SET = 24


def shuffled_choices(rng, correct, distractors):
    choices = [correct] + list(distractors)
    rng.shuffle(choices)
    return choices, chr(ord('A') + choices.index(correct))


def make_question(chapter, topic, difficulty, qtype, statement_md, answer, explanation_md, choices=None):
    question = {
        'chapter': chapter,
        'topic': topic,
        'difficulty': difficulty,
        'type': qtype,
        'statement_md': statement_md,
        'answer': str(answer),
        'explanation_md': explanation_md,
    }
    if choices is not None:
        question['choices'] = choices
    return question


def mcq(rng, chapter, topic, difficulty, statement_md, correct, distractors, explanation_md):
    choices, answer = shuffled_choices(rng, correct, distractors)
    return make_question(chapter, topic, difficulty, 'mcq', statement_md, answer, explanation_md, choices)


def code_question(chapter, topic, difficulty, statement_md, solution_md, answer='见参考实现/伪代码'):
    return make_question(chapter, topic, difficulty, 'code', statement_md, answer, solution_md)


def set_repr(values):
    values = sorted(values)
    return '{' + ', '.join(map(str, values)) + '}' if values else 'set()'


def fib_call_count(n, cache={0: 1, 1: 1}):
    if n not in cache:
        cache[n] = fib_call_count(n - 1) + fib_call_count(n - 2) + 1
    return cache[n]


def fast_power_mult_count(n):
    if n <= 1:
        return 0
    if n % 2:
        return 1 + fast_power_mult_count(n - 1)
    return 1 + fast_power_mult_count(n // 2)


def bfs_order(graph, start):
    seen = set()
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for nxt in sorted(graph[node]):
            if nxt not in seen:
                queue.append(nxt)
    return order


def bfs_distance(graph, start, target):
    queue = deque([(start, 0)])
    seen = set()
    while queue:
        node, distance = queue.popleft()
        if node == target:
            return distance
        if node in seen:
            continue
        seen.add(node)
        for nxt in sorted(graph[node]):
            if nxt not in seen:
                queue.append((nxt, distance + 1))
    return None


def graph_literal(graph):
    parts = [f"{node!r}: {sorted(neighbours)!r}" for node, neighbours in graph.items()]
    return '{' + ', '.join(parts) + '}'


def tree_size(tree):
    return 1 + sum(tree_size(child) for child in tree[1:])


def tree_height(tree):
    if len(tree) == 1:
        return 1
    return 1 + max(tree_height(child) for child in tree[1:])


def decimal_repr(x, p):
    sign = '-' if x < 0 else ''
    digits = str(abs(x))
    if p == 0:
        return sign + digits + '.'
    if len(digits) < p + 1:
        digits = '0' * (p + 1 - len(digits)) + digits
    return sign + digits[:-p] + '.' + digits[-p:]


BASE_GRAPH = {
    'A': {'B', 'C'},
    'B': {'A', 'D'},
    'C': {'A', 'D', 'E'},
    'D': {'B', 'C', 'F'},
    'E': {'C', 'F'},
    'F': {'D', 'E'},
}

TRIANGLE_GRAPH = {
    'A': {'B', 'C'},
    'B': {'A', 'C', 'D'},
    'C': {'A', 'B', 'E'},
    'D': {'B'},
    'E': {'C'},
}

DISCONNECTED_GRAPH = {
    'A': {'B'},
    'B': {'A'},
    'C': {'D'},
    'D': {'C'},
    'E': set(),
}

SAMPLE_TREES = [
    ['r', ['a'], ['b', ['c'], ['d']], ['e']],
    [4, [2, [2], [5]], [7], [4, [4]]],
    [5, [3, [1], [2]], [8, [4]], [0]],
    ['x', ['x'], ['y', ['x'], ['z']], ['z', ['z']]],
]


# ======================================================================
# CH1 - Types Python avances
# ======================================================================
def q_complex_attr(rng):
    a, b = rng.choice([(3, 4), (-2, 5), (5, -12), (8, 15)])
    z = complex(a, b)
    return make_question(
        CH1, 'complex / attributs', 2, 'short',
        f"设 `z = {a}{'+' if b >= 0 else ''}{b}j`。请写出 `z.real z.imag abs(z)` 三个值,用空格分隔。",
        f'{float(a)} {float(b)} {abs(z)}',
        f'复数的 `.real` 与 `.imag` 都是浮点数;`abs(z)` 是模长。这里模长为 `sqrt({a}^2+{b}^2) = {abs(z)}`。',
    )


def q_complex_square(rng):
    a, b = rng.choice([(1, 2), (2, -3), (-1, 4), (3, 1)])
    z = complex(a, b)
    answer = str(z * z).replace('(', '').replace(')', '')
    return make_question(
        CH1, 'complex / calcul', 2, 'short',
        f"计算 `(z*z)` 的结果,其中 `z = {a}{'+' if b >= 0 else ''}{b}j`。请用 Python 复数格式填写,例如 `-3+4j`。",
        answer,
        f'按 `(a+bj)^2 = (a^2-b^2) + 2ab j`。代入 `{a}` 和 `{b}` 得 `{answer}`。',
    )


def q_rounding_tuple(rng):
    x = rng.choice([-3.7, -2.5, -1.2, 2.5, 3.7])
    result = (int(x), math.floor(x), math.ceil(x), round(x))
    return make_question(
        CH1, 'arrondis', 2, 'short',
        '填写下面代码的输出,按 Python 元组格式填写。\n\n'
        f'```python\nimport math\nx = {x}\nprint((int(x), math.floor(x), math.ceil(x), round(x)))\n```',
        result,
        '`int` 向 0 截断,`floor` 向负无穷,`ceil` 向正无穷,`round` 对 .5 使用偶数舍入。'
        f'所以输出 `{result}`。',
    )


def q_base_conversion_trace(rng):
    n = rng.randint(9, 31)
    binary = format(n, 'b')
    other = rng.randint(2, 8)
    result = int(binary, 2) + 0b11 + int(str(other), 10)
    return make_question(
        CH1, 'bases / int(s, base)', 2, 'short',
        '下面代码会输出什么?\n\n'
        f'```python\na = int({binary!r}, 2)\nb = 0b11\nc = int({str(other)!r})\nprint(a + b + c)\n```',
        result,
        f'`int({binary!r}, 2)` 把二进制字符串转回 `{n}`;`0b11` 是整数 3;`int({str(other)!r})` 默认十进制。总和是 `{result}`。',
    )


def q_bin_string_trace(rng):
    n = rng.choice([7, 13, 19, 31])
    m = rng.choice([3, 5, 6])
    value = bin(n) + str(0b101 + m)
    return make_question(
        CH1, 'bases / chaines', 2, 'short',
        '下面代码会输出什么? 格式为 `<字符串> <长度>`。\n\n'
        f'```python\ns = bin({n}) + str(0b101 + {m})\nprint(s, len(s))\n```',
        f'{value} {len(value)}',
        '`bin` 返回带 `0b` 前缀的字符串;`str(...)` 也是字符串。这里发生的是字符串拼接,不是二进制加法。',
    )


def q_float_precision_mcq(rng):
    return mcq(
        rng, CH1, 'float / precision', 2,
        '关于 Python 的 `float`,下列哪项说法正确?',
        '`0.1 + 0.2 == 0.3` 通常为 `False`,因为二进制浮点不能精确表示这些十进制小数',
        ['`float` 和 `int` 一样是任意精度', '`round(2.5)` 一定返回 `3`', '`1 + 1e-16 - 1` 一定精确等于 `1e-16`'],
        'Python 的 `float` 是有限精度 IEEE 754 双精度浮点数。很多十进制小数只是近似存储,所以相等比较要小心。',
    )


def q_float_limits_mcq(rng):
    return mcq(
        rng, CH1, 'float / limites', 2,
        '关于大整数与浮点数边界,下列哪项说法正确?',
        '`2**2000` 可以作为 `int` 精确计算,但把它转成 `float` 可能溢出',
        ['`int` 在 Python 中固定为 64 位,所以 `2**2000` 会溢出', '`1e309` 会自动变成一个任意精度整数', '`math.pow(2, 2000)` 返回精确整数'],
        'Python `int` 任意精度;`float` 有指数范围限制。`math.pow` 返回 `float`,不适合保持大整数精度。',
    )


def q_alias_nested_trace(rng):
    x, y = rng.randint(1, 4), rng.randint(5, 9)
    new_inner = rng.randint(50, 99)
    new_outer = rng.randint(100, 199)
    return make_question(
        CH1, 'copie / alias', 3, 'short',
        '下面代码会输出什么?\n\n'
        f'```python\nA = [[{x}], [{y}]]\nB = A[:]\nA[0][0] = {new_inner}\nA[1] = [{new_outer}]\nprint(B[0][0], B[1][0])\n```',
        f'{new_inner} {y}',
        '`A[:]` 只复制外层列表。`A[0][0]` 修改的是共享的内层列表,所以影响 `B`;但 `A[1] = ...` 只替换 `A` 的外层槽位,不影响 `B[1]`。',
    )


def q_deepcopy_mcq(rng):
    return mcq(
        rng, CH1, 'copie profonde', 2,
        '若 `A` 是二维列表,哪种写法能为每一行也创建一个新列表?',
        '`B = [ligne[:] for ligne in A]`',
        ['`B = A`', '`B = A[:]`', '`B = list(A)`'],
        '`A[:]` 与 `list(A)` 只复制外层。二维列表常用 `[ligne[:] for ligne in A]` 复制每个子列表。',
    )


def q_tuple_single_mcq(rng):
    return mcq(rng, CH1, 'tuple', 1, '哪个表达式创建“只含一个元素 7 的元组”?', '`(7,)`', ['`(7)`', '`[7]`', '`{7}`'], '单元素元组的关键是逗号。`(7)` 只是整数 7 外面加括号。')


def q_empty_set_mcq(rng):
    return mcq(rng, CH1, 'set / dict', 1, '哪个表达式创建空集合 `set`?', '`set()`', ['`{}`', '`()`', '`frozenset({})`'], '`{}` 是空字典。空集合必须写 `set()`。')


def q_set_ops_trace(rng):
    A = set(rng.sample(range(1, 12), 5))
    B = set(rng.sample(range(1, 12), 5))
    C = set(rng.sample(range(1, 12), 3))
    result = (A | B) - (A & C)
    return make_question(
        CH1, 'set / operations', 2, 'short',
        '计算下面表达式,用 Python 集合记法填写。\n\n'
        f'```python\nA = {set_repr(A)}\nB = {set_repr(B)}\nC = {set_repr(C)}\n(A | B) - (A & C)\n```',
        set_repr(result),
        '`|` 是并集,`&` 是交集,`-` 是差集。先按括号算出 `(A | B)` 和 `(A & C)`,再做差集。',
    )


def q_symmetric_difference_trace(rng):
    A = set(rng.sample(range(1, 10), 4))
    B = set(rng.sample(range(1, 10), 4))
    result = A ^ B
    return make_question(CH1, 'set / difference symetrique', 2, 'short', f'计算 `{set_repr(A)} ^ {set_repr(B)}`。结果用 Python 集合记法填写。', set_repr(result), '`^` 是对称差:只保留恰好出现在一个集合中的元素,两边共有的元素会被去掉。')


def q_set_hashability_mcq(rng):
    return mcq(
        rng, CH1, 'hashable', 2,
        '下列表达式中,哪一个是合法的集合?',
        '`{(1, 2), frozenset({3, 4})}`',
        ['`{[1, 2]}`', '`{{1, 2}}`', '`{{1: 2}}`'],
        '集合元素必须可哈希。`tuple` 若内部元素可哈希则可用,`frozenset` 也可哈希;`list/set/dict` 不可哈希。',
    )


def q_dict_get_trace(rng):
    keys = rng.sample(['a', 'b', 'c', 'd'], 3)
    values = rng.sample(range(2, 20), 3)
    data = dict(zip(keys, values))
    missing = rng.choice(['x', 'y', 'z'])
    default = rng.randint(20, 40)
    result = data.get(keys[1], 0) + data.get(missing, default)
    return make_question(
        CH1, 'dict.get', 2, 'short',
        '下面代码会输出什么?\n\n'
        f'```python\nD = {data}\nprint(D.get({keys[1]!r}, 0) + D.get({missing!r}, {default}))\n```',
        result,
        f'`{keys[1]}` 存在,所以取 `{data[keys[1]]}`;`{missing}` 不存在,所以取默认值 `{default}`。',
    )


def q_dict_invert_trace(rng):
    data = {'a': 1, 'b': 2, 'c': 1, 'd': 3}
    result = {v: k for k, v in data.items()}
    return make_question(
        CH1, 'dict / inversion', 3, 'short',
        '下面代码会输出什么字典?\n\n'
        f'```python\nD = {data}\nR = {{v: k for k, v in D.items()}}\nprint(R)\n```',
        result,
        '倒置字典时若多个键有同一个值,后写入的键会覆盖前一个。这里值 `1` 先对应 `a`,后来被 `c` 覆盖。',
    )


def q_dict_view_trace(rng):
    return make_question(
        CH1, 'dict views', 3, 'short',
        '下面代码会输出什么列表?\n\n'
        "```python\nD = {'a': 1, 'b': 2}\nK = D.keys()\nD['c'] = 3\ndel D['a']\nprint(list(K))\n```",
        "['b', 'c']",
        '`dict.keys()` 返回动态视图,不是当场冻结的列表。字典后续增删会反映到 `K` 中。',
    )


def q_bool_key_trace(rng):
    return make_question(
        CH1, 'dict / hash equality', 4, 'short',
        '下面代码会输出什么?\n\n'
        "```python\nD = {1: 'un', True: 'vrai', 1.0: 'float'}\nprint(len(D), D[1])\n```",
        '1 float',
        '`1 == True == 1.0` 且哈希相同,所以它们在字典里是同一个键,后面的赋值覆盖前面的值。',
    )


def q_listcomp_trace(rng):
    n = rng.randint(7, 11)
    expr = rng.choice(['x*x - 1', '2*x + 1', 'x//2'])
    cond = rng.choice(['x % 3 != 0', 'x % 2 == 0', 'x > 3'])
    code = f'[{expr} for x in range({n}) if {cond}]'
    result = eval(code)
    return make_question(CH1, 'comprehension de liste', 2, 'short', f'写出下面表达式的结果。\n\n```python\n{code}\n```', result, f'先遍历 `range({n})`,过滤满足 `{cond}` 的 `x`,再代入表达式 `{expr}`。')


def q_slice_negative_trace(rng):
    values = list(rng.sample(range(10, 40), 8))
    start, stop, step = rng.choice([(None, None, -1), (-1, 1, -2), (6, 1, -2), (-2, None, -3)])
    expr = f"L[{'' if start is None else start}:{'' if stop is None else stop}:{step}]"
    result = eval(expr, {'L': values})
    return make_question(CH1, 'slice / pas negatif', 3, 'short', f'设 `L = {values}`。计算下面切片。\n\n```python\n{expr}\n```', result, '负步长切片从右向左取值,停止端点仍然不包含。逐个列出被访问的下标即可。')


def q_zip_enumerate_trace(rng):
    return make_question(CH1, 'zip / iterator', 2, 'short', '下面代码中第二次 `list(z)` 的结果是什么?\n\n```python\nz = zip([\'a\', \'b\', \'c\'], [10, 20])\nprint(list(z))\nprint(list(z))\n```', '[]', '`zip` 返回迭代器,并且按最短序列截断。第一次 `list(z)` 已经把它消耗完,第二次为空。')


def q_hashable_nested_mcq(rng):
    return mcq(rng, CH1, 'hashable / tuple', 3, '哪一个对象可以作为字典键?', '`(1, frozenset({2, 3}))`', ['`(1, [2, 3])`', '`{1, 2}`', '`{"a": 1}`'], '`tuple` 只有在所有元素都可哈希时才可哈希。`frozenset` 可哈希,但 `list/set/dict` 不可哈希。')


def q_math_pow_mcq(rng):
    return mcq(rng, CH1, 'math.pow / **', 2, '关于 `math.pow(2, 10)` 与 `2**10`,下列哪项正确?', '`math.pow` 返回 `float`,而 `**` 在这里返回 `int`', ['两者都返回 `int`', '`2**10` 返回字符串', '`math.pow` 比 `**` 更能保持大整数精度'], '`math.pow` 的结果类型是浮点数。需要保持整数精度时,优先使用 `**`。')


def q_groupby_code(rng):
    statement = '写函数 `groupe_par_initiale(L)`,输入字符串列表 `L`,返回字典 `D`。对每个字符串 `s`,把它加入 `D[s[0]]` 对应的列表中;同一首字母下保持原顺序。'
    solution = '参考实现:\n\n```python\ndef groupe_par_initiale(L):\n    D = {}\n    for s in L:\n        c = s[0]\n        if c not in D:\n            D[c] = []\n        D[c].append(s)\n    return D\n```\n\n检查点:值必须是列表,不能只保存最后一个字符串;不能因为使用 `set` 而打乱顺序。'
    return code_question(CH1, 'dict / groupement', 3, statement, solution)


def q_deepcopy_code(rng):
    statement = '写函数 `copie2(A)`,其中 `A` 是二维列表。返回一个新二维列表,要求外层列表和每一行列表都不能与原列表共享。禁止直接返回 `A`、`A[:]` 或 `list(A)`。'
    solution = '参考实现:\n\n```python\ndef copie2(A):\n    return [ligne[:] for ligne in A]\n```\n\n关键点:`ligne[:]` 会为每一行创建新列表;只复制外层无法避免内层共享。'
    return code_question(CH1, 'copie / liste 2D', 3, statement, solution)


def q_set_symmetric_code(rng):
    statement = '写函数 `diff_sym(A, B)`,输入两个集合,返回它们的对称差。要求:不要使用运算符 `^`;可以使用 `-`、`|` 或循环。'
    solution = '参考实现:\n\n```python\ndef diff_sym(A, B):\n    return (A - B) | (B - A)\n```\n\n对称差保留“只属于其中一个集合”的元素。这个函数不修改 `A` 或 `B`。'
    return code_question(CH1, 'set / difference symetrique', 3, statement, solution)


def q_base_manual_code(rng):
    statement = '写函数 `valeur_binaire(s)`,输入只含字符 `0` 和 `1` 的字符串 `s`,返回它表示的二进制整数。要求:不要调用 `int(s, 2)`。'
    solution = '参考实现:\n\n```python\ndef valeur_binaire(s):\n    n = 0\n    for c in s:\n        n = 2 * n + int(c)\n    return n\n```\n\n核心是不停左移一位再加当前位。'
    return code_question(CH1, 'bases / conversion manuelle', 4, statement, solution)


def q_occurrences_indices_code(rng):
    statement = '写函数 `positions(s)`,输入字符串 `s`,返回字典 `D`。若字符 `c` 出现在下标 `i1, i2, ...`,则 `D[c] = [i1, i2, ...]`。'
    solution = '参考实现:\n\n```python\ndef positions(s):\n    D = {}\n    for i, c in enumerate(s):\n        if c not in D:\n            D[c] = []\n        D[c].append(i)\n    return D\n```\n\n重点是字典的值是“下标列表”,不是简单计数。'
    return code_question(CH1, 'dict / positions', 4, statement, solution)


def q_filter_real_ints_code(rng):
    statement = '写函数 `vrais_entiers(L)`,输入一个可能混有 `int`, `bool`, `float`, `str` 的列表。返回其中类型严格为 `int` 的元素,保持原顺序。注意:`bool` 是 `int` 的子类,但这里不应保留 `True` 或 `False`。'
    solution = '参考实现:\n\n```python\ndef vrais_entiers(L):\n    return [x for x in L if type(x) is int]\n```\n\n`isinstance(True, int)` 为真,所以本题要用 `type(x) is int` 来排除布尔值。'
    return code_question(CH1, 'types mixtes', 4, statement, solution)


# ======================================================================
# CH2 - Fonctions, recursion, generateurs
# ======================================================================
def q_param_legality_mcq(rng):
    return mcq(rng, CH2, 'arguments', 2, '设 `def f(x, y=1, z=False): ...`。下面哪个调用会因为“同一参数被指定两次”而抛出 `TypeError`?', '`f(1, False, y=2)`', ['`f(1)`', '`f(z=True, x=2)`', '`f(1, z=True)`'], '`f(1, False, y=2)` 中第二个位置参数已经给了 `y`,后面又写 `y=2`,所以同一参数被赋值两次。')


def q_default_arg_trace(rng):
    values = [rng.randint(1, 4), rng.randint(5, 8), rng.randint(9, 12)]
    return make_question(CH2, 'arguments par defaut', 3, 'short', '下面代码会输出什么列表?\n\n' f'```python\ndef f(x, L=[]):\n    L.append(x)\n    return L\nf({values[0]})\nf({values[1]})\nprint(f({values[2]}))\n```', values, '默认参数 `L=[]` 在函数定义时只创建一次。三次调用复用同一个列表,所以三个值都会保留。')


def q_sort_append_none_trace(rng):
    return make_question(CH2, 'None / methodes en place', 2, 'short', '下面代码会输出什么?\n\n```python\nL = [3, 1, 2]\nx = L.sort()\ny = L.append(4)\nprint(L, x, y)\n```', '[1, 2, 3, 4] None None', '`sort` 和 `append` 都原地修改列表,返回值都是 `None`。')


def q_lambda_legal_mcq(rng):
    return mcq(rng, CH2, 'lambda', 1, '下面哪个是合法的 Python `lambda` 表达式?', '`lambda x: x*x if x >= 0 else -x`', ['`lambda x: return x*x`', '`lambda x: y = x+1`', '`lambda x: if x > 0: x`'], '`lambda` 的函数体只能是一个表达式。三元表达式可以,`return`、赋值语句和语句块不可以。')


def q_return_print_trace(rng):
    x = rng.randint(2, 6)
    return make_question(CH2, 'return / print', 2, 'short', '下面程序输出两行。请用空格分隔两行输出。\n\n' f'```python\ndef f(x):\n    print(x + 1)\n    return 2 * x\ny = f({x})\nprint(y)\n```', f'{x + 1} {2 * x}', '`print` 只负责显示;函数真正返回的是 `2*x`。先打印 `x+1`,再打印变量 `y`。')


def q_fib_calls_trace(rng):
    n = rng.randint(5, 9)
    return make_question(CH2, 'Fibonacci / appels', 3, 'short', '设 `c(n)` 为执行下面 `fib2(n)` 时的总调用次数,初始调用也算一次,且 `c(0)=c(1)=1`。\n\n```python\ndef fib2(n):\n    return n if n <= 1 else fib2(n-1) + fib2(n-2)\n```\n\n' f'求 `c({n})`。', fib_call_count(n), f'调用次数满足 `c(n)=c(n-1)+c(n-2)+1`。逐步计算可得 `c({n})={fib_call_count(n)}`。')


def q_power_count_trace(rng):
    n = rng.randint(17, 45)
    return make_question(CH2, 'exponentiation rapide', 3, 'short', '按下面快速幂函数计算时,会执行多少次乘法?\n\n```python\ndef power(A, n):\n    if n == 0: return 1\n    if n == 1: return A\n    if n % 2: return power(A, n-1) * A\n    B = power(A, n//2)\n    return B * B\n```\n\n' f'问题: `power(A, {n})`。', fast_power_mult_count(n), '奇数分支做一次 `* A`,偶数分支做一次平方。沿递归链数乘法即可。')


def q_quicksort_partition_trace(rng):
    values = list(rng.sample(range(1, 40), 7))
    pivot = values[0]
    left = [x for x in values[1:] if x < pivot]
    right = [x for x in values[1:] if x >= pivot]
    return make_question(CH2, 'tri rapide / partition', 2, 'short', '快速排序以首元素为 pivot。第一次分区后,请写出 `L1; L2`。\n\n' f'```python\nL = {values}\nx = L[0]\nL1 = [a for a in L[1:] if a < x]\nL2 = [a for a in L[1:] if a >= x]\n```', f'{left}; {right}', f'pivot 是 `{pivot}`。小于 pivot 的元素进入 `L1`,其余进入 `L2`。')


def q_quicksort_complexity_mcq(rng):
    return mcq(rng, CH2, 'tri rapide / complexite', 3, '若快速排序总是选择首元素为 pivot,且输入列表已经按升序排列,复杂度最可能是哪一种?', '`O(n^2)`', ['`O(log n)`', '`O(n)`', '`O(n log n)` 且不会退化'], '升序输入时首元素 pivot 会导致极不平衡划分:一边为空,另一边长度 `n-1`,递归式退化为平方复杂度。')


def q_generator_consumed_trace(rng):
    n = rng.randint(5, 8)
    first = [x * x for x in range(n) if x % 2]
    return make_question(CH2, 'generateur / epuisement', 2, 'short', '下面代码会输出什么?\n\n' f'```python\ng = (x*x for x in range({n}) if x % 2)\na = list(g)\nb = list(g)\nprint(a, b)\n```', f'{first} []', '生成器是一次性的。第一次 `list(g)` 已消耗全部元素,第二次只能得到空列表。')


def q_next_generator_trace(rng):
    n = rng.randint(6, 9)
    values = [x for x in range(n) if x % 3 != 0]
    return make_question(CH2, 'next / generateur', 2, 'short', '下面代码会输出什么?\n\n' f'```python\ng = (x for x in range({n}) if x % 3 != 0)\nprint(next(g), list(g))\n```', f'{values[0]} {values[1:]}', '`next(g)` 先取走第一个满足条件的元素,后面的 `list(g)` 只包含剩余元素。')


def q_recursion_error_mcq(rng):
    return mcq(rng, CH2, 'recursion / terminaison', 2, '下面哪个递归函数最可能因为规模没有变小而导致 `RecursionError`?', '`def f(n): return 1 if n == 0 else f(n) + 1`', ['`def f(n): return 1 if n == 0 else n*f(n-1)`', '`def f(n): return n if n <= 1 else f(n-1)+f(n-2)`', '`def f(n): return 0 if n < 0 else f(n-1)`'], '递归必须向基准情形靠近。`f(n)` 再调用 `f(n)` 自身,参数没有变小。')


def q_pgcd_trace(rng):
    a, b = rng.choice([(84, 30), (91, 35), (144, 54), (221, 85)])
    return make_question(CH2, 'pgcd / Euclide', 2, 'short', f'用欧几里得算法计算 `pgcd({a}, {b})`,填写最终结果。', math.gcd(a, b), f'欧几里得递推为 `pgcd(a,b)=pgcd(b,a%b)`,直到余数为 0。结果是 `{math.gcd(a, b)}`。')


def q_memoization_mcq(rng):
    return mcq(rng, CH2, 'memoisation', 2, '想把朴素双递归 Fibonacci 从指数复杂度降到线性复杂度,最直接的方法是什么?', '用字典缓存已经算过的 `fib(k)`,重复遇到时直接返回缓存值', ['把函数名缩短', '把 `return` 改成 `print`', '先把 `n` 转成 `float`'], '朴素 Fibonacci 的慢来自重复计算同一子问题。记忆化让每个 `k` 至多计算一次。')


def q_safe_float_equal_code(rng):
    statement = '写函数 `presque_egal(a, b, eps)`,若 `a` 和 `b` 的距离不超过 `eps`,返回 `True`,否则返回 `False`。要求:不要直接使用 `a == b` 判断浮点数相等。'
    solution = '参考实现:\n\n```python\ndef presque_egal(a, b, eps):\n    return abs(a - b) <= eps\n```\n\n浮点数通常只比较误差范围;是否使用 `<=` 要跟题目边界约定一致。'
    return code_question(CH2, 'float / fonction', 2, statement, solution)


def q_fib_iter_code(rng):
    statement = '写函数 `fib_iter(n)`,返回 Fibonacci 数 `F_n`,其中 `F_0=0`, `F_1=1`。要求使用循环,不要使用递归。'
    solution = '参考实现:\n\n```python\ndef fib_iter(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n```\n\n循环不产生递归调用栈,时间复杂度 `O(n)`,额外空间 `O(1)`。'
    return code_question(CH2, 'Fibonacci iteratif', 3, statement, solution)


def q_memo_fib_code(rng):
    statement = '写一个带记忆化的函数 `fib_memo(n)`,返回 Fibonacci 数 `F_n`。要求:使用字典缓存已经计算过的值,并说明复杂度。'
    solution = '参考实现:\n\n```python\nD = {0: 0, 1: 1}\n\ndef fib_memo(n):\n    if n not in D:\n        D[n] = fib_memo(n - 1) + fib_memo(n - 2)\n    return D[n]\n```\n\n每个 `k <= n` 至多真正计算一次,所以时间复杂度为 `O(n)`,缓存空间也是 `O(n)`。'
    return code_question(CH2, 'Fibonacci / memoisation', 4, statement, solution)


def q_memo_sequence_code(rng):
    statement = '定义 `u_0 = -1`, `u_1 = 2`。对 `n >= 2`:若 `u_(n-2) <= 0`,则 `u_n = 2*u_(n-1) + u_(n-2)`;否则 `u_n = u_(n-1) - 3*u_(n-2)`。写带记忆化的递归函数 `suite(n)` 返回 `u_n`。'
    solution = '参考实现:\n\n```python\nD = {0: -1, 1: 2}\n\ndef suite(n):\n    if n not in D:\n        a = suite(n - 2)\n        b = suite(n - 1)\n        if a <= 0:\n            D[n] = 2 * b + a\n        else:\n            D[n] = b - 3 * a\n    return D[n]\n```\n\n先查缓存,再递归计算缺失项。每个下标只填一次。'
    return code_question(CH2, 'suite recurrente / memoisation', 5, statement, solution)


def q_generator_multiples_code(rng):
    statement = '写生成器 `uniques_multiples(L, n)`,其中 `L` 是正整数列表。它按递增顺序产出所有 `0 <= k <= n` 中,恰好是 `L` 中一个且仅一个元素倍数的整数。'
    solution = '参考实现:\n\n```python\ndef uniques_multiples(L, n):\n    for k in range(n + 1):\n        if sum(k % x == 0 for x in L) == 1:\n            yield k\n```\n\n外层扫描 `0..n`,内层统计能整除 `k` 的元素个数。时间复杂度 `O(n*len(L))`,额外空间 `O(1)`。'
    return code_question(CH2, 'generateur / multiples', 4, statement, solution)


def q_partitions_generator_code(rng):
    statement = '写递归生成器 `partitions(n)`,产出所有由正整数组成、非降序排列、总和为 `n` 的列表。例:`partitions(4)` 应产出 `[1,1,1,1]`, `[1,1,2]`, `[2,2]`, `[1,3]`, `[4]`。'
    solution = '参考实现:\n\n```python\ndef partitions(n):\n    if n == 1:\n        yield [1]\n    else:\n        for last in range(1, n):\n            for L in partitions(n - last):\n                if L[-1] <= last:\n                    yield L + [last]\n        yield [n]\n```\n\n非降序条件避免同一划分以不同排列重复出现。复杂度与输出数量相关。'
    return code_question(CH2, 'generateur recursif / partitions', 5, statement, solution)


def q_recursive_to_iterative_code(rng):
    statement = '把欧几里得算法写成迭代函数 `pgcd_iter(a, b)`,返回 `a` 和 `b` 的最大公约数。要求使用 `while`,不要递归。'
    solution = '参考实现:\n\n```python\ndef pgcd_iter(a, b):\n    while b != 0:\n        a, b = b, a % b\n    return a\n```\n\n更新顺序必须同时完成,否则会丢失旧的 `a` 或 `b`。'
    return code_question(CH2, 'pgcd iteratif', 3, statement, solution)


def q_quicksort_code(rng):
    statement = '写函数 `tri(L)`,返回列表 `L` 的一个升序新列表。要求使用课程中的快速排序思想:首元素为 pivot,分成 `< pivot` 和 `>= pivot` 两部分。'
    solution = '参考实现:\n\n```python\ndef tri(L):\n    if not L:\n        return []\n    x = L[0]\n    L1 = [a for a in L[1:] if a < x]\n    L2 = [a for a in L[1:] if a >= x]\n    return tri(L1) + [x] + tri(L2)\n```\n\n平均复杂度 `O(n log n)`,但首元素 pivot 在已排序输入上会退化到 `O(n^2)`。'
    return code_question(CH2, 'tri rapide', 4, statement, solution)


def q_call_count_code(rng):
    statement = '写函数 `nb_appels_fib(n)`,返回朴素 `fib2(n)` 的总调用次数。约定 `nb_appels_fib(0)=nb_appels_fib(1)=1`,且当前调用本身也要计数。'
    solution = '参考实现:\n\n```python\ndef nb_appels_fib(n):\n    if n <= 1:\n        return 1\n    return nb_appels_fib(n - 1) + nb_appels_fib(n - 2) + 1\n```\n\n最后的 `+1` 对应当前这一层调用。'
    return code_question(CH2, 'complexite / appels recursifs', 4, statement, solution)


# ======================================================================
# CH3 - Types abstraits
# ======================================================================
def q_stack_trace(rng):
    ops = [('empiler', 4), ('empiler', 7), ('depiler', None), ('empiler', 2), ('empiler', 9)]
    if rng.random() < 0.5:
        ops.append(('depiler', None))
    stack = []
    text = []
    for op, value in ops:
        if op == 'empiler':
            stack.append(value)
            text.append(f'empiler(P, {value})')
        else:
            stack.pop()
            text.append('depiler(P)')
    return make_question(CH3, 'pile / LIFO', 2, 'short', '初始时栈 `P` 为空。执行操作后,写出最终栈状态 `[底, ..., 顶]`。\n\n```text\n' + '\n'.join(text) + '\n```', stack, '栈是 LIFO:后入栈的元素先出栈。按顺序模拟即可。')


def q_queue_trace(rng):
    ops = [('ajouter', 3), ('ajouter', 8), ('extraire', None), ('ajouter', 5), ('ajouter', 1)]
    if rng.random() < 0.5:
        ops.append(('extraire', None))
    queue = []
    text = []
    for op, value in ops:
        if op == 'ajouter':
            queue.append(value)
            text.append(f'ajouter_element({value}, F)')
        else:
            queue.pop(0)
            text.append('extraire_element(F)')
    return make_question(CH3, 'file / FIFO', 2, 'short', '初始时队列 `F` 为空。执行操作后,写出最终队列状态 `[队首, ..., 队尾]`。\n\n```text\n' + '\n'.join(text) + '\n```', queue, '队列是 FIFO:先进入的元素先被取出。')


def q_stack_vs_queue_trace(rng):
    values = rng.sample(range(1, 10), 4)
    return make_question(CH3, 'pile vs file', 2, 'short', '把列表元素从左到右依次放入栈 `P` 和队列 `F`,然后全部取出。写出 `栈输出; 队列输出`。\n\n' f'列表为 `{values}`。', f'{list(reversed(values))}; {values}', '栈 LIFO 会反序输出;队列 FIFO 会保持原顺序输出。')


def q_brackets_mcq(rng):
    return mcq(rng, CH3, 'pile / parentheses', 2, '用栈检查括号匹配时,读到一个右括号 `]` 应该先做什么?', '检查栈是否非空,再确认栈顶是对应的 `[`', ['直接把 `]` 入栈', '忽略它,直到字符串结束再判断', '只要字符串长度为偶数就一定匹配'], '提前遇到右括号时若栈为空就失败;否则必须与栈顶左括号配对。')


def q_tree_size_height_trace(rng):
    tree = rng.choice(SAMPLE_TREES)
    return make_question(CH3, 'arbre / taille hauteur', 2, 'short', '树用 `[标签, 子树1, 子树2, ...]` 表示。填写 `taille hauteur`,高度按节点数计算。\n\n' f'```python\nA = {tree}\n```', f'{tree_size(tree)} {tree_height(tree)}', f'`taille` 是节点总数 `{tree_size(tree)}`;`hauteur` 是根到最深叶子的节点数 `{tree_height(tree)}`。')


def q_tree_leaf_children_trace(rng):
    tree = ['r', ['a'], ['b', ['c'], ['d']], ['e', ['f']]]
    def count(node):
        own = any(len(child) == 1 for child in node[1:])
        return (1 if own else 0) + sum(count(child) for child in node[1:])
    return make_question(CH3, 'arbre / enfants feuilles', 3, 'short', '树用嵌套列表表示。统计整棵树中“至少有一个叶子作为孩子”的节点个数。\n\n' f'```python\nA = {tree}\n```', count(tree), '要判断的是“当前节点的孩子里是否存在叶子”,不是数叶子本身。然后对子树递归累加。')


def q_tree_parent_label_trace(rng):
    tree = [4, [4], [2, [2], [4]], [5, [5]]]
    def count(node):
        total = 0
        for child in node[1:]:
            if child[0] == node[0]:
                total += 1
            total += count(child)
        return total
    return make_question(CH3, 'arbre / etiquette parent', 3, 'short', '统计树中“标签与父节点标签相同”的节点个数。根节点没有父节点,不计。\n\n' f'```python\nA = {tree}\n```', count(tree), '比较发生在父节点与每个孩子之间;比较后仍要递归处理孩子的整棵子树。')


def q_tree_score_trace(rng):
    tree = [5, [3, [1], [2]], [8, [4]], [0]]
    def score(node):
        return sum(child[0] for child in node[1:])
    def best(node):
        return max([score(node)] + [best(child) for child in node[1:]])
    return make_question(CH3, 'arbre / score', 3, 'short', '定义一个节点的 `score` 为它所有孩子标签之和;叶子的 score 为 0。求整棵树中的最大 score。\n\n' f'```python\nA = {tree}\n```', best(tree), '每个节点只看直接孩子,不是所有后代。对每个节点算当前 score,再与各子树最大值取最大。')


def q_bfs_order_trace(rng):
    start = rng.choice(list(BASE_GRAPH))
    order = ''.join(bfs_order(BASE_GRAPH, start))
    return make_question(CH3, 'BFS / ordre', 2, 'short', '在下面无向图中做 BFS,每次按字母顺序查看邻居。写出访问顺序,字母连写。\n\n' f'```python\nG = {graph_literal(BASE_GRAPH)}\nstart = {start!r}\n```', order, 'BFS 用队列逐层扩展。按题目约定的邻居顺序模拟队列即可。')


def q_bfs_distance_trace(rng):
    pairs = [('A', 'F'), ('B', 'E'), ('E', 'D'), ('A', 'D')]
    start, target = rng.choice(pairs)
    distance = bfs_distance(BASE_GRAPH, start, target)
    return make_question(CH3, 'BFS / distance', 2, 'short', '在下面图中,求从 `start` 到 `target` 的最短距离(边数)。\n\n' f'```python\nG = {graph_literal(BASE_GRAPH)}\nstart = {start!r}\ntarget = {target!r}\n```', distance, '无权图最短距离用 BFS 分层得到。第一次到达目标顶点时的层数就是最短边数。')


def q_graph_complete_mcq(rng):
    graph = {'A': {'B', 'C'}, 'B': {'A', 'C'}, 'C': {'A', 'B'}}
    if rng.random() < 0.5:
        graph['C'].remove('B'); graph['B'].remove('C')
    complete = all(graph[s] == set(graph) - {s} for s in graph)
    return make_question(CH3, 'graphe complet', 2, 'mcq', '下面无向图是完全图吗?\n\n' f'```python\nG = {graph_literal(graph)}\n```', 'A' if complete else 'B', '完全图要求每个顶点都与所有其他顶点相邻。逐个比较邻接集合即可。', ['是', '否'])


def q_graph_regular_mcq(rng):
    graph = {'A': {'B', 'D'}, 'B': {'A', 'C'}, 'C': {'B', 'D'}, 'D': {'A', 'C'}}
    if rng.random() < 0.5:
        graph['A'].add('C'); graph['C'].add('A')
    regular = len({len(neighbours) for neighbours in graph.values()}) == 1
    return make_question(CH3, 'graphe regulier', 2, 'mcq', '下面无向图是正则图(graphe régulier)吗?\n\n' f'```python\nG = {graph_literal(graph)}\n```', 'A' if regular else 'B', '正则图要求所有顶点度数相同。度数就是邻居集合的大小。', ['是', '否'])


def q_euler_mcq(rng):
    cases = [
        ({'A': {'B', 'D'}, 'B': {'A', 'C'}, 'C': {'B', 'D'}, 'D': {'A', 'C'}}, True, 0),
        ({'A': {'B'}, 'B': {'A', 'C'}, 'C': {'B', 'D'}, 'D': {'C'}}, True, 2),
        ({'A': {'B', 'C', 'D'}, 'B': {'A'}, 'C': {'A'}, 'D': {'A'}}, False, 4),
    ]
    graph, has_path, odd_count = rng.choice(cases)
    return make_question(CH3, 'Euler', 3, 'mcq', '下面连通无向图存在欧拉通路(每条边恰好经过一次)吗?\n\n' f'```python\nG = {graph_literal(graph)}\n```', 'A' if has_path else 'B', f'连通图存在欧拉通路当且仅当奇度数顶点个数为 0 或 2。这里奇度数顶点数为 `{odd_count}`。', ['是', '否'])


def q_triangle_mcq(rng):
    has_triangle = rng.random() < 0.7
    graph = TRIANGLE_GRAPH if has_triangle else BASE_GRAPH
    return make_question(CH3, 'graphe / triangle', 3, 'mcq', '下面图中是否存在 3-cycle(三角形)?\n\n' f'```python\nG = {graph_literal(graph)}\n```', 'A' if has_triangle else 'B', '三角形是三个互不相同的顶点两两相邻。可枚举 `x-y-z` 后检查 `x` 与 `z` 是否相邻。', ['是', '否'])


def q_components_trace(rng):
    return make_question(CH3, 'composantes connexes', 3, 'short', '下面无向图有多少个连通分量?\n\n' f'```python\nG = {graph_literal(DISCONNECTED_GRAPH)}\n```', 3, '分量分别是 `{A,B}`,`{C,D}` 和孤立顶点 `{E}`。')


def q_matrix_paths_mcq(rng):
    return mcq(rng, CH3, 'matrice adjacency', 3, '设 `M` 是图的邻接矩阵。`(M^k)[i][j]` 在课程中可解释为什么?', '从顶点 `i` 到顶点 `j` 的长度恰好为 `k` 的路径数量', ['从 `i` 到 `j` 的最短距离', '顶点 `i` 的度数', '图中所有欧拉路径的数量'], '邻接矩阵幂计数的是“固定长度”的路径数,不是最短距离。')


def q_pseudo_signature_mcq(rng):
    return mcq(rng, CH3, 'pseudo-code / signature', 1, '某函数输入一棵树并返回节点总数。哪条 signature 最符合课程约定?', '`fonction taille(A) // arbre -> entier`', ['`def taille(A):`', '`fonction taille(A) -> arbre`', '`taille(A: arbre): int`'], '伪代码题要写 `fonction`,并用注释标明输入类型和返回类型。')


def q_pseudo_tree_leaf_code(rng):
    statement = '用课程伪代码写函数 `nb_avec_feuille(N)`,输入树节点 `N`,返回整棵树中“至少有一个叶子孩子”的节点数。要求写 signature,使用 `fonction`, `pour tout`, `retourner` 等伪代码记号。'
    solution = '参考伪代码:\n\n```text\nfonction nb_avec_feuille(N)\n// noeud -> entier\ntotal <- 0\na_feuille <- faux\npour tout enfant E de N\n    si nombre_enfants(E) = 0\n        a_feuille <- vrai\n    total <- total + nb_avec_feuille(E)\nsi a_feuille\n    total <- total + 1\nretourner total\n```\n\n注意:计数的是“有叶子孩子的父节点”,不是叶子本身。'
    return code_question(CH3, 'pseudo-code / arbre', 4, statement, solution)


def q_pseudo_tree_score_code(rng):
    statement = '用伪代码写函数 `score_max(N)`,输入一棵标签为整数的树,返回所有节点 score 的最大值。一个节点的 score 定义为它所有孩子标签之和;叶子的 score 为 0。'
    solution = '参考伪代码:\n\n```text\nfonction score_max(N)\n// noeud -> entier\ns <- 0\nm <- 0\npour tout enfant E de N\n    s <- s + etiquette(E)\n    m <- max(m, score_max(E))\nretourner max(s, m)\n```\n\n关键是同时考虑当前节点的 score 与每棵子树里的最大 score。'
    return code_question(CH3, 'pseudo-code / score arbre', 5, statement, solution)


def q_pseudo_graph_triangle_code(rng):
    statement = '用伪代码写函数 `triangle(G)`,输入简单无向图 `G`,若图中存在三角形则返回 `vrai`,否则返回 `faux`。'
    solution = '参考伪代码:\n\n```text\nfonction triangle(G)\n// graphe -> booleen\npour tout sommet x de G\n    pour tout voisin y de x\n        pour tout voisin z de y\n            si z <> x et z est voisin de x\n                retourner vrai\nretourner faux\n```\n\n这个算法枚举长度为 2 的路径 `x-y-z`,再检查是否能回到 `x`。'
    return code_question(CH3, 'pseudo-code / triangle', 4, statement, solution)


def q_pseudo_graph_connectivity_code(rng):
    statement = '用伪代码写函数 `est_connexe(G)`,判断无向图 `G` 是否连通。要求使用 BFS 或 DFS 和一个已访问集合。'
    solution = '参考伪代码:\n\n```text\nfonction est_connexe(G)\n// graphe -> booleen\nchoisir un sommet s de G\nM <- ensemble_vide()\nexplore(G, s, M)\nretourner cardinal(M) = nombre_sommets(G)\n```\n\n`explore` 可以是 DFS 或 BFS。核心是从一个起点能否访问全部顶点。'
    return code_question(CH3, 'pseudo-code / connexite', 4, statement, solution)


def q_pseudo_bfs_distance_code(rng):
    statement = '用伪代码写函数 `distance(G, x, y)`,返回无权图中从 `x` 到 `y` 的最短边数;不可达时返回 `None`。'
    solution = '参考伪代码:\n\n```text\nfonction distance(G, x, y)\n// graphe x sommet x sommet -> entier ou None\nF <- file_vide()\najouter_element((x,0), F)\nM <- ensemble_vide()\ntant que non est_vide(F)\n    (s,d) <- extraire_element(F)\n    si s = y\n        retourner d\n    si s non dans M\n        ajouter_element(s, M)\n        pour tout voisin t de s\n            ajouter_element((t,d+1), F)\nretourner None\n```\n\nBFS 的第一次到达给出最短距离。'
    return code_question(CH3, 'pseudo-code / BFS', 4, statement, solution)


def q_pseudo_brackets_code(rng):
    statement = '用伪代码写函数 `bien_parenthese(s)`,判断字符串 `s` 中的 `()` 与 `[]` 是否正确匹配。忽略其他字符。'
    solution = '参考伪代码:\n\n```text\nfonction bien_parenthese(s)\n// chaine -> booleen\nP <- pile_vide()\npour tout caractere c dans s\n    si c = "(" ou c = "["\n        empiler(c, P)\n    sinon si c = ")"\n        si est_vide(P) ou depiler(P) <> "("\n            retourner faux\n    sinon si c = "]"\n        si est_vide(P) ou depiler(P) <> "["\n            retourner faux\nretourner est_vide(P)\n```'
    return code_question(CH3, 'pseudo-code / pile', 4, statement, solution)


def q_pseudo_euler_code(rng):
    statement = '用伪代码写函数 `a_chemin_eulerien(G)`,判断无向图是否存在欧拉通路。'
    solution = '参考伪代码:\n\n```text\nfonction a_chemin_eulerien(G)\n// graphe -> booleen\nsi non est_connexe(G)\n    retourner faux\nimpairs <- 0\npour tout sommet s de G\n    si degre(s) est impair\n        impairs <- impairs + 1\nretourner impairs = 0 ou impairs = 2\n```\n\n欧拉条件不能只看奇偶度数,还必须先保证连通。'
    return code_question(CH3, 'pseudo-code / Euler', 4, statement, solution)


def q_pseudo_stack_reverse_code(rng):
    statement = '用伪代码写函数 `renverse_file(F)`,输入一个队列 `F`,返回一个元素顺序反转的新队列。提示:可以使用一个栈。'
    solution = '参考伪代码:\n\n```text\nfonction renverse_file(F)\n// file -> file\nP <- pile_vide()\ntant que non est_vide(F)\n    empiler(extraire_element(F), P)\nR <- file_vide()\ntant que non est_vide(P)\n    ajouter_element(depiler(P), R)\nretourner R\n```\n\n栈的 LIFO 性质正好用于反转顺序。'
    return code_question(CH3, 'pseudo-code / file et pile', 4, statement, solution)


def q_tree_path_code(rng):
    statement = '用伪代码写函数 `chemin_vers(N, x)`,若树中存在标签 `x`,返回从根到该节点的标签列表;不存在则返回空列表。'
    solution = '参考伪代码:\n\n```text\nfonction chemin_vers(N, x)\n// noeud x etiquette -> liste\nsi etiquette(N) = x\n    retourner [x]\npour tout enfant E de N\n    C <- chemin_vers(E, x)\n    si C <> []\n        retourner [etiquette(N)] + C\nretourner []\n```\n\n一旦某个子树找到路径,就把当前根标签接在前面返回。'
    return code_question(CH3, 'pseudo-code / chemin arbre', 5, statement, solution)


def q_bounded_dfs_code(rng):
    statement = '写伪代码函数 `existe_chemin_borne(G, s, t, k)`,判断图中是否存在从 `s` 到 `t` 且长度不超过 `k` 的路径。'
    solution = '参考思路:\n\n```text\nfonction existe_chemin_borne(G, s, t, k)\n// graphe x sommet x sommet x entier -> booleen\nsi s = t\n    retourner vrai\nsi k = 0\n    retourner faux\npour tout voisin u de s\n    si existe_chemin_borne(G, u, t, k-1)\n        retourner vrai\nretourner faux\n```\n\n若题目允许环,可以额外传入已访问集合来避免重复走同一条路径。'
    return code_question(CH3, 'pseudo-code / DFS borne', 5, statement, solution)


def q_components_code(rng):
    statement = '用伪代码写函数 `nb_composantes(G)`,返回无向图的连通分量数。'
    solution = '参考伪代码:\n\n```text\nfonction nb_composantes(G)\n// graphe -> entier\nM <- ensemble_vide()\nn <- 0\npour tout sommet s de G\n    si s non dans M\n        n <- n + 1\n        explore(G, s, M)\nretourner n\n```\n\n每遇到一个未访问顶点,就发现了一个新分量,并把该分量全部标记。'
    return code_question(CH3, 'pseudo-code / composantes', 5, statement, solution)


# ======================================================================
# CH4 - Classes et objets
# ======================================================================
def q_vecteur_repr_trace(rng):
    a, b, c, d = rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(-4, 4), rng.randint(-4, 4)
    return make_question(CH4, 'Vecteur2d / __add__', 2, 'short', '`Vecteur2d.__add__` 按坐标相加,`__repr__` 返回 `(x,y)`。求下面表达式。\n\n' f'```python\nrepr(Vecteur2d({a}, {b}) + Vecteur2d({c}, {d}))\n```', f'({a + c},{b + d})', '加法逐坐标进行,再由 `__repr__` 控制显示格式。')


def q_vecteur_norm_trace(rng):
    a, b = rng.choice([(3, 4), (5, 12), (8, 15), (7, 24)])
    return make_question(CH4, 'Vecteur2d / norme', 2, 'short', f'若 `Vecteur2d({a}, {b}).norm()` 返回欧几里得范数,结果是多少?', float((a * a + b * b) ** 0.5), f'范数为 `sqrt({a}^2 + {b}^2) = {float((a * a + b * b) ** 0.5)}`。')


def q_trinome_derive_trace(rng):
    a, b, c = rng.randint(-5, 5), rng.randint(-5, 5), rng.randint(-5, 5)
    return make_question(CH4, 'Trinome / derive', 2, 'short', f'`Trinome(a,b,c)` 表示 `aX^2+bX+c`。设 `P = Trinome({a},{b},{c})`,求 `P.derive()` 的属性 `a b c`。', f'0 {2*a} {b}', f'导函数为 `{2*a}X + {b}`,仍用 `Trinome(0, {2*a}, {b})` 表示。')


def q_trinome_add_trace(rng):
    p = [rng.randint(-3, 4) for _ in range(3)]
    q = [rng.randint(-3, 4) for _ in range(3)]
    result = [p[i] + q[i] for i in range(3)]
    return make_question(CH4, 'Trinome / __add__', 2, 'short', f'若 `Trinome.__add__` 逐项相加,求 `Trinome{tuple(p)} + Trinome{tuple(q)}` 的属性 `a b c`。', ' '.join(map(str, result)), '两个二次多项式相加时,`X^2`、`X`、常数项分别相加。')


def q_decimal_mul_trace(rng):
    x1, p1 = rng.randint(2, 90), rng.randint(0, 3)
    x2, p2 = rng.randint(2, 90), rng.randint(0, 3)
    return make_question(CH4, 'Decimal / __mul__', 2, 'short', f'`Decimal(x,p)` 表示 `x*10^(-p)`。设 `P=Decimal({x1},{p1})`, `Q=Decimal({x2},{p2})`。求 `P*Q` 的属性 `x p`。', f'{x1*x2} {p1+p2}', '乘法让 `x` 相乘,小数位数 `p` 相加;不需要转成 `float`。')


def q_decimal_repr_trace(rng):
    x, p = rng.choice([(7, 2), (42, 0), (305, 4), (-4350072, 4), (1200, 3)])
    return make_question(CH4, 'Decimal / __repr__', 3, 'short', f'课程中的 `Decimal({x}, {p})` 显示时先按需左补零,再在倒数第 `p` 位前插入小数点。`repr(Decimal({x}, {p}))` 是什么?', decimal_repr(x, p), f'`x` 的数字串按 `p={p}` 插入小数点;位数不足时要左补零。结果是 `{decimal_repr(x, p)}`。')


def q_class_attribute_trace(rng):
    return make_question(CH4, 'attribut de classe', 3, 'short', '下面代码会输出什么?\n\n```python\nclass Boite:\n    objets = []\n    def __init__(self, nom):\n        self.nom = nom\n\na = Boite("a")\nb = Boite("b")\na.objets.append("x")\nprint(b.objets)\n```', "['x']", '`objets` 写在类体里,是类属性。两个实例在没有遮蔽它时共享同一个列表。')


def q_dunder_mcq(rng):
    cases = [('x + y', '__add__'), ('x * y', '__mul__'), ('len(x)', '__len__'), ('x[k]', '__getitem__'), ('k in x', '__contains__'), ('repr(x)', '__repr__'), ('for v in x', '__iter__'), ('hash(x)', '__hash__')]
    expr, correct = rng.choice(cases)
    distractors = rng.sample([name for _, name in cases if name != correct], 3)
    return mcq(rng, CH4, 'dunder', 1, f'表达式 `{expr}` 会优先触发哪个特殊方法?', correct, distractors, f'Python 协议中 `{expr}` 对应 `{correct}`。')


def q_init_return_mcq(rng):
    return mcq(rng, CH4, '__init__', 2, '关于 `__init__`,下列哪项正确?', '`__init__` 负责初始化实例,不能返回非 `None` 的值', ['`__init__` 必须返回创建好的实例', '`self` 是 Python 关键字,不能换名', '`__init__` 不会在 `Classe(...)` 时调用'], '对象创建后 Python 会调用 `__init__` 初始化。若 `__init__` 返回非 `None`,会抛 `TypeError`。')


def q_eq_hash_mcq(rng):
    return mcq(rng, CH4, '__eq__ / __hash__', 3, '在自定义类中只定义 `__eq__` 而不定义 `__hash__`,通常会发生什么?', '实例会变成不可哈希,不能作为 `set` 元素或 `dict` 键', ['实例会自动按值获得完美哈希', '`__eq__` 会被 Python 忽略', '所有实例都会被视为不相等'], 'Python 为了避免可变相等关系破坏哈希表,会把 `__hash__` 设为 `None`。')


def q_mutable_default_class_mcq(rng):
    return mcq(rng, CH4, 'valeur mutable par defaut', 3, '下面哪种构造器写法能避免多个树节点共享同一个 `enfants` 列表?', '`def __init__(self, etiquette, enfants=None): self.enfants = [] if enfants is None else enfants`', ['`def __init__(self, etiquette, enfants=[]): self.enfants = enfants`', '`enfants = []` 写在类体中', '`def __init__(self, etiquette, enfants={}): self.enfants = enfants`'], '可变默认值只创建一次。安全习惯是默认 `None`,再在函数体里创建新列表。')


def q_decimal_class_code(rng):
    statement = '实现类 `Decimal`,属性 `x, p` 表示数 `x*10^(-p)`。要求实现 `__init__`, `__mul__`, `int(self)` 和 `__repr__`。`__repr__` 要处理前导零,例如 `Decimal(7,2)` 显示为 `0.07`。'
    solution = '参考实现:\n\n```python\nclass Decimal:\n    def __init__(self, x, p):\n        self.x = x\n        self.p = p\n\n    def __mul__(self, other):\n        return Decimal(self.x * other.x, self.p + other.p)\n\n    def int(self):\n        return self.x // 10**self.p\n\n    def __repr__(self):\n        s = str(self.x)\n        if len(s) < self.p + 1:\n            s = "0" * (self.p + 1 - len(s)) + s\n        if self.p == 0:\n            return s + "."\n        return s[:-self.p] + "." + s[-self.p:]\n```\n\n重点:乘法是 `x` 相乘、`p` 相加;显示时不要转 `float`。'
    return code_question(CH4, 'Decimal / classe', 5, statement, solution)


def q_trinome_class_code(rng):
    statement = '实现类 `Trinome(a,b,c)`,表示 `aX^2+bX+c`。要求实现 `__init__`, `__add__`, `derive`。`derive` 返回一个新的 `Trinome`。'
    solution = '参考实现:\n\n```python\nclass Trinome:\n    def __init__(self, a, b, c):\n        self.a = a\n        self.b = b\n        self.c = c\n\n    def __add__(self, other):\n        return Trinome(self.a + other.a, self.b + other.b, self.c + other.c)\n\n    def derive(self):\n        return Trinome(0, 2 * self.a, self.b)\n```\n\n运算方法应返回新对象,不要直接修改参与运算的对象。'
    return code_question(CH4, 'Trinome / classe', 4, statement, solution)


def q_arbre_class_code(rng):
    statement = '实现类 `Arbre(etiquette, enfants=None)`。要求:避免共享默认列表;实现方法 `taille(self)` 返回节点总数。'
    solution = '参考实现:\n\n```python\nclass Arbre:\n    def __init__(self, etiquette, enfants=None):\n        self.etiquette = etiquette\n        self.enfants = [] if enfants is None else enfants\n\n    def taille(self):\n        total = 1\n        for enfant in self.enfants:\n            total += enfant.taille()\n        return total\n```\n\n`enfants=None` 是为了避免所有实例共享同一个默认列表。'
    return code_question(CH4, 'Arbre / classe', 4, statement, solution)


def q_fraction_invariant_code(rng):
    statement = '实现类 `Fraction(p, q)`,表示分数 `p/q`。要求:构造时保证 `q > 0`,并用 `pgcd` 约分;实现 `__repr__` 返回 `p/q`。'
    solution = '参考实现:\n\n```python\nfrom math import gcd\n\nclass Fraction:\n    def __init__(self, p, q):\n        assert q != 0\n        if q < 0:\n            p, q = -p, -q\n        d = gcd(abs(p), q)\n        self.p = p // d\n        self.q = q // d\n\n    def __repr__(self):\n        return f"{self.p}/{self.q}"\n```\n\n类不变量是:分母严格为正,且分子分母互素。'
    return code_question(CH4, 'classe / invariant', 5, statement, solution)


def q_factory_class_code(rng):
    statement = '为类 `Vecteur2d` 写一个函数 `depuis_tuple(t)`,其中 `t` 是形如 `(x, y)` 的二元组。函数返回一个新的 `Vecteur2d(x, y)` 实例。然后说明这个函数是否会共享可变状态。'
    solution = '参考实现:\n\n```python\ndef depuis_tuple(t):\n    x, y = t\n    return Vecteur2d(x, y)\n```\n\n这里只读取元组中的两个值并创建新实例,不会引入共享列表之类的可变状态。'
    return code_question(CH4, 'factory / objet', 3, statement, solution)


def q_interval_code(rng):
    statement = '实现类 `Intervalle(a, b)`,表示闭区间 `[a,b]`。要求构造时保证 `a <= b`;实现 `contient(self, x)` 判断 `x` 是否在区间内。'
    solution = '参考实现:\n\n```python\nclass Intervalle:\n    def __init__(self, a, b):\n        assert a <= b\n        self.a = a\n        self.b = b\n\n    def contient(self, x):\n        return self.a <= x <= self.b\n```\n\n`a <= b` 是这个类的基本不变量,构造时就要保证。'
    return code_question(CH4, 'classe / invariant', 4, statement, solution)


EXAM_PLANS = {
    1: [q_base_conversion_trace, q_rounding_tuple, q_tuple_single_mcq, q_empty_set_mcq, q_param_legality_mcq, q_sort_append_none_trace, q_stack_trace, q_tree_size_height_trace, q_vecteur_repr_trace, q_dunder_mcq, q_listcomp_trace, q_dict_get_trace, q_pgcd_trace, q_queue_trace, q_trinome_derive_trace, q_pseudo_signature_mcq, q_pseudo_stack_reverse_code, q_pseudo_tree_leaf_code, q_pseudo_bfs_distance_code, q_pseudo_brackets_code, q_memo_fib_code, q_pseudo_tree_score_code, q_trinome_class_code, q_generator_multiples_code],
    2: [q_alias_nested_trace, q_set_ops_trace, q_dict_get_trace, q_zip_enumerate_trace, q_lambda_legal_mcq, q_default_arg_trace, q_stack_vs_queue_trace, q_bfs_distance_trace, q_vecteur_norm_trace, q_mutable_default_class_mcq, q_set_symmetric_code, q_occurrences_indices_code, q_fib_iter_code, q_pseudo_stack_reverse_code, q_factory_class_code, q_pseudo_tree_leaf_code, q_pseudo_graph_connectivity_code, q_pseudo_bfs_distance_code, q_pseudo_brackets_code, q_pseudo_signature_mcq, q_memo_sequence_code, q_pseudo_graph_triangle_code, q_arbre_class_code, q_partitions_generator_code],
    3: [q_hashable_nested_mcq, q_deepcopy_mcq, q_bool_key_trace, q_slice_negative_trace, q_return_print_trace, q_generator_consumed_trace, q_queue_trace, q_graph_complete_mcq, q_class_attribute_trace, q_init_return_mcq, q_deepcopy_code, q_groupby_code, q_pgcd_trace, q_bfs_order_trace, q_trinome_add_trace, q_pseudo_euler_code, q_pseudo_tree_score_code, q_pseudo_graph_connectivity_code, q_pseudo_stack_reverse_code, q_pseudo_brackets_code, q_memo_fib_code, q_components_code, q_decimal_class_code, q_generator_multiples_code],
    4: [q_complex_attr, q_complex_square, q_rounding_tuple, q_base_conversion_trace, q_float_limits_mcq, q_fib_calls_trace, q_return_print_trace, q_tree_size_height_trace, q_tree_leaf_children_trace, q_trinome_derive_trace, q_safe_float_equal_code, q_fib_iter_code, q_memo_fib_code, q_pseudo_tree_leaf_code, q_trinome_add_trace, q_queue_trace, q_pseudo_tree_leaf_code, q_pseudo_tree_score_code, q_pseudo_bfs_distance_code, q_groupby_code, q_memo_fib_code, q_pseudo_tree_leaf_code, q_trinome_class_code, q_generator_multiples_code],
    5: [q_set_ops_trace, q_empty_set_mcq, q_symmetric_difference_trace, q_set_hashability_mcq, q_dict_get_trace, q_fib_calls_trace, q_memoization_mcq, q_default_arg_trace, q_dunder_mcq, q_vecteur_repr_trace, q_set_symmetric_code, q_occurrences_indices_code, q_memo_sequence_code, q_pseudo_graph_triangle_code, q_vecteur_norm_trace, q_pseudo_signature_mcq, q_pseudo_stack_reverse_code, q_pseudo_tree_leaf_code, q_pseudo_graph_triangle_code, q_pseudo_graph_connectivity_code, q_memo_sequence_code, q_pseudo_graph_triangle_code, q_trinome_class_code, q_partitions_generator_code],
    6: [q_dict_invert_trace, q_hashable_nested_mcq, q_dict_view_trace, q_generator_consumed_trace, q_next_generator_trace, q_stack_trace, q_stack_vs_queue_trace, q_decimal_mul_trace, q_decimal_repr_trace, q_dunder_mcq, q_groupby_code, q_occurrences_indices_code, q_generator_multiples_code, q_pseudo_stack_reverse_code, q_decimal_class_code, q_groupby_code, q_pseudo_stack_reverse_code, q_pseudo_brackets_code, q_pseudo_tree_leaf_code, q_pseudo_bfs_distance_code, q_memo_sequence_code, q_pseudo_tree_score_code, q_decimal_class_code, q_generator_multiples_code],
    7: [q_float_precision_mcq, q_float_limits_mcq, q_rounding_tuple, q_alias_nested_trace, q_recursion_error_mcq, q_fib_calls_trace, q_bfs_order_trace, q_bfs_distance_trace, q_euler_mcq, q_class_attribute_trace, q_safe_float_equal_code, q_recursive_to_iterative_code, q_fib_iter_code, q_pseudo_bfs_distance_code, q_mutable_default_class_mcq, q_pseudo_bfs_distance_code, q_pseudo_euler_code, q_tree_parent_label_trace, q_tree_path_code, q_pseudo_stack_reverse_code, q_memo_sequence_code, q_pseudo_euler_code, q_arbre_class_code, q_generator_multiples_code],
    8: [q_listcomp_trace, q_generator_consumed_trace, q_alias_nested_trace, q_sort_append_none_trace, q_fib_calls_trace, q_memoization_mcq, q_stack_vs_queue_trace, q_trinome_derive_trace, q_dunder_mcq, q_bfs_distance_trace, q_listcomp_trace, q_groupby_code, q_memo_fib_code, q_occurrences_indices_code, q_trinome_class_code, q_pseudo_tree_score_code, q_pseudo_graph_connectivity_code, q_pseudo_tree_score_code, q_pseudo_bfs_distance_code, q_pseudo_stack_reverse_code, q_memo_fib_code, q_pseudo_tree_score_code, q_trinome_class_code, q_partitions_generator_code],
    9: [q_base_conversion_trace, q_bin_string_trace, q_decimal_mul_trace, q_math_pow_mcq, q_quicksort_complexity_mcq, q_quicksort_partition_trace, q_alias_nested_trace, q_dict_get_trace, q_default_arg_trace, q_generator_consumed_trace, q_base_manual_code, q_occurrences_indices_code, q_quicksort_code, q_decimal_repr_trace, q_pseudo_graph_connectivity_code, q_pseudo_bfs_distance_code, q_pseudo_graph_triangle_code, q_tree_size_height_trace, q_pseudo_graph_connectivity_code, q_quicksort_complexity_mcq, q_memo_sequence_code, q_pseudo_graph_triangle_code, q_decimal_class_code, q_generator_multiples_code],
    10: [q_symmetric_difference_trace, q_empty_set_mcq, q_set_ops_trace, q_dict_get_trace, q_set_hashability_mcq, q_default_arg_trace, q_generator_consumed_trace, q_power_count_trace, q_components_trace, q_vecteur_repr_trace, q_set_symmetric_code, q_occurrences_indices_code, q_generator_multiples_code, q_pseudo_graph_connectivity_code, q_factory_class_code, q_stack_vs_queue_trace, q_pseudo_graph_connectivity_code, q_components_code, q_pseudo_euler_code, q_tree_parent_label_trace, q_memo_sequence_code, q_components_code, q_trinome_class_code, q_partitions_generator_code],
    11: [q_dict_get_trace, q_dict_invert_trace, q_default_arg_trace, q_decimal_mul_trace, q_alias_nested_trace, q_memoization_mcq, q_bfs_order_trace, q_tree_score_trace, q_dunder_mcq, q_decimal_repr_trace, q_groupby_code, q_occurrences_indices_code, q_memo_sequence_code, q_call_count_code, q_decimal_class_code, q_pseudo_stack_reverse_code, q_pseudo_bfs_distance_code, q_pseudo_tree_score_code, q_tree_parent_label_trace, q_graph_regular_mcq, q_memo_sequence_code, q_pseudo_tree_score_code, q_decimal_class_code, q_generator_multiples_code],
    12: [q_alias_nested_trace, q_deepcopy_mcq, q_deepcopy_code, q_dict_view_trace, q_recursion_error_mcq, q_fib_calls_trace, q_generator_consumed_trace, q_stack_vs_queue_trace, q_bfs_order_trace, q_eq_hash_mcq, q_deepcopy_code, q_listcomp_trace, q_memo_sequence_code, q_call_count_code, q_generator_multiples_code, q_pseudo_brackets_code, q_pseudo_bfs_distance_code, q_groupby_code, q_graph_regular_mcq, q_tree_parent_label_trace, q_memo_sequence_code, q_pseudo_tree_score_code, q_fraction_invariant_code, q_partitions_generator_code],
    13: [q_bool_key_trace, q_tuple_single_mcq, q_slice_negative_trace, q_alias_nested_trace, q_hashable_nested_mcq, q_default_arg_trace, q_next_generator_trace, q_decimal_mul_trace, q_power_count_trace, q_bfs_order_trace, q_groupby_code, q_filter_real_ints_code, q_partitions_generator_code, q_decimal_class_code, q_bounded_dfs_code, q_pseudo_brackets_code, q_tree_path_code, q_bounded_dfs_code, q_components_code, q_interval_code, q_memo_sequence_code, q_bounded_dfs_code, q_decimal_class_code, q_partitions_generator_code],
    14: [q_rounding_tuple, q_float_precision_mcq, q_float_limits_mcq, q_alias_nested_trace, q_default_arg_trace, q_fib_calls_trace, q_lambda_legal_mcq, q_stack_vs_queue_trace, q_init_return_mcq, q_math_pow_mcq, q_safe_float_equal_code, q_listcomp_trace, q_recursive_to_iterative_code, q_pgcd_trace, q_factory_class_code, q_tree_path_code, q_tree_path_code, q_pseudo_bfs_distance_code, q_pseudo_stack_reverse_code, q_pseudo_euler_code, q_memo_sequence_code, q_tree_path_code, q_factory_class_code, q_generator_multiples_code],
    15: [q_dict_view_trace, q_math_pow_mcq, q_hashable_nested_mcq, q_zip_enumerate_trace, q_param_legality_mcq, q_sort_append_none_trace, q_power_count_trace, q_generator_consumed_trace, q_matrix_paths_mcq, q_eq_hash_mcq, q_groupby_code, q_generator_multiples_code, q_memo_sequence_code, q_pseudo_bfs_distance_code, q_interval_code, q_components_code, q_pseudo_tree_score_code, q_pseudo_bfs_distance_code, q_matrix_paths_mcq, q_bounded_dfs_code, q_memo_sequence_code, q_pseudo_bfs_distance_code, q_fraction_invariant_code, q_partitions_generator_code],
}


TRACE_FALLBACKS = [
    q_complex_attr, q_complex_square, q_rounding_tuple, q_base_conversion_trace, q_bin_string_trace,
    q_float_precision_mcq, q_float_limits_mcq, q_alias_nested_trace, q_deepcopy_mcq,
    q_tuple_single_mcq, q_empty_set_mcq, q_set_ops_trace, q_symmetric_difference_trace,
    q_set_hashability_mcq, q_dict_get_trace, q_dict_invert_trace, q_dict_view_trace,
    q_bool_key_trace, q_listcomp_trace, q_slice_negative_trace, q_zip_enumerate_trace,
    q_hashable_nested_mcq, q_math_pow_mcq, q_param_legality_mcq, q_default_arg_trace,
    q_sort_append_none_trace, q_lambda_legal_mcq, q_return_print_trace, q_fib_calls_trace,
    q_power_count_trace, q_quicksort_partition_trace, q_quicksort_complexity_mcq,
    q_generator_consumed_trace, q_next_generator_trace, q_recursion_error_mcq, q_pgcd_trace,
    q_memoization_mcq, q_stack_trace, q_queue_trace, q_stack_vs_queue_trace, q_brackets_mcq,
    q_tree_size_height_trace, q_tree_leaf_children_trace, q_tree_parent_label_trace,
    q_tree_score_trace, q_bfs_order_trace, q_bfs_distance_trace, q_graph_complete_mcq,
    q_graph_regular_mcq, q_euler_mcq, q_triangle_mcq, q_components_trace,
    q_matrix_paths_mcq, q_pseudo_signature_mcq, q_vecteur_repr_trace, q_vecteur_norm_trace,
    q_trinome_derive_trace, q_trinome_add_trace, q_decimal_mul_trace, q_decimal_repr_trace,
    q_class_attribute_trace, q_dunder_mcq, q_init_return_mcq, q_eq_hash_mcq,
    q_mutable_default_class_mcq,
]

SHORT_FALLBACKS = [
    q_groupby_code, q_deepcopy_code, q_set_symmetric_code, q_base_manual_code,
    q_occurrences_indices_code, q_filter_real_ints_code, q_safe_float_equal_code,
    q_fib_iter_code, q_memo_fib_code, q_recursive_to_iterative_code, q_quicksort_code,
    q_call_count_code, q_pseudo_stack_reverse_code, q_factory_class_code, q_interval_code,
]

PSEUDO_FALLBACKS = [
    q_pseudo_tree_leaf_code, q_pseudo_tree_score_code, q_pseudo_graph_triangle_code,
    q_pseudo_graph_connectivity_code, q_pseudo_bfs_distance_code, q_pseudo_brackets_code,
    q_pseudo_euler_code, q_pseudo_stack_reverse_code, q_tree_path_code, q_bounded_dfs_code,
    q_components_code,
]

LONG_FALLBACKS = [
    q_memo_fib_code, q_memo_sequence_code, q_generator_multiples_code,
    q_partitions_generator_code, q_quicksort_code, q_call_count_code,
    q_pseudo_tree_leaf_code, q_pseudo_tree_score_code, q_pseudo_graph_triangle_code,
    q_pseudo_graph_connectivity_code, q_pseudo_bfs_distance_code, q_pseudo_euler_code,
    q_tree_path_code, q_bounded_dfs_code, q_components_code,
    q_decimal_class_code, q_trinome_class_code, q_arbre_class_code,
    q_fraction_invariant_code, q_factory_class_code, q_interval_code,
]


def fallbacks_for_slot(index):
    if index <= 10:
        return TRACE_FALLBACKS
    if index <= 15:
        return SHORT_FALLBACKS
    if index <= 20:
        return PSEUDO_FALLBACKS
    return LONG_FALLBACKS


SET_FOCUS = {
    1: '热身:进制、取整、参数、栈队列和基础类',
    2: '热身:拷贝、集合、lambda、BFS 和可变默认值',
    3: '热身:哈希性、迭代器、图概念和类属性',
    4: '复数与类型转换、Fibonacci、树叶子孩子、Trinome',
    5: '集合运算、双递归复杂度、图三角形、运算符重载',
    6: '字典推导、生成器消费、栈反序、Decimal 初级',
    7: '浮点精度、递归终止、BFS/欧拉、类属性共享',
    8: '列表推导、记忆化 Fibonacci、树 score、Trinome',
    9: '进制字符串、快排复杂度、3-cycle、Decimal 格式化',
    10: '集合对称差、递归生成器、连通性、类方法组合',
    11: '字典倒置、记忆化应用、树权重、Decimal repr',
    12: '嵌套拷贝、递归树计数、ADT 多操作、类不变量',
    13: '类型混合、递归生成器、图剪枝、Decimal 高阶',
    14: '浮点边界、递归转迭代、树路径、对象构造',
    15: '综合类型、生成器递归、最短路、综合类题',
}


def build_set(set_id):
    rng = random.Random(set_id * 1000 + 7)
    templates = EXAM_PLANS[set_id]
    if len(templates) != QUESTIONS_PER_SET:
        raise ValueError(f'Set {set_id} has {len(templates)} templates, expected {QUESTIONS_PER_SET}')

    questions = []
    used_statements = set()
    for index, template in enumerate(templates, 1):
        question = None
        for candidate in [template] + fallbacks_for_slot(index):
            candidate_question = candidate(rng)
            if candidate_question['statement_md'] not in used_statements:
                question = candidate_question
                break
        if question is None:
            question = template(rng)
            question['statement_md'] += f'\n\n变体编号: {set_id}-{index}'
        used_statements.add(question['statement_md'])
        question['id'] = f'{set_id}-{index}'
        questions.append(question)

    return {
        'id': set_id,
        'title': f'第 {set_id} 套模拟卷',
        'focus': SET_FOCUS[set_id],
        'questions': questions,
    }


def main():
    out = {
        'meta': {
            'course': 'AP2 — 算法与程序设计 2',
            'sets_count': 15,
            'questions_per_set': QUESTIONS_PER_SET,
            'structure': 'Q1-10 trace/细节判断,Q11-15 短编程,Q16-20 伪代码/ADT,Q21-24 长题',
        },
        'sets': [build_set(i) for i in range(1, 16)],
    }
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'exams.json')
    with open(out_path, 'w', encoding='utf-8') as handle:
        json.dump(out, handle, ensure_ascii=False, indent=2)
    total = sum(len(item['questions']) for item in out['sets'])
    print(f'OK -> {out_path} ({total} questions)')


if __name__ == '__main__':
    main()