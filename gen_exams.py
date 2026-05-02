"""DEPRECATED — n'utilise plus ce fichier.

Le banque de questions est désormais **écrite à la main**, dans
`data/exams.json`. Les sources brutes par examen vivent dans
`data/handwritten/set_<N>.json` (1 ≤ N ≤ 10) et sont compilées par
`data/handwritten/_compile.py`.

L'ancien générateur procédural est conservé sous
`gen_exams_legacy.py` pour référence historique.

Pour régénérer `data/exams.json` à partir des fichiers manuscrits :

    cd data/handwritten
    python _compile.py
"""

import sys

if __name__ == "__main__":
    print(__doc__)
    sys.exit(0)
