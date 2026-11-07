# ENG-07：提示与参考答案

[返回题目与初始化](../讲义/ENG-07_Git提交分支与恢复.md) · [复盘记录](../练习与复盘记录.md)

以下操作仅针对题目中新建的练习仓库。每题重新初始化，避免前一题遗留状态改变结果。

<a id="ex1"></a>

## 第 1 题

| 位置 | 内容 |
|---|---|
| HEAD | value=1 |
| 暂存区 | value=2 |
| 工作区 | value=3 |

git diff 显示 2→3；git diff --staged 显示 1→2；短状态常见 `MM notes.txt`，前一个 M 是暂存区相对 HEAD，后一个是工作区相对暂存区。

此时 commit 记录 2。提交后 HEAD 和暂存区都为 2，工作区仍为 3，仍有一项未暂存修改。若想提交 3，需再次 add，但要先确定这正是你的意图。

可以用 `git show HEAD:notes.txt`、`git show :notes.txt`、`cat notes.txt` 分别观察三处；这比只看编辑器里的文件更明确。

<a id="ex2"></a>

## 第 2 题

提示：两个分支从同一行分开，各自提交，才形成需要 Git 结合处理的分歧。

在新初始化的仓库里：

```bash
printf 'angle_unit=rad\n' > config.txt
git add config.txt
git commit -m "Declare baseline angle unit"
git switch -c feature
printf 'angle_unit=deg\n' > config.txt
git add config.txt
git commit -m "Try degree input"
git switch main
printf 'angle_unit=RAD\n' > config.txt
git add config.txt
git commit -m "Try uppercase unit label"
git merge feature
```

预期 merge 暂停并留下冲突。查看文件和 status，解释双方差异；本题按当前程序只接受 rad 的约定，将整个文件整理成一行 `angle_unit=rad`，不保留标记，再验证配置。

```bash
git add config.txt
git commit -m "Resolve unit conflict using supported radians"
git log --oneline --graph --all
```

真实项目也可能选择支持 deg 并转换，那就要同步修改接口与验证。只统一字符串大小写而不理解物理单位，无法解决真正的数据问题。

<a id="ex3"></a>

## 第 3 题

1. `git restore --staged -- notes.txt`：取消暂存，工作区修改保留。
2. `git restore -- notes.txt`：默认从暂存区恢复工作区文件，丢弃该文件尚未暂存的修改。
3. `git revert --no-edit HEAD`：对干净工作区中的最新普通提交创建反向提交，历史保留。

以上依赖题目的场景；merge commit、多个后续提交或冲突等情况需要另外分析。不要因为三条命令都与“撤销”有关，就互换使用。

<a id="ex4"></a>

## 第 4 题

这题没有唯一提交号或文件划分。验收时检查：

- 两次提交能各自说明问题、行为与验证；第二次没有意外夹入无关配置。
- README 的运行命令真实可用；样例标明合成，数据字段与单位清楚。
- 代码、必要配置、小样例与说明可定位；已有修改是否提交或仍 dirty 如实记录。
- .venv、build 和大结果按项目约定忽略；需要展示的少量结果可有选择保存。

一种起点是忽略 `.venv/`、`__pycache__/`、`build/`、`runs/`，但不要因此忽略所有 CSV、JSON 或图片——其中可能有必要样例与配置。已跟踪文件的处理要单独决定。

