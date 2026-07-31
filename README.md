# CS336: Building a Transformer Language Model

这是一个用于学习 Stanford CS336《Language Modeling from Scratch》的个人实践仓库，围绕 Assignment 1: Basics 展开。目标是从基础组件开始，逐步理解并实现一个可训练、可生成文本的 Transformer 语言模型。

> 当前仓库处于学习与开发早期阶段，现有内容主要是 PyTorch 基础概念实验，完整的 Assignment 1 实现仍在持续补充中。

## 学习目标

根据 Assignment 1 的要求，本项目计划覆盖以下内容：

- 训练并实现字节级 BPE（Byte-Pair Encoding）分词器
- 从零实现 decoder-only Transformer 语言模型
- 实现交叉熵损失、AdamW 优化器与余弦学习率调度
- 实现梯度裁剪、批数据采样和模型 checkpoint
- 在 TinyStories 数据集上完成训练、评估与文本生成
- 探索 OpenWebText 训练及不同模型结构的消融实验

## 当前内容

`Assign01/test01` 至 `Assign01/test07` 是一组循序渐进的 PyTorch 小实验：

| 文件 | 内容 |
| --- | --- |
| `test01` | Token ID 与 embedding 张量形状 |
| `test02` | Softmax 与概率分布 |
| `test03` | 负对数似然的直观含义 |
| `test04` | 交叉熵、反向传播与参数更新 |
| `test05` | 批量分类的交叉熵计算 |
| `test06` | 语言模型中的逐 token loss |
| `test07` | 使用 SGD 优化 logits 的完整小循环 |

作业说明位于 [`Assign01/cs336_assignment1_basics.pdf`](Assign01/cs336_assignment1_basics.pdf)。

## 项目结构

```text
CS336/
├── Assign01/
│   ├── cs336_assignment1_basics.pdf
│   ├── test01
│   ├── test02
│   ├── ...
│   └── test07
└── README.md
```

## 环境要求

- Python 3.10+
- PyTorch

建议使用虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install torch
```

## 运行示例

这些脚本没有 `.py` 后缀，但可以直接交给 Python 运行：

```bash
python Assign01/test01
python Assign01/test04
python Assign01/test07
```

运行全部示例（PowerShell）：

```powershell
Get-ChildItem Assign01/test* | ForEach-Object { python $_.FullName }
```

## 开发路线

- [x] Embedding、Softmax 与交叉熵基础实验
- [x] Autograd 与简单优化循环
- [ ] BPE tokenizer
- [ ] Transformer 基础模块
- [ ] AdamW 与学习率调度
- [ ] 训练循环与 checkpoint
- [ ] 文本生成与困惑度评估
- [ ] TinyStories / OpenWebText 实验

## 说明

本仓库仅用于个人学习与课程实践，不代表 Stanford University 或 CS336 课程团队。课程材料及原始作业要求的版权归其各自权利人所有。使用本仓库内容时，请遵守课程的学术诚信与 AI 使用政策。

## 致谢

- [Stanford CS336: Language Modeling from Scratch](https://stanford-cs336.github.io/spring2026/)
- [CS336 Assignment 1: Basics](https://github.com/stanford-cs336/assignment1-basics)

