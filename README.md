# AP2 模拟卷站点

> 这个仓库保存可直接发布的网页版本,以及配套的**手写**题库。

## 项目状态

- ✅ **重构题库为手写版本(2026-05)**:取消生成器,改为 10 套**完全手工编写**的考卷,每套围绕一条主线展开,题型与场景互不重复。
- ✅ 自动批改:选择题/简答题逐题判分,代码题手动自评。
- ✅ 打印模式:支持「打印题目」与「打印答案」两种导出模式。
- ✅ 客户端缓存版本号 `2026-05-02-handwritten-v1`,网页会自动拉到最新题库。

## 当前题库

10 套手写考卷(每套约 18-22 题),共约 200 道题。每套覆盖全部 4 章节,但有一条主导主线:

| N° | 主题 | 主导章 |
|----|------|--------|
| 1 | Pièges arithmétiques & types numériques | CH1 |
| 2 | Conteneurs Python(list/tuple/set/dict、可哈希、拷贝) | CH1 |
| 3 | Récursion classique & 复杂度分析 | CH2 |
| 4 | Diviser pour régner & 排序 | CH2 |
| 5 | Itérateurs & générateurs(`yield` / `yield from`) | CH2 |
| 6 | Piles & Files(应用与摊销复杂度) | CH3 |
| 7 | Arbres ordonnés étiquetés(DFS / BFS / 谓词) | CH3 |
| 8 | Graphes — exploration & connexité | CH3 |
| 9 | Cycles eulériens & 结构性质 | CH3 |
| 10 | Classes & objets — synthèse type partiel | CH4 |

## 仓库结构

```
work/web/
├── index.html              ← 网页入口
├── app.js                  ← 答题逻辑 + 自动批改
├── style.css               ← 样式 + 打印样式
├── fascicule.html          ← 复习册页面
├── gen_exams.py            ← (DEPRECATED stub) 仅说明题库已改为手写
├── gen_exams_legacy.py     ← 旧版程序化生成器(归档)
├── README.md               ← 本说明
├── sources/                ← 原始课件 PDF、抽取文本与抽取脚本
└── data/
    ├── exams.json          ← 编译后的最终题库(网页直接读取)
    └── handwritten/
        ├── SHARED_BLUEPRINT.md   ← 题库手写规范(子 agent 入口)
        ├── set_1.json            ← 第 1 套 原始 JSON
        ├── …
        ├── set_10.json           ← 第 10 套 原始 JSON
        ├── _extract.py           ← 从 LLM 输出抽取 JSON 的辅助脚本
        ├── _patch_supplements.py ← 手工补题脚本(CH4 补强等)
        └── _compile.py           ← 合并 + 校验 → exams.json
```

## 使用方法

### 1. 启动网页

```powershell
cd s:\tmp\RESOURCE\ap\work\web
python -m http.server 8000
```

打开 <http://localhost:8000>。

页面说明:
1. 顶部选择 **第 1 套 ~ 第 10 套**。
2. 选择题与简答题自动批改;代码题展示参考解答,自评。
3. 「打印题目」导出空白题目;「打印答案」导出「题目-答案-解析」紧凑版。

### 2. 重新编译题库

如果你修改了任意 `data/handwritten/set_<N>.json`,运行:

```powershell
cd s:\tmp\RESOURCE\ap\work\web\data\handwritten
python _compile.py
```

会重写 `data/exams.json`,并打印每套题量、章节分布、重复检测结果。

### 3. 添加 / 替换题目

直接编辑对应的 `set_<N>.json`(JSON 格式定义见 `SHARED_BLUEPRINT.md`),
然后跑 `_compile.py`。**不要**修改 `data/exams.json` —— 它会被覆盖。

> 升级题库后建议把 `app.js` 顶部的 `DATA_VERSION` 字符串改一个新值,
> 强制浏览器跳过缓存重新拉取。
