# AP2 — Cahier des charges pour les 10 examens manuscrits

> Lis ce document AVANT d'écrire les questions. Il définit le contrat strict.

## 1. Objectif global
- 10 examens d'entraînement, **rédigés à la main**, profonds et variés.
- Chaque examen : **20 questions** thématiquement cohérentes mais couvrant les 4 chapitres.
- Aucun chevauchement sémantique entre examens (ni énoncé, ni snippet de code, ni scénario).
- Priorité absolue : **profondeur de connaissance**, pas la quantité.

## 2. Découpage des 20 questions par examen (gabarit recommandé)
| Slots | Type | But |
|---|---|---|
| Q1–Q5 | mcq / short rapides | concepts, pièges, lecture de code (1 ligne) |
| Q6–Q10 | short / code (court) | calcul, trace, mini-fonction |
| Q11–Q15 | code / short | algorithmes, ADT, parcours |
| Q16–Q18 | code (moyen) | implémentation complète d'une fonction |
| Q19–Q20 | code (long) | sujet type partiel (pseudo-code, classe, ou algorithme avec spécification) |

Souplesse : ±2 dans chaque catégorie selon le thème. **Au moins 2 questions par chapitre** dans chaque examen.

## 3. Distribution des chapitres (par examen)
- Le thème principal de l'examen domine (~10–12 questions).
- Les 3 autres chapitres : ~2–4 questions chacun (révision/transversal).
- **Aucun examen ne doit ignorer un chapitre.**

## 4. Schéma JSON exact à produire
Chaque sous-agent produit **UN seul objet JSON** correspondant à un examen :

```json
{
  "id": <int 1..10>,
  "title": "第 N 套 — <titre court FR>",
  "focus": "<phrase courte FR ou ZH décrivant le thème, 1 ligne>",
  "questions": [
    {
      "chapter": 1,
      "topic": "<courte étiquette FR, ex: 'round / floor / ceil'>",
      "difficulty": 1,
      "type": "mcq",
      "statement_md": "...",
      "choices": ["...", "...", "...", "..."],
      "answer": "A",
      "explanation_md": "..."
    },
    { ... 19 autres ... }
  ]
}
```

### Champs obligatoires
- `id` : entier, identique au numéro de l'examen attribué.
- `title` : `第 N 套 — <Titre français court>` (le préfixe en chinois est conservé).
- `focus` : 1 phrase, en français (ou bilingue) — décrit l'angle.
- `questions` : exactement **20** entrées.
- Pour chaque question :
  - `chapter` ∈ {1, 2, 3, 4}
  - `topic` : étiquette courte (~3 mots) — utilisée comme tag, en français.
  - `difficulty` ∈ {1, 2, 3, 4, 5} (1 facile → 5 sujet de partiel).
  - `type` ∈ {`mcq`, `short`, `code`}.
  - `statement_md` : énoncé en Markdown.
    - Le tronc principal de l'énoncé est en **français** (style cours Moisan).
    - **Toutes les explications de contexte / commentaires d'aide / intuitions** ajoutées sont en **chinois**, intercalées si utile (`> 提示：...`).
    - Tu peux mettre des blocs ` ```python ` pour le code.
  - `choices` : présent **uniquement** si `type=="mcq"`, **exactement 4** entrées, distinctes, plausibles.
  - `answer` :
    - `mcq` : une seule lettre `"A"|"B"|"C"|"D"`.
    - `short` : chaîne **courte et déterministe**, normalisable (le grader supprime espaces, met en minuscules, accepte synonymes booléens fr/zh, équivalence ensembliste pour `{a,b,c}`).
      - Préfère des sorties uniques : `"7"`, `"True"`, `"[1,2,3]"`, `"{1,2,3}"`, `"O(n log n)"`, `"5292 1"`, etc.
      - Si plusieurs réponses sont acceptables, choisis l'énoncé pour qu'il n'y en ait qu'une.
    - `code` : une **brève indication** (1 phrase ≤ 80 caractères) servant de "réponse de référence courte" affichée dans la fiche imprimée. **La vraie correction** va dans `explanation_md`.
  - `explanation_md` : explication concise en **chinois** (la langue de l'utilisateur). Pour les `code`, inclure la solution de référence dans un bloc ` ```python ` suivi de quelques lignes d'analyse / complexité / piège.

### Contraintes anti-doublon
- Les énoncés doivent être **textuellement distincts** entre examens.
- Pas de réutilisation de noms de fonctions emblématiques (e.g. `pgcd`, `fact`) dans plusieurs énoncés — varie les noms et les scénarios narratifs.
- Pas de "même problème, mais avec un autre nombre". Change la structure du problème.

## 5. Style de cours (référence Moisan)
- Les pseudo-codes doivent **éviter la syntaxe Python pure** (utiliser `←`, `pour tout x dans E`, `tant que`, `retourner`, indentation). Les blocs `python` sont réservés aux questions où on demande explicitement du Python.
- Préciser **signature** quand c'est demandé (`f : type1 × type2 → type`).
- Donner les conditions préalables / hypothèses (`# pre: L est triée`, etc.).
- Pour les ADT (pile, file, arbre, graphe), respecter les noms d'opérations vus en cours :
  - Pile : `pile_vide`, `est_vide`, `empiler`, `depiler`, `sommet`.
  - File : `file_vide`, `est_vide`, `ajouter_element`, `extraire_element`, `premier_element`.
  - Arbre : `etiquette(N)`, `enfants(N)`, `creer_noeud(e, L)`.
  - Graphe (dict de set) : `sommets(G)`, `voisins(G, s)`, `ajouter_sommet/arete`, `supprimer_sommet/arete`.

