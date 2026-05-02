"""Patch under-filled sets with 2-3 hand-written supplement questions each.
Run after _extract.py / before _compile.py."""
import json
from pathlib import Path

HERE = Path(__file__).parent

# All supplements are CH4 (objects) — chapter under-represented in theme sets.
SUPPLEMENTS = {
    4: [
        # set 4 needs 1 more CH4 question (already has 1)
        {
            "chapter": 4,
            "topic": "__add__ et immutabilité",
            "difficulty": 3,
            "type": "code",
            "statement_md": "On définit la classe `Fraction` ci-dessous (les fractions ne sont **pas** simplifiées automatiquement) :\n\n```python\nclass Fraction:\n    def __init__(self, n, d):\n        self.n, self.d = n, d\n    def __repr__(self):\n        return f'{self.n}/{self.d}'\n```\n\nÉcrire la méthode `__add__(self, other)` qui retourne une **nouvelle** `Fraction` égale à `self + other`, sans modifier `self` ni `other`. Donner aussi un exemple : que renvoie `Fraction(1, 6) + Fraction(1, 4)` (sans simplification) ?",
            "answer": "nouvelle Fraction(self.n*other.d + other.n*self.d, self.d*other.d) ; ex 10/24",
            "explanation_md": "**思路**：分数加法 a/b + c/d = (a·d + c·b) / (b·d)，**不**要在原对象上修改属性，必须返回**新对象**（保持不可变行为）。\n\n```python\ndef __add__(self, other):\n    return Fraction(self.n * other.d + other.n * self.d,\n                    self.d * other.d)\n```\n\n例：`Fraction(1, 6) + Fraction(1, 4)` → `Fraction(1*4 + 1*6, 6*4)` = `10/24`（未化简）。\n\n⚠️ 若错误地写成 `self.n = ...` 会**改变左操作数**，破坏 `+` 运算符的纯函数性质。"
        }
    ],
    6: [
        # set 6 needs 2 more questions, one CH4
        {
            "chapter": 4,
            "topic": "Pile orientée objet",
            "difficulty": 3,
            "type": "code",
            "statement_md": "Implémenter une classe `Pile` LIFO en POO, avec liste interne `self._t`. Méthodes attendues : `__init__()`, `est_vide()`, `empiler(x)`, `depiler()` (assert si vide), `sommet()`, `__len__()`, `__repr__()` au format `'(bas) [...] (haut)'`. Donner le code complet.",
            "answer": "self._t = [] ; append/pop ; assert non vide ; __repr__ utilise self._t",
            "explanation_md": "```python\nclass Pile:\n    def __init__(self):\n        self._t = []\n    def est_vide(self):\n        return len(self._t) == 0\n    def empiler(self, x):\n        self._t.append(x)\n    def depiler(self):\n        assert not self.est_vide(), 'pile vide'\n        return self._t.pop()\n    def sommet(self):\n        assert not self.est_vide(), 'pile vide'\n        return self._t[-1]\n    def __len__(self):\n        return len(self._t)\n    def __repr__(self):\n        return f'(bas) {self._t} (haut)'\n```\n\n所有操作 `O(1)` 摊销（`append`/`pop` 末尾）。`__repr__` 让 `print(p)` 一目了然。"
        },
        {
            "chapter": 3,
            "topic": "File via deux piles",
            "difficulty": 4,
            "type": "code",
            "statement_md": "**Astuce classique** : simuler une file (FIFO) en utilisant **deux** piles `P_in` et `P_out`. Décrire en pseudo-code :\n\n1. `ajouter_element(x)` (enfile `x`)\n2. `extraire_element()` (défile)\n\nDonner ensuite la **complexité amortie** par opération.",
            "answer": "ajouter: empiler dans P_in O(1) ; extraire: si P_out vide, vider P_in dans P_out (renverse) puis depiler P_out ; amorti O(1)",
            "explanation_md": "**伪代码**：\n```\nfonction ajouter_element(x)\n  empiler(P_in, x)\n\nfonction extraire_element()\n  si est_vide(P_out)\n    tant que non est_vide(P_in)\n      empiler(P_out, depiler(P_in))\n  retourner depiler(P_out)\n```\n\n**摊销分析**：每个元素最多被压入/弹出 P_in 一次、P_out 一次，共 4 次基本操作。所以 n 次队列操作总开销 O(n)，**摊销** O(1)。\n\n⚠️ 单次 `extraire_element` 在 P_out 为空时是 O(k)（k 是 P_in 大小），但摊销下来仍是 O(1)。这是经典的「会计法 / 势能法」分析。"
        }
    ],
    8: [
        # set 8 needs 1 more CH4 question
        {
            "chapter": 4,
            "topic": "Graphe en classe",
            "difficulty": 3,
            "type": "code",
            "statement_md": "Définir une classe `Graphe` (non orienté simple) ayant l'attribut interne `self._adj : dict[sommet, set[sommet]]`. Implémenter au moins :\n- `__init__()`\n- `ajouter_sommet(s)`\n- `ajouter_arete(s, t)` (ajoute aussi les sommets si nécessaire)\n- `voisins(s) -> set`\n- `__len__()` (renvoie l'ordre = nombre de sommets)\n\nIndiquer la complexité de chaque opération.",
            "answer": "self._adj = {} ; ajouter_arete vérifie/insère, set.add(t) et set.add(s) ; toutes O(1) amorti",
            "explanation_md": "```python\nclass Graphe:\n    def __init__(self):\n        self._adj = {}\n    def ajouter_sommet(self, s):\n        if s not in self._adj:\n            self._adj[s] = set()\n    def ajouter_arete(self, s, t):\n        self.ajouter_sommet(s)\n        self.ajouter_sommet(t)\n        self._adj[s].add(t)\n        self._adj[t].add(s)\n    def voisins(self, s):\n        return self._adj[s]\n    def __len__(self):\n        return len(self._adj)\n```\n\n**复杂度**：所有操作均为 `O(1)` 摊销（`dict` 查找/插入和 `set.add` 都是 O(1)）。\n\n⚠️ 注意 `voisins(s)` 返回的是**内部 set 的引用**——外部如果修改它会破坏图结构。生产代码可考虑返回 `frozenset(self._adj[s])` 拷贝。"
        }
    ],
    9: [
        # set 9 needs 1 more, prefer CH4 to stabilize coverage
        {
            "chapter": 4,
            "topic": "Multigraphe en classe",
            "difficulty": 4,
            "type": "code",
            "statement_md": "On veut une classe `Multigraphe` qui accepte des **arêtes multiples** (plusieurs arêtes entre les mêmes sommets). On stocke pour chaque paire de sommets le **nombre** d'arêtes :\n\n- attribut `self._adj : dict[sommet, dict[sommet, int]]` (multiplicité).\n\nÉcrire la méthode `degre(self, s)` qui retourne le **degré** de `s` au sens multigraphe (chaque arête, même multiple, compte une fois). Préciser pourquoi cette définition est exactement celle qui apparaît dans le théorème d'Euler.",
            "answer": "sum(self._adj[s].values()) ; le théorème d'Euler compte les passages d'arêtes, donc multiplicités",
            "explanation_md": "```python\ndef degre(self, s):\n    return sum(self._adj[s].values())\n```\n\n**为什么是这个定义？** 欧拉定理统计的是**每条边经过的次数**。若 s 与 t 之间有 3 条平行边，画一笔时每条都要走过一次，所以 s 和 t 的「度数」各自要加 3。普通图（简单图）正好是「多重图退化为多重度 1」的特例，所以公式 `sum(_adj[s].values())` 在两种情形都正确。\n\n⚠️ 若错把 `len(self._adj[s])` 当成度，会忽略多重边，导致 Königsberg 这种典型问题判断错误。"
        }
    ],
}


def patch():
    for sid, extras in SUPPLEMENTS.items():
        f = HERE / f"set_{sid}.json"
        data = json.loads(f.read_text(encoding="utf-8"))
        # Insert supplements at positions guaranteed to survive a 22-cap.
        # If existing questions > 18, replace last few (which are usually weakest).
        qs = data["questions"]
        for i, e in enumerate(extras):
            target = min(20 + i, len(qs))
            qs.insert(target, e)
        # Trim any over 22
        if len(qs) > 22:
            data["questions"] = qs[:22]
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  patched set_{sid}.json -> {len(data['questions'])} questions")


if __name__ == "__main__":
    patch()
