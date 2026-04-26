"""生成 15 套 AP2 模拟卷。
每套题可复现(seed 由卷号决定),输出到 data/exams.json。
"""

import json
import os
import random


# ======================================================================
# Helpers
# ======================================================================
def fib2_calls(n, cache={0: 1, 1: 1}):
    """朴素 fib2(n) 的总调用次数(包含初始调用本身)。"""
    if n not in cache:
        cache[n] = fib2_calls(n - 1) + fib2_calls(n - 2) + 1
    return cache[n]


def fast_power_mult_count(n):
    """按题目中的递归快速幂写法,计算 power(A, n) 需要多少次乘法。"""
    if n <= 1:
        return 0
    if n % 2 == 0:
        return 1 + fast_power_mult_count(n // 2)
    return 1 + fast_power_mult_count(n - 1)


def shuffled_choices(rng, correct, distractors):
    choices = [correct] + distractors
    rng.shuffle(choices)
    return choices, chr(ord('A') + choices.index(correct))


def make_code_question(
    chapter,
    topic,
    difficulty,
    statement_md,
    explanation_md,
    answer_hint='请对照下方参考实现自评',
):
    return dict(
        chapter=chapter,
        topic=topic,
        difficulty=difficulty,
        type='code',
        statement_md=statement_md,
        answer=answer_hint,
        explanation_md=explanation_md,
    )


# ======================================================================
# Question templates
# ======================================================================
CH1, CH2, CH3, CH4 = 1, 2, 3, 4


def t_set_ops(rng):
    A = set(rng.sample(range(1, 10), 4))
    B = set(rng.sample(range(1, 10), 4))
    op = rng.choice(['&', '|', '-', '^'])
    res = eval(f'A {op} B')
    res_str = '{' + ', '.join(map(str, sorted(res))) + '}' if res else 'set()'
    op_name = {'&': '交集', '|': '并集', '-': '差集', '^': '对称差'}[op]
    return dict(
        chapter=CH1,
        topic='集合',
        difficulty=1,
        type='short',
        statement_md=(
            '计算下面的集合表达式,结果请用 Python 记法填写(`{...}` 或 `set()`)。\n\n'
            f'```python\n{A} {op} {B}\n```'
        ),
        answer=res_str,
        explanation_md=(
            f'这里的运算符 `{op}` 表示{op_name}。按元素逐个判断后,结果是 `{res_str}`。'
        ),
    )


def t_dict_trace(rng):
    keys = rng.sample(['a', 'b', 'c', 'd', 'e', 'f'], 4)
    vals = rng.sample(range(1, 30), 4)
    data = dict(zip(keys, vals))
    add_k = rng.choice(['x', 'y', 'z'])
    add_v = rng.randint(1, 30)
    del_k = rng.choice(keys)
    code = f"D = {data}\nD[{add_k!r}] = {add_v}\ndel D[{del_k!r}]\nprint(len(D), {keys[0]!r} in D)"
    final = dict(data)
    final[add_k] = add_v
    del final[del_k]
    answer = f"{len(final)} {keys[0] in final}"
    return dict(
        chapter=CH1,
        topic='字典',
        difficulty=1,
        type='short',
        statement_md=(
            '下面代码会输出什么? 格式要求: `<整数> <True/False>`\n\n'
            f'```python\n{code}\n```'
        ),
        answer=answer,
        explanation_md=(
            f'先新增键 `{add_k}` 对应值 `{add_v}`,再删除键 `{del_k}`。最终字典是 `{final}`,'
            f' 所以 `len(D) = {len(final)}`,而 `{keys[0]!r} in D` 为 `{keys[0] in final}`。'
        ),
    )


def t_arrondis(rng):
    correct = '`floor(x)` 对任意实数都表示“向负无穷方向取整”'
    distractors = [
        '`int(x)` 总是和 `floor(x)` 完全相同',
        '`ceil(x)` 表示“向 0 取整”',
        '`round(2.5)` 在 Python 中一定等于 `3`',
    ]
    choices, answer = shuffled_choices(rng, correct, distractors)
    return dict(
        chapter=CH1,
        topic='取整',
        difficulty=2,
        type='mcq',
        statement_md='关于 `int / floor / ceil / round` 的行为,下列哪项说法正确?',
        choices=choices,
        answer=answer,
        explanation_md=(
            '`int` 是向 0 截断,`floor` 是向负无穷取整,`ceil` 是向正无穷取整。'
            '`round` 在 .5 的情形使用银行家舍入,例如 `round(2.5) == 2`。'
        ),
    )


def t_alias(rng):
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    new = rng.randint(50, 99)
    code = f"A = [[{a}, {b}], [{a+1}, {b+1}]]\nB = A[:]\nA[0][0] = {new}\nprint(B[0][0])"
    return dict(
        chapter=CH1,
        topic='拷贝/别名',
        difficulty=2,
        type='short',
        statement_md=f'下面代码会输出什么?\n\n```python\n{code}\n```',
        answer=str(new),
        explanation_md=(
            '`A[:]` 只是浅拷贝:外层列表是新的,但内部子列表仍然共享。'
            f'所以修改 `A[0][0] = {new}` 后,`B[0][0]` 也会变成 `{new}`。'
        ),
    )


def t_tuple_pieges(rng):
    return dict(
        chapter=CH1,
        topic='元组',
        difficulty=1,
        type='mcq',
        statement_md='哪个表达式会得到“只含一个元素 7 的元组(tuple)”?',
        choices=['(7)', '[7]', '(7,)', '{7}'],
        answer='C',
        explanation_md='`(7)` 只是整数 7 外面套括号。单元素元组必须写成 `(7,)`,关键是那个逗号。',
    )


def t_set_litt(rng):
    return dict(
        chapter=CH1,
        topic='集合/字典',
        difficulty=1,
        type='mcq',
        statement_md='哪个表达式会创建“空集合(set)”?',
        choices=['{}', 'set()', '{None}', '()'],
        answer='B',
        explanation_md='`{}` 是空字典(dict),`set()` 才是空集合,`()` 是空元组(tuple)。',
    )


def t_listcomp(rng):
    n = rng.randint(5, 9)
    op = rng.choice(['x*x', 'x+1', '2*x'])
    cond = rng.choice(['x % 2 == 0', 'x % 2 == 1', 'x > 2'])
    expr = f"[{op} for x in range({n}) if {cond}]"
    res = eval(expr)
    return dict(
        chapter=CH1,
        topic='列表推导式',
        difficulty=2,
        type='short',
        statement_md=f'写出下面表达式的结果(按 Python 列表格式填写):\n\n```python\n{expr}\n```',
        answer=str(res),
        explanation_md=(
            f'它遍历 `range({n})`,只保留满足 `{cond}` 的元素,再把每个元素代入 `{op}`。'
            f'结果是 `{res}`。'
        ),
    )


def t_slice(rng):
    values = list(rng.sample(range(10, 30), 8))
    i, j, k = rng.choice([(1, 6, 2), (None, None, -1), (2, None, 1), (None, 4, 1), (-3, None, 1)])
    expr = f"L[{i if i is not None else ''}:{j if j is not None else ''}:{k if k is not None else ''}]"
    res = eval(expr, {'L': values})
    return dict(
        chapter=CH1,
        topic='切片',
        difficulty=2,
        type='short',
        statement_md=f'设 `L = {values}`,求表达式:\n\n```python\n{expr}\n```',
        answer=str(res),
        explanation_md=f'按 `L[i:j:k]` 的切片规则,这里得到的新列表是 `{res}`。',
    )


def t_int_arbitraire(rng):
    n = rng.choice([200, 300, 500])
    return dict(
        chapter=CH1,
        topic='整数',
        difficulty=1,
        type='mcq',
        statement_md=f'关于 Python 的整数 `int`,下面对 `2**{n}` 的说法哪项正确?',
        choices=[
            '可以直接算出,因为 Python 的 int 是任意精度整数',
            '会像 64 位整型一样溢出',
            '会自动变成 `inf`',
            '结果一定是 `float`',
        ],
        answer='A',
        explanation_md='Python 的 `int` 不是固定 64 位,而是任意精度;受限制的是内存,不是位宽。',
    )


def t_complex(rng):
    correct = '`abs(3+4j)` 的值是 `5.0`'
    distractors = [
        '`(3+4j) < (4+5j)` 在 Python 中合法并返回 `True`',
        '`(3+4j).real` 的值是 `4.0`',
        '`(3+4j).imag` 的值是 `3.0`',
    ]
    choices, answer = shuffled_choices(rng, correct, distractors)
    return dict(
        chapter=CH1,
        topic='复数',
        difficulty=2,
        type='mcq',
        statement_md='关于 Python 复数(`complex`),下面哪项说法正确?',
        choices=choices,
        answer=answer,
        explanation_md=(
            '对 `z = 3+4j`,有 `z.real = 3.0`,`z.imag = 4.0`,`abs(z) = 5.0`。'
            '复数不支持 `<`、`>` 这样的大小比较。'
        ),
    )


# ===== CH2 =====
def t_fact(rng):
    correct = '基准情形 `n == 0` 返回 1,递推写成 `n * factorielle(n-1)`'
    distractors = [
        '基准情形 `n == 0` 返回 0,递推写成 `n + factorielle(n-1)`',
        '基准情形 `n == 1` 返回 0,递推写成 `n * factorielle(n-1)`',
        '无论 n 是多少都返回 `factorielle(n-1)`',
    ]
    choices, answer = shuffled_choices(rng, correct, distractors)
    return dict(
        chapter=CH2,
        topic='阶乘递归',
        difficulty=1,
        type='mcq',
        statement_md='如果要递归实现 `factorielle(n)` (`n!`),下面哪种描述是正确的?',
        choices=choices,
        answer=answer,
        explanation_md='因为 `0! = 1`,所以基准情形必须返回 1;对 `n > 0` 时递推关系是 `n! = n × (n-1)!`。',
    )


def t_pgcd(rng):
    correct = '`pgcd(a, b) = pgcd(b, a % b)` ,并在 `b == 0` 时返回 `a`'
    distractors = [
        '`pgcd(a, b) = pgcd(a - 1, b - 1)`',
        '`pgcd(a, b) = pgcd(a, b // 2)`',
        '`pgcd(a, b)` 必须先把 `a` 和 `b` 排序后直接返回较小值',
    ]
    choices, answer = shuffled_choices(rng, correct, distractors)
    return dict(
        chapter=CH2,
        topic='欧几里得算法',
        difficulty=1,
        type='mcq',
        statement_md='关于欧几里得算法 `pgcd(a, b)` 的递推关系,下列哪项正确?',
        choices=choices,
        answer=answer,
        explanation_md='欧几里得算法利用不变量 `pgcd(a, b) = pgcd(b, a % b)`。当 `b = 0` 时,最大公约数就是 `a`。',
    )


def t_fib(rng):
    correct = '使用记忆化(mémoïsation)或缓存,避免重复计算同一个 `fib(k)`'
    distractors = [
        '先把 `n` 转成 `float`,这样会更快',
        '把 `return` 改成 `print`,复杂度就会下降',
        '把递归函数名字换短一点,Python 会少做解析',
    ]
    choices, answer = shuffled_choices(rng, correct, distractors)
    return dict(
        chapter=CH2,
        topic='Fibonacci/记忆化',
        difficulty=2,
        type='mcq',
        statement_md='想把朴素递归版 `fib(n)` 从指数复杂度降到线性复杂度,最直接的方法是什么?',
        choices=choices,
        answer=answer,
        explanation_md='朴素递归会一遍又一遍地重复算同一个 `fib(k)`。加缓存后,每个 `k` 只算一次,时间复杂度可降到 `O(n)`。',
    )


def t_fib_calls(rng):
    n = rng.randint(5, 10)
    return dict(
        chapter=CH2,
        topic='复杂度',
        difficulty=3,
        type='short',
        statement_md=(
            '设有如下朴素递归函数:\n\n'
            '```python\n'
            'def fib2(n):\n'
            '    return n if n <= 1 else fib2(n-1) + fib2(n-2)\n'
            '```\n\n'
            f'记 `c(n)` 为执行 `fib2({n})` 时的**总调用次数**(初始调用本身也算 1 次,且 `c(0)=c(1)=1`)。'
            '请写出 `c(n)` 的具体值。'
        ),
        answer=str(fib2_calls(n)),
        explanation_md=(
            '递推关系是 `c(n) = c(n-1) + c(n-2) + 1`,其中最后那个 `+1` 对应当前这次调用本身。'
            f'因此 `c({n}) = {fib2_calls(n)}`。'
        ),
    )


def t_lambda(rng):
    correct = '`lambda x, y: x + y`'
    distractors = [
        '`lambda x, y: return x + y`',
        '`lambda x, y: if x > y: x else y`',
        '`lambda x, y: x = y`',
    ]
    choices, answer = shuffled_choices(rng, correct, distractors)
    return dict(
        chapter=CH2,
        topic='lambda',
        difficulty=1,
        type='mcq',
        statement_md='下面哪个表达式是**合法**的 Python `lambda`?',
        choices=choices,
        answer=answer,
        explanation_md='`lambda` 后面只能跟“单个表达式”,不能写 `return`、赋值语句,也不能写多行 `if` 语句块。',
    )


def t_gen_count(rng):
    return dict(
        chapter=CH2,
        topic='生成器',
        difficulty=2,
        type='mcq',
        statement_md=(
            '设 `g = (x*x for x in range(4))`。先执行一次 `list(g)`,然后再次执行 `list(g)`。'
            '第二次的结果是什么?'
        ),
        choices=['[]', '[0, 1, 4, 9]', '会返回同一个 generator 对象', '会抛出 SyntaxError'],
        answer='A',
        explanation_md='生成器是“一次性”的。第一次 `list(g)` 已经把它消费完了,第二次再转列表时就只剩空列表 `[]`。',
    )


def t_sort_none(rng):
    return dict(
        chapter=CH2,
        topic='None',
        difficulty=1,
        type='mcq',
        statement_md='执行 `y = [3, 1, 2].sort()` 后,变量 `y` 的值是什么?',
        choices=['[1, 2, 3]', '[3, 1, 2]', 'None', '会报错'],
        answer='C',
        explanation_md='`list.sort()` 是“原地排序”,它修改原列表,但返回值是 `None`。需要新列表时应使用 `sorted(...)`。',
    )


def t_default_arg(rng):
    return dict(
        chapter=CH2,
        topic='默认参数',
        difficulty=3,
        type='mcq',
        statement_md=(
            '设有代码:\n'
            '```python\n'
            'def f(x, L=[]):\n'
            '    L.append(x)\n'
            '    return L\n'
            'f(1); f(2); print(f(3))\n'
            '```\n'
            '最后一行会输出什么?'
        ),
        choices=['[3]', '[1, 2, 3]', '[1, 3]', '会报错'],
        answer='B',
        explanation_md=(
            '默认参数 `L=[]` 在函数定义时只创建一次,后续每次不显式传 `L` 都会复用这同一个列表。'
            '所以三次调用依次把 1、2、3 都追加进去了。'
        ),
    )


def t_quicksort_pivot(rng):
    values = list(rng.sample(range(1, 30), 6))
    pivot = values[0]
    left = [a for a in values[1:] if a < pivot]
    right = [a for a in values[1:] if a >= pivot]
    return dict(
        chapter=CH2,
        topic='快速排序',
        difficulty=2,
        type='short',
        statement_md=(
            '考虑如下递归版快速排序:\n'
            '```python\n'
            'def tri(L):\n'
            '    if not L: return []\n'
            '    x = L[0]\n'
            '    L1 = [a for a in L[1:] if a <  x]\n'
            '    L2 = [a for a in L[1:] if a >= x]\n'
            '    return tri(L1) + [x] + tri(L2)\n'
            '```\n\n'
            f'若输入是 `L = {values}`,第一次分区后 `L1` 是什么? 请按 Python 列表格式填写。'
        ),
        answer=str(left),
        explanation_md=(
            f'首元素 `{pivot}` 是 pivot。所有 `< {pivot}` 的元素进入 `L1`,所以 `L1 = {left}`。'
            f'其余元素进入 `L2 = {right}`。'
        ),
    )


def t_power(rng):
    n = rng.randint(17, 45)
    count = fast_power_mult_count(n)
    return dict(
        chapter=CH2,
        topic='快速幂',
        difficulty=2,
        type='short',
        statement_md=(
            '设快速幂使用如下递归写法:\n'
            '```python\n'
            'def power(A, n):\n'
            '    if n == 0: return 1\n'
            '    if n == 1: return A\n'
            '    if n % 2: return power(A, n-1) * A\n'
            '    B = power(A, n//2)\n'
            '    return B * B\n'
            '```\n\n'
            f'按这段代码计算 `power(A, {n})`,一共需要多少次乘法?'
        ),
        answer=str(count),
        explanation_md=(
            '每遇到奇数 `n` 会先做一次 `power(A, n-1) * A`,每遇到偶数 `n` 会做一次平方。'
            f'沿着递归链一路数下去,总乘法次数是 `{count}`。'
        ),
    )


# ===== CH3 =====
def t_pile(rng):
    ops = []
    stack = []
    for _ in range(6):
        action = rng.choice(['emp', 'emp', 'dep'])
        if action == 'emp':
            value = rng.randint(1, 30)
            stack.append(value)
            ops.append(f'empile(P, {value})')
        elif stack:
            stack.pop()
            ops.append('v ← depile(P)')
    code = '\n'.join(ops)
    return dict(
        chapter=CH3,
        topic='栈',
        difficulty=2,
        type='short',
        statement_md=(
            '初始时栈 `P` 为空。执行下列操作后,请给出栈的最终状态(用 Python 列表表示,格式 `[底, ..., 顶]`)。\n\n'
            f'```\n{code}\n```\n'
            '若为空则填写 `[]`。'
        ),
        answer=str(stack),
        explanation_md='栈遵循 LIFO(后进先出): `empile` 入栈,`depile` 弹出栈顶。最终结果就是按这个顺序模拟得到的。',
    )


def t_file(rng):
    ops = []
    queue = []
    for _ in range(6):
        action = rng.choice(['ajt', 'ajt', 'ext'])
        if action == 'ajt':
            value = rng.randint(1, 30)
            queue.append(value)
            ops.append(f'ajouter_element({value}, F)')
        elif queue:
            queue.pop(0)
            ops.append('v ← extraire_element(F)')
    code = '\n'.join(ops)
    return dict(
        chapter=CH3,
        topic='队列',
        difficulty=2,
        type='short',
        statement_md=(
            '初始时队列 `F` 为空(FIFO)。执行下列操作后,请给出最终状态(按 `[队首, ..., 队尾]` 填写)。\n\n'
            f'```\n{code}\n```\n'
            '若为空则填写 `[]`。'
        ),
        answer=str(queue),
        explanation_md='队列遵循 FIFO(先进先出): `ajouter_element` 在队尾加入,`extraire_element` 从队首取出。',
    )


def t_arbre_taille(rng):
    leaves = [['a'], ['b'], ['c'], ['d'], ['e'], ['f']]
    internal_count = rng.randint(2, 4)
    tree = rng.choice(leaves[:3])
    for _ in range(internal_count):
        child_count = rng.randint(1, 3)
        tree = ['x'] + [tree] + [rng.choice(leaves) for _ in range(child_count - 1)]

    def taille(node):
        return 1 + sum(taille(child) for child in node[1:])

    def hauteur(node):
        if len(node) == 1:
            return 1
        return 1 + max(hauteur(child) for child in node[1:])

    return dict(
        chapter=CH3,
        topic='树',
        difficulty=2,
        type='short',
        statement_md=(
            '树用 `[标签, 子树1, 子树2, ...]` 表示。给定:\n\n'
            f'```\n{tree}\n```\n'
            '请填写 `taille hauteur` 两个整数(空格分隔),其中高度按“根到最深叶子的节点数”计算。'
        ),
        answer=f'{taille(tree)} {hauteur(tree)}',
        explanation_md=(
            f'`taille = {taille(tree)}` 表示节点总数; '
            f'`hauteur = {hauteur(tree)}` 表示从根到最深叶子的节点数。'
        ),
    )


def t_graphe_complet(rng):
    n = rng.choice([3, 4, 5])
    vertices = list(range(1, n + 1))
    graph = {s: set(t for t in vertices if t != s) for s in vertices}
    if rng.random() < 0.5:
        s, t = rng.sample(vertices, 2)
        graph[s].discard(t)
        graph[t].discard(s)
    is_complete = all(graph[s] == set(vertices) - {s} for s in vertices)
    return dict(
        chapter=CH3,
        topic='图',
        difficulty=2,
        type='mcq',
        statement_md=(
            '设无向图用“字典套集合”表示:\n\n'
            f'```\nG = {{ {", ".join(f"{s}: {sorted(graph[s])}" for s in vertices)} }}\n```\n'
            '这个图是完全图(graphe complet)吗?'
        ),
        choices=['是', '否'],
        answer='A' if is_complete else 'B',
        explanation_md='完全图的定义是:每个顶点都与所有其他顶点相连。对照各个邻接集合即可判断。',
    )


def t_euler(rng):
    n = rng.choice([4, 5, 6])
    vertices = list(range(1, n + 1))
    graph = {s: set() for s in vertices}
    edges = set()
    max_edges = n * (n - 1) // 2
    target_edges = min(rng.randint(n, 2 * n), max_edges)
    while len(edges) < target_edges:
        a, b = rng.sample(vertices, 2)
        if (a, b) not in edges and (b, a) not in edges:
            edges.add((a, b))
            graph[a].add(b)
            graph[b].add(a)

    visited = set()
    stack = [vertices[0]]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        stack.extend(graph[node])

    connected = visited == set(vertices)
    odd_count = sum(1 for s in vertices if len(graph[s]) % 2 == 1)
    has_path = connected and odd_count in (0, 2)
    return dict(
        chapter=CH3,
        topic='欧拉',
        difficulty=3,
        type='mcq',
        statement_md=(
            '给定无向图:\n\n'
            f'```\nG = {{ {", ".join(f"{s}: {sorted(graph[s])}" for s in vertices)} }}\n```\n'
            '它是否存在欧拉通路 `chemin eulérien` (每条边恰好经过一次)?'
        ),
        choices=['是', '否'],
        answer='A' if has_path else 'B',
        explanation_md=(
            '欧拉定理:无向图存在欧拉通路,当且仅当它连通且奇度数顶点个数为 0 或 2。'
            f'这里连通性 = {connected},奇度数顶点数 = {odd_count},因此答案是 ' 
            f'`{"是" if has_path else "否"}`。'
        ),
    )


def t_bfs_order(rng):
    vertices = ['A', 'B', 'C', 'D', 'E']
    graph = {'A': {'B', 'C'}, 'B': {'A', 'D'}, 'C': {'A', 'D', 'E'}, 'D': {'B', 'C'}, 'E': {'C'}}
    start = rng.choice(vertices)
    seen = set()
    queue = [start]
    order = []
    while queue:
        node = queue.pop(0)
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for nxt in sorted(graph[node]):
            if nxt not in seen:
                queue.append(nxt)
    return dict(
        chapter=CH3,
        topic='BFS',
        difficulty=2,
        type='short',
        statement_md=(
            "设图 `G = {'A':{'B','C'}, 'B':{'A','D'}, 'C':{'A','D','E'}, 'D':{'B','C'}, 'E':{'C'}}`。\n\n"
            f'从 `{start}` 开始做广度优先搜索(BFS),并且每次都按字母顺序访问邻居。'
            '请写出访问顺序(字母直接连写,例如 `ABCDE`)。'
        ),
        answer=''.join(order),
        explanation_md=f'按 BFS 的“逐层扩展”规则,从 `{start}` 出发得到的访问顺序是 `{"".join(order)}`。',
    )


def t_distance(rng):
    pairs = [('A', 'D', 2), ('A', 'E', 2), ('B', 'E', 3), ('A', 'C', 1), ('B', 'C', 2), ('D', 'E', 2)]
    x, y, distance = rng.choice(pairs)
    return dict(
        chapter=CH3,
        topic='距离/BFS',
        difficulty=2,
        type='short',
        statement_md=(
            "设图 `G = {'A':{'B','C'}, 'B':{'A','D'}, 'C':{'A','D','E'}, 'D':{'B','C'}, 'E':{'C'}}`。"
            f'请给出从 `{x}` 到 `{y}` 的最短距离(边数)。'
        ),
        answer=str(distance),
        explanation_md=f'用 BFS 分层搜索即可得到最短边数距离,这里结果是 `{distance}`。',
    )


def t_pseudo_signature(rng):
    return dict(
        chapter=CH3,
        topic='伪代码',
        difficulty=1,
        type='mcq',
        statement_md='某函数输入一棵树,输出节点总数。下面哪条伪代码签名(signature)最符合本课约定?',
        choices=['fonction f(A) // arbre', 'fonction f(A) // arbre → entier', 'fonction f(A: arbre): entier', 'fonction f(A) → entier'],
        answer='B',
        explanation_md='课程约定是 `fonction nom(args) // 输入类型 → 输出类型`。既要写输入类型,也要写返回类型。',
    )


# ===== CH4 =====
def t_vecteur(rng):
    a, b = rng.randint(-5, 5), rng.randint(-5, 5)
    c, d = rng.randint(-5, 5), rng.randint(-5, 5)
    return dict(
        chapter=CH4,
        topic='Vecteur2d',
        difficulty=1,
        type='short',
        statement_md=(
            '`Vecteur2d` 类有 `__init__(self, x, y)`,`__repr__` 输出 `(x,y)`,`__add__` 按分量相加。\n\n'
            f'那么 `repr(Vecteur2d({a},{b}) + Vecteur2d({c},{d}))` 的结果是什么?'
            '请按精确格式 `(x,y)` 填写,不要空格。'
        ),
        answer=f'({a + c},{b + d})',
        explanation_md=f'按分量相加即可: `({a}+{c}, {b}+{d}) = ({a + c},{b + d})`。',
    )


def t_decimal_mul(rng):
    x1, p1 = rng.randint(2, 99), rng.randint(0, 3)
    x2, p2 = rng.randint(2, 99), rng.randint(0, 3)
    return dict(
        chapter=CH4,
        topic='Decimal',
        difficulty=2,
        type='short',
        statement_md=(
            '`Decimal(x, p)` 表示数 `x · 10^(-p)`。类中 `__mul__` 的规则是:相乘时 `x` 相乘,`p` 相加。\n\n'
            f'设 `P = Decimal({x1}, {p1})`,`Q = Decimal({x2}, {p2})`。'
            '请写出 `P * Q` 的属性 `(x, p)`,格式为 `x p`。'
        ),
        answer=f'{x1 * x2} {p1 + p2}',
        explanation_md=(
            f'根据题设,新的 `x = {x1} × {x2} = {x1 * x2}`,新的 `p = {p1} + {p2} = {p1 + p2}`。'
        ),
    )


def t_trinome(rng):
    a, b, c = rng.randint(-5, 5), rng.randint(-5, 5), rng.randint(-5, 5)
    return dict(
        chapter=CH4,
        topic='Trinome',
        difficulty=2,
        type='short',
        statement_md=(
            '`Trinome(a, b, c)` 表示多项式 `aX² + bX + c`。方法 `derive()` 返回它的导函数,并仍用 `Trinome` 表示(导函数的 `a = 0`)。\n\n'
            f'设 `P = Trinome({a},{b},{c})`。请写出 `P.derive()` 的属性 `(a, b, c)`,格式 `a b c`。'
        ),
        answer=f'0 {2 * a} {b}',
        explanation_md=f'对 `{a}X² + {b}X + {c}` 求导得 `{2 * a}X + {b}`。对应的 `Trinome` 属性就是 `(0, {2 * a}, {b})`。',
    )


def t_dunder_mcq(rng):
    cases = [
        ('x[k]', '__getitem__'),
        ('len(x)', '__len__'),
        ('x + y', '__add__'),
        ('x == y', '__eq__'),
        ('print(x)', '__str__'),
        ('x * y', '__mul__'),
        ('hash(x)', '__hash__'),
        ('for v in x', '__iter__'),
    ]
    expr, dunder = rng.choice(cases)
    distractors = rng.sample([name for _, name in cases if name != dunder], 3)
    choices, answer = shuffled_choices(rng, dunder, distractors)
    return dict(
        chapter=CH4,
        topic='dunder',
        difficulty=1,
        type='mcq',
        statement_md=f'表达式 `{expr}` 会触发哪个特殊方法(dunder method)?',
        choices=choices,
        answer=answer,
        explanation_md=f'在 Python 中,`{expr}` 对应的协议方法就是 `{dunder}`。',
    )


def t_default_attr(rng):
    return dict(
        chapter=CH4,
        topic='类的陷阱',
        difficulty=3,
        type='mcq',
        statement_md='下面哪种写法**能够避免**“共享可变默认值”这个经典坑?',
        choices=[
            'def __init__(self, enfants=[]): self.enfants = enfants',
            'def __init__(self, enfants=None): self.enfants = enfants if enfants is not None else []',
            'enfants = []  # 直接写在类体里',
            'def __init__(self, enfants={}): self.enfants = enfants',
        ],
        answer='B',
        explanation_md='`[]` 和 `{}` 这样的可变对象若作为默认值,会在定义时只创建一次并被后续实例共享。安全写法是 `=None` 再在方法体里新建列表。',
    )


# ===== Long-form algorithmic questions (pseudo-code / application) =====
def t_pseudo_tree_leaf_child(rng):
    statement = (
        '按课程要求的**伪代码**格式,写一个递归函数 `f1(N)`。\n\n'
        '输入是一棵树的根节点 `N`,返回整棵树中“**至少有一个叶子作为孩子**”的节点个数。\n\n'
        '要求:\n'
        '- 必须写 signature\n'
        '- 必须使用伪代码记号(`fonction`, `pour tout`, `retourner`, `←` 等)\n'
        '- 不接受 Python 语法'
    )
    explanation = (
        '一种标准写法如下:\n\n'
        '```text\n'
        'fonction f1(N)\n'
        '// noeud -> entier\n'
        'compte <- 0\n'
        'total <- 0\n'
        'pour tout enfant E de N\n'
        '  total <- total + f1(E)\n'
        '  si nombre d\'enfants(E) = 0\n'
        '    compte <- compte + 1\n'
        'si compte >= 1\n'
        '  total <- total + 1\n'
        'retourner total\n'
        '```\n\n'
        '关键点:当前节点自己的贡献要和所有子树的贡献一起累加。'
    )
    return make_code_question(CH3, '伪代码/树递归', 4, statement, explanation, '请对照下方参考伪代码自评')


def t_pseudo_tree_same_label(rng):
    statement = (
        '按课程要求的**伪代码**格式,写一个递归函数 `f2(N)`。\n\n'
        '输入是一棵带数值标签的树根 `N`,返回整棵树中“**标签与父节点相同**”的节点个数。\n\n'
        '要求:写出 signature,并使用伪代码而不是 Python。'
    )
    explanation = (
        '一种标准写法如下:\n\n'
        '```text\n'
        'fonction f2(N)\n'
        '// noeud -> entier\n'
        'compte <- 0\n'
        'pour tout enfant E de N\n'
        '  si etiquette(E) = etiquette(N)\n'
        '    compte <- compte + 1\n'
        '  compte <- compte + f2(E)\n'
        'retourner compte\n'
        '```\n\n'
        '关键点:比较发生在“父子”之间,所以要先比较 `E` 与 `N`,再递归处理 `E` 的子树。'
    )
    return make_code_question(CH3, '伪代码/树应用', 4, statement, explanation, '请对照下方参考伪代码自评')


def t_pseudo_graph_triangle(rng):
    statement = (
        '按课程要求的**伪代码**格式,写一个函数 `triangle(G)`。\n\n'
        '输入是一个简单无向图 `G`,输出布尔值,表示图中是否存在长度为 3 的环(三角形)。\n\n'
        '要求:必须写 signature,并使用伪代码记号。'
    )
    explanation = (
        '一种典型写法如下:\n\n'
        '```text\n'
        'fonction triangle(G)\n'
        '// graphe -> booleen\n'
        'pour tout sommet x de G\n'
        '  pour tout voisin y de x\n'
        '    pour tout voisin z de y\n'
        '      si z <> x et x est voisin de z\n'
        '        retourner vrai\n'
        'retourner faux\n'
        '```\n\n'
        '核心思想:枚举长度为 2 的路径 `x -> y -> z`,再检查 `x` 和 `z` 是否相邻。'
    )
    return make_code_question(CH3, '伪代码/图算法', 4, statement, explanation, '请对照下方参考伪代码自评')


def t_pseudo_graph_max_degree(rng):
    statement = (
        '按课程要求的**伪代码**格式,写一个函数 `sommet_deg_max(G)`。\n\n'
        '输入是一个非空无向图 `G`,返回一个**度数最大的顶点**(若有多个,返回任意一个即可)。\n\n'
        '要求:必须写 signature,并使用伪代码而不是 Python。'
    )
    explanation = (
        '一种标准写法如下:\n\n'
        '```text\n'
        'fonction sommet_deg_max(G)\n'
        '// graphe -> sommet\n'
        'dmax <- -1\n'
        'pour tout sommet s de G\n'
        '  d <- nombre de voisins de s\n'
        '  si d > dmax\n'
        '    dmax <- d\n'
        '    t <- s\n'
        'retourner t\n'
        '```\n\n'
        '关键点:维护当前最大度数 `dmax` 和对应顶点 `t`。'
    )
    return make_code_question(CH3, '伪代码/图应用', 3, statement, explanation, '请对照下方参考伪代码自评')


def t_code_partial_sums(rng):
    statement = (
        '写一个 Python 函数 `g1(L)`,输入是一个**非空整数列表** `L`,返回它的**前缀和列表**。\n\n'
        '例: `g1([2, 1, 0, 5])` 应返回 `[2, 3, 3, 8]`。\n\n'
        '要求:写出 signature,并给出完整函数。'
    )
    explanation = (
        '一种线性时间实现如下:\n\n'
        '```python\n'
        'def g1(L):\n'
        '    """ list -> list """\n'
        '    cumul = 0\n'
        '    S = []\n'
        '    for x in L:\n'
        '        cumul += x\n'
        '        S.append(cumul)\n'
        '    return S\n'
        '```\n\n'
        '关键点:边遍历边维护累计和 `cumul`,复杂度是 `O(n)`。'
    )
    return make_code_question(CH2, '应用/前缀和', 3, statement, explanation)


def t_code_occurrences_indices(rng):
    statement = (
        '写一个 Python 函数 `occurrences(s)`,输入是字符串 `s`,返回一个字典 `D`。\n\n'
        '对每个在 `s` 中出现过的字符 `c`,有 `D[c]` 等于字符 `c` 在 `s` 中所有出现位置的下标列表。\n\n'
        '例: `occurrences("abcaaca")` 应返回 `{\'a\':[0,3,4,6], \'b\':[1], \'c\':[2,5]}`。\n\n'
        '要求:写出 signature 和完整函数。'
    )
    explanation = (
        '一种标准实现如下:\n\n'
        '```python\n'
        'def occurrences(s):\n'
        '    """ str -> dict """\n'
        '    D = {}\n'
        '    for i, c in enumerate(s):\n'
        '        if c in D:\n'
        '            D[c].append(i)\n'
        '        else:\n'
        '            D[c] = [i]\n'
        '    return D\n'
        '```\n\n'
        '关键点:字典的值是“下标列表”,不是简单计数。'
    )
    return make_code_question(CH1, '应用/字典算法', 4, statement, explanation)


def t_code_search_substring(rng):
    statement = (
        '写一个 Python 函数 `recherche(s1, s2)`,判断字符串 `s1` 是否作为**连续子串**出现在 `s2` 中。\n\n'
        '要求:\n'
        '- 返回布尔值\n'
        '- 写出 signature\n'
        '- 不使用 `in`、`find`、`index` 这类现成查找函数'
    )
    explanation = (
        '一种直接翻译真题伪代码的实现如下:\n\n'
        '```python\n'
        'def recherche(s1, s2):\n'
        '    """ str x str -> bool """\n'
        '    n1 = len(s1)\n'
        '    n2 = len(s2)\n'
        '    for i in range(n2):\n'
        '        k = 0\n'
        '        while k < n1 and i + k < n2 and s1[k] == s2[i + k]:\n'
        '            k += 1\n'
        '        if k == n1:\n'
        '            return True\n'
        '    return False\n'
        '```\n\n'
        '关键点:外层枚举起点 `i`,内层尽量向右匹配。'
    )
    return make_code_question(CH2, '应用/字符串算法', 4, statement, explanation)


def t_code_generator_unique_multiple(rng):
    statement = (
        '写一个**生成器** `g2(L, n)`,其中 `L` 是由正整数组成的列表,`n` 是自然数。\n\n'
        '它要按递增顺序产出所有 `0 <= k <= n` 中,恰好是 `L` 中**一个且仅一个**元素倍数的整数 `k`。\n\n'
        '例: `list(g2([3,7,6], 15))` 应得到 `[3, 7, 9, 14, 15]`。\n\n'
        '要求:写出 signature 和完整函数。'
    )
    explanation = (
        '一种简洁实现如下:\n\n'
        '```python\n'
        'def g2(L, n):\n'
        '    """ list x int -> generator """\n'
        '    for k in range(n + 1):\n'
        '        if sum(k % x == 0 for x in L) == 1:\n'
        '            yield k\n'
        '```\n\n'
        '关键点:对每个 `k` 统计“有多少个 `x in L` 能整除它”,只有等于 1 时才 `yield`。'
    )
    return make_code_question(CH2, '应用/生成器', 4, statement, explanation)


def t_code_memo_suite(rng):
    statement = (
        '定义数列 `u0 = -1`, `u1 = 2`,并且对任意 `n >= 0` 有:\n\n'
        '- 若 `u_n <= 0`,则 `u_(n+2) = 2*u_(n+1) + u_n`\n'
        '- 否则 `u_(n+2) = u_(n+1) - 3*u_n`\n\n'
        '写一个带**记忆化**的递归函数 `suite2(n)`,返回 `u_n`。\n\n'
        '要求:写出 signature,并使用一个字典缓存已经算出的项。'
    )
    explanation = (
        '一种标准写法如下:\n\n'
        '```python\n'
        'D = {0: -1, 1: 2}\n'
        '\n'
        'def suite2(n):\n'
        '    """ int -> int """\n'
        '    if n not in D:\n'
        '        u2 = suite2(n - 2)\n'
        '        u1 = suite2(n - 1)\n'
        '        if u2 <= 0:\n'
        '            D[n] = 2 * u1 + u2\n'
        '        else:\n'
        '            D[n] = u1 - 3 * u2\n'
        '    return D[n]\n'
        '```\n\n'
        '关键点:先判断 `n` 是否已经在缓存里,避免重复递归。'
    )
    return make_code_question(CH2, '应用/记忆化递归', 5, statement, explanation)


def t_code_partitions_generator(rng):
    statement = (
        '写一个**递归生成器** `g5(n)`,其中 `n >= 1`,它要产出所有由**正整数**组成、且元素按**非降序**排列、总和等于 `n` 的列表。\n\n'
        '例: `list(g5(5))` 应产出 `[1,1,1,1,1]`, `[1,1,1,2]`, `[1,2,2]`, `[1,1,3]`, `[2,3]`, `[1,4]`, `[5]`。\n\n'
        '要求:写出 signature 和完整函数。'
    )
    explanation = (
        '一种真题风格的递归生成器如下:\n\n'
        '```python\n'
        'def g5(n):\n'
        '    """ int -> generator """\n'
        '    if n == 1:\n'
        '        yield [1]\n'
        '    else:\n'
        '        for last in range(1, n):\n'
        '            for L in g5(n - last):\n'
        '                if L[-1] <= last:\n'
        '                    yield L + [last]\n'
        '        yield [n]\n'
        '```\n\n'
        '关键点:把结果看作 `A + [last]`,并用 `L[-1] <= last` 保证非降序。'
    )
    return make_code_question(CH2, '应用/递归生成器', 5, statement, explanation)


# ======================================================================
# Template pool
# ======================================================================
BASE_TEMPLATES = [
    t_set_ops,
    t_dict_trace,
    t_arrondis,
    t_alias,
    t_tuple_pieges,
    t_set_litt,
    t_listcomp,
    t_slice,
    t_int_arbitraire,
    t_complex,
    t_fact,
    t_pgcd,
    t_fib,
    t_fib_calls,
    t_lambda,
    t_gen_count,
    t_sort_none,
    t_default_arg,
    t_quicksort_pivot,
    t_power,
    t_pile,
    t_file,
    t_arbre_taille,
    t_graphe_complet,
    t_euler,
    t_bfs_order,
    t_distance,
    t_pseudo_signature,
    t_vecteur,
    t_decimal_mul,
    t_trinome,
    t_dunder_mcq,
    t_default_attr,
]

# 基础 20 题的目标分布:
# CH1 6 题,CH2 6 题,CH3 5 题,CH4 3 题
BASE_ALLOC = {CH1: 6, CH2: 6, CH3: 5, CH4: 3}

# 每套卷额外追加 4 道更像真题的长题:
# 1 道树伪代码 + 1 道图伪代码 + 1 道算法实现 + 1 道递归/生成器应用
EXTRA_PSEUDO_TREE_TEMPLATES = [
    t_pseudo_tree_leaf_child,
    t_pseudo_tree_same_label,
]
EXTRA_PSEUDO_GRAPH_TEMPLATES = [
    t_pseudo_graph_triangle,
    t_pseudo_graph_max_degree,
]
EXTRA_IMPL_TEMPLATES = [
    t_code_partial_sums,
    t_code_occurrences_indices,
    t_code_search_substring,
]
EXTRA_RECURSIVE_TEMPLATES = [
    t_code_generator_unique_multiple,
    t_code_memo_suite,
    t_code_partitions_generator,
]

QUESTIONS_PER_SET = sum(BASE_ALLOC.values()) + 4


def pool_by_chapter():
    pools = {1: [], 2: [], 3: [], 4: []}
    for template in BASE_TEMPLATES:
        q = template(random.Random(0))
        pools[q['chapter']].append(template)
    return pools


# ======================================================================
# Build 15 sets
# ======================================================================
def build_set(set_id):
    rng = random.Random(set_id * 1000 + 7)
    pools = pool_by_chapter()
    base_questions = []
    qid = 1

    for chapter, count in BASE_ALLOC.items():
        templates = pools[chapter][:]
        chosen = []
        while len(chosen) < count:
            rng.shuffle(templates)
            for template in templates:
                if len(chosen) >= count:
                    break
                chosen.append(template)
        for template in chosen:
            q = template(rng)
            q['id'] = f'{set_id}-{qid}'
            qid += 1
            base_questions.append(q)

    rng.shuffle(base_questions)

    extra_questions = [
        rng.choice(EXTRA_PSEUDO_TREE_TEMPLATES)(rng),
        rng.choice(EXTRA_PSEUDO_GRAPH_TEMPLATES)(rng),
        rng.choice(EXTRA_IMPL_TEMPLATES)(rng),
        rng.choice(EXTRA_RECURSIVE_TEMPLATES)(rng),
    ]

    questions = base_questions + extra_questions
    for i, question in enumerate(questions, 1):
        question['id'] = f'{set_id}-{i}'

    return {'id': set_id, 'title': f'第 {set_id} 套模拟卷', 'questions': questions}


def main():
    out = {
        'meta': {
            'course': 'AP2 — 算法与程序设计 2',
            'sets_count': 15,
            'questions_per_set': QUESTIONS_PER_SET,
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
    print(f'OK -> {out_path}  ({total} questions)')


if __name__ == '__main__':
    main()
