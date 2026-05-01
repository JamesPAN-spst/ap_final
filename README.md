# AP2 模拟卷站点

> 这个仓库保存可直接发布的网页版本,以及与之配套的题库生成器。

## 项目状态

- ✅ 重写考试1-15：使用详细计划生成360道题，避免重复，基于课程材料和往年格式。
- ✅ 优化打印功能：添加“打印题目”和“打印答案”模式，直接显示“问题-答案-解析”无需提交。
- ✅ 更新文档：刷新README.md和EXAM_BLUEPRINT.md，同步最新结构。
- ✅ 验证系统：确认无重复题，打印模式正常，题库可复现。

## 仓库结构

```
work/web/
├── index.html          ← 网页入口
├── app.js              ← 答题逻辑 + 自动批改
├── style.css           ← 样式 + 打印样式
├── fascicule.html      ← 复习册页面
├── gen_exams.py        ← 15 套模拟卷生成器
├── EXAM_BLUEPRINT.md   ← 模板试卷与 15 套覆盖计划
├── README.md           ← 当前说明文档
├── sources/            ← 原始课件 PDF、抽取文本与抽取脚本
└── data/
    └── exams.json      ← 360 道题数据(15 套 × 24 题)
```

## 使用方法

### 1. 启动网页

因为浏览器直接打开 `file://` 页面时通常会拦截 `fetch`,建议在仓库根目录起一个本地服务器:

```powershell
cd s:\tmp\RESOURCE\ap\work\web
python -m http.server 8000
```

然后打开 <http://localhost:8000>。

页面说明:
1. 顶部可选择 **第 1 套** 到 **第 15 套**。
2. 每套固定 **24 题**:Q1-Q10 是 trace/细节判断,Q11-Q15 是短编程,Q16-Q20 是伪代码/ADT,Q21-Q24 是长题。
3. 选择题和简答题支持自动批改。
4. 代码题展示参考实现,通过“我做对了 / 我做错了”手动自评。
5. 可以使用 **打印题目** 导出空白题目,或使用 **打印答案** 导出紧凑版“题目-答案-解析”。答案打印不需要先提交,也不需要展开解析。

### 2. 重新生成题库

在仓库根目录直接运行生成器:

```powershell
cd s:\tmp\RESOURCE\ap\work\web
python gen_exams.py
```

脚本会重写 `data/exams.json`。当前的种子规则是 `set_id * 1000 + 7`,所以同一份代码每次生成的 15 套题都可复现。

题库结构与覆盖计划见 [EXAM_BLUEPRINT.md](EXAM_BLUEPRINT.md)。

### 3. 查看原始材料

仓库里现在已经包含一份整理过的源材料目录 [work/web/sources/README.md](work/web/sources/README.md):

1. `sources/pdf/` 保存原始 PDF 课件、练习和考卷更正。
2. `sources/text/` 保存从 PDF 抽取出的文本版本。
3. `sources/extract_pdfs.py` 可在仓库内直接重新生成这些文本文件。

## 题目结构

| 模块 | 数量 | 覆盖内容 |
|---|---:|---|
| Q1-Q10 | 10 | Python 类型细节、函数参数、递归 trace、ADT 概念、dunder 与类陷阱 |
| Q11-Q15 | 5 | 列表/字典/集合短算法、简单递归、生成器、类方法补全 |
| Q16-Q20 | 5 | `pile`, `file`, `arbre`, `graphe`, BFS/DFS/Euler 等伪代码题 |
| Q21-Q24 | 4 | 记忆化递归、树/图算法、Decimal/Trinome/Arbre 类、递归生成器 |

## 说明

- 题库是按每套卷的考点蓝图生成的,答案由代码同步计算或由对应参考实现给出。
- 自动批改本质上还是字符串比对,虽然已经做了空格、真假值和集合顺序归一化,极端格式差异仍可能需要人工判断。
- 原始 PDF 与抽取文本也已经并入仓库中的 `sources/` 目录,后续发布与维护以这里为准。