## 6. Bornes de scope (ne pas dépasser)
- **OK** : tout ce qui est dans `KNOWLEDGE.md` et dans les `partiel_correction*.txt`.
- **À éviter** : démonstrations hors-programme (Tychonoff, Jordan-Hölder, FLT, p-adique…). Le cours est AP2 L1 informatique, **pas** théorie avancée.
- Pour les codes : pas de bibliothèques exotiques. `math`, `cmath`, `copy` autorisés. Pas de `numpy`, `pandas`.

## 7. Bonnes pratiques pour un `short` correct
- Demander **le résultat exact** d'une expression Python.
- Demander **un nombre**, **un booléen**, **un littéral** (`[1,2,3]`, `{1,2,3}`, `(1,2)`), ou **une chaîne courte** (`"O(n log n)"`).
- Si tu demandes un `set`, le grader compare en équivalence ensembliste.
- N'utilise pas de retour à la ligne dans `answer`.

## 8. Bonnes pratiques pour un `mcq`
- Les 4 propositions doivent être de longueur comparable et toutes plausibles.
- Une seule est correcte.
- Pas de "toutes les réponses ci-dessus" ni de "aucune".

## 9. Bonnes pratiques pour un `code`
- Énoncé : décrire une **fonction** à implémenter, donner sa signature, 2–3 cas d'exemple `>>> f(...) → ...`.
- `answer` : phrase d'indice ("récursion sur la liste des enfants, accumulateur", etc.)
- `explanation_md` : code Python complet, court (≤ 25 lignes), lisible, + commentaire complexité.

## 10. Livraison
- Écris ton fichier directement à : `s:\tmp\RESOURCE\ap\work\web\data\handwritten\set_<N>.json`.
- **JSON pur** (UTF-8, indentation 2). Aucune prose autour.
- Vérifie : 20 questions, schéma respecté, lettres MCQ entre A et D, etc.

---

## 11. Plan thématique des 10 examens

| N° | Thème principal | Sujets-clés à couvrir | Cas longs Q19–Q20 |
|---|---|---|---|
| 1 | **Pièges arithmétiques & types numériques** (CH1) | int illimité, IEEE 754, `int/round/floor/ceil`, `complex`, `math`, divisions | (1) trace de `round` sur 6 valeurs négatives (2) fonction `presque_egal(x,y,eps)` |
| 2 | **Conteneurs Python : list / tuple / set / dict, hashabilité, copies** (CH1) | slicing, alias vs copy vs deepcopy, comprehensions, `frozenset`, dict pivot | (1) implémenter `inverser_dict(D)` (2) trace d'un alias 2D + question de hashabilité |
| 3 | **Récursion classique & complexité** (CH2) | terminaison, complexité de fib double, mémoïsation, Hanoï, Syracuse | (1) implémenter `bin_to_int(s)` récursif (2) compter le nombre d'appels de fib2(n) |
| 4 | **Diviser pour régner & tri** (CH2) | quicksort/tri-fusion, exponentiation rapide, recherche dichotomique | (1) `tri_fusion` complet (2) `power_mat(M, n)` ou recherche dichotomique sur tableau |
| 5 | **Itérateurs & générateurs** (CH2) | genexp vs comprehension, `yield`, `yield from`, générateurs récursifs (partitions, sous-ensembles) | (1) générateur `sous_ensembles(E)` (2) générateur `partitions_decroissantes(n)` |
| 6 | **Piles & Files** (CH3) | applications : parenthèses bien formées, évaluation post-fixe, simulation FIFO, conversion | (1) évaluation post-fixe (RPN) (2) simulation file d'attente avec stats |
| 7 | **Arbres** (CH3) | implémentation liste imbriquée, taille/hauteur, parcours profondeur/largeur, prédicats sur étiquettes | (1) `feuilles(A)` retourne la liste (2) prédicat "tout nœud a au plus k enfants" |
| 8 | **Graphes — exploration & connexité** (CH3) | dict de set, DFS/BFS, `distance(G,x,y)`, composantes connexes, matrice d'adjacence | (1) `nb_composantes(G)` (2) BFS retournant le dict des distances depuis une source |
| 9 | **Cycles eulériens & propriétés structurelles** (CH3) | théorème d'Euler, multigraphe, application "1 trait", cycle hamiltonien (mention seulement) | (1) `a_chemin_eulerien(G)` complet (2) construire un cycle eulérien sur petit exemple, expliquer théorème |
| 10 | **Classes & objets — synthèse type partiel** (CH4 + transverse) | dunder, `__init__`/`__repr__`/`__add__`/`__eq__`, encapsulation, classes pour ADT | (1) classe `Polynome` avec `+`, `*`, `derive`, `__repr__` (2) classe `FileChainee` avec maillon (linked list) |

## 12. Auto-vérification finale (avant de rendre)
- [ ] Exactement 20 questions.
- [ ] `mcq` ont exactement 4 `choices`.
- [ ] `answer` ne dépend pas de l'environnement (pas de timestamp, pas d'aléatoire).
- [ ] Chaque chapitre apparaît au moins 2 fois.
- [ ] Pas deux questions presque identiques **dans le même examen**.
- [ ] Pas de réutilisation littérale d'un énoncé / scénario du fichier `KNOWLEDGE.md` ou des `partiel_correction*.txt` (s'inspirer, pas recopier).
