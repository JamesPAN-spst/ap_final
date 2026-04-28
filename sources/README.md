# AP2 源材料

这个目录保存站点之外的原始材料,主要用于追溯题库和复习内容的来源。

## 目录结构

```
sources/
├── pdf/                ← 原始 PDF 文件
├── text/               ← 从 PDF 抽取出的文本文件
├── extract_pdfs.py     ← 重新抽取文本的脚本
└── README.md           ← 当前说明
```

## 内容说明

### 课程课件

- `1-types_python.pdf`
- `2-fonctions.pdf`
- `3-types.pdf`
- `4-objets.pdf`

### 作业与练习

- `dm1.pdf` 到 `dm3.pdf`
- `exos1.pdf` 到 `exos12.pdf`

### 考卷与更正

- `exam_correction (1).pdf`
- `exam2024_correction (1).pdf`
- `entrainement_correction.pdf`
- `partiel_correction (2).pdf`
- `partiel_correction (3).pdf`
- `partiel_correction_points (1).pdf`

## 文本文件

- `text/` 下的文件是从对应 PDF 抽出来的纯文本版本。
- 其中 `3-types.pdf` 由于页数较多,被拆成了 `3-types__part1.txt` 到 `3-types__part5.txt`。
- 这些文本保留原始内容的可搜索版本,便于后续整理、比对和再次生成资料。

## 重新抽取

如果后面你替换了 PDF,可以在仓库根目录运行:

```powershell
cd s:\tmp\RESOURCE\ap\work\web
python .\sources\extract_pdfs.py
```

脚本会读取 `sources/pdf/` 下的 PDF,并重写 `sources/text/` 里的文本文件。