# ENG-07 Pro Git 中英对照精读（快照、暂存与撤销）

[学习指南](../学习指南.md) · [ENG-07 讲义](ENG-07_Git提交分支与恢复.md) · [知识索引](../知识索引.md#eng-07)

> 这份文件解决一件事：把 ENG-07 需要的 Pro Git 原文和中文译文放在同一页，再配一组**独立于你练习仓库**的真实命令输出。
> 读法：先读「原文」和「译文」，两段对照；再看「实例」里我在 `/tmp` 下新建的演示仓库跑出的输出；「批注」是我的补充，选读。
> 全文约 90 分钟可以读完一遍；明天做练习时把它当手册查，不必一次背下来。

---

## 0. 为什么要先读这三节

ENG-07 的四道题只涉及 Git 的很小的一个面：

- 第 1 题问「我改的 3 为什么没进提交」——考的是**暂存区**这个概念；
- 第 2 题处理同一行冲突——考的是**分支与合并**；
- 第 3 题区分三种撤销——考的是**工作区、暂存区、提交**三个位置分别怎么改；
- 第 4 题给项目留两次可解释的提交——考的是**提交的粒度与说明**。

这四题背后是同一个模型：**Git 保存的是快照，提交从暂存区取内容，分支只是指向提交的指针。** 下面第 1、2 节讲模型，第 3 节讲日常命令，第 4 节讲撤销，第 5 节讲分支与冲突。模型看懂之后，命令只是查表。

---

## 1. Git 记录的是快照，不是差异

### 原文（Pro Git, 1.3 What is Git? — Snapshots, Not Differences）

> The major difference between Git and any other VCS (Subversion and friends included) is the way Git thinks about its data.
> Conceptually, most other systems store information as a list of file-based changes.
> These other systems (CVS, Subversion, Perforce, and so on) think of the information they store as a set of files and the changes made to each file over time (this is commonly described as _delta-based_ version control).
>
> Git doesn't think of or store its data this way.
> Instead, Git thinks of its data more like a series of snapshots of a miniature filesystem.
> With Git, every time you commit, or save the state of your project, Git basically takes a picture of what all your files look like at that moment and stores a reference to that snapshot.
> To be efficient, if files have not changed, Git doesn't store the file again, just a link to the previous identical file it has already stored.
> Git thinks about its data more like a *stream of snapshots*.

### 译文（Pro Git 中文版，1.3 Git 基础 — 直接记录快照，而非差异比较）

> Git 和其它版本控制系统（包括 Subversion 和近似工具）的主要差别在于 Git 对待数据的方式。从概念上来说，其它大部分系统以文件变更列表的方式存储信息，这类系统（CVS、Subversion、Perforce 等等）将它们存储的信息看作是一组基本文件和每个文件随时间逐步累积的差异（它们通常称作 *基于差异（delta-based）* 的版本控制）。
>
> Git 不按照以上方式对待或保存数据。反之，Git 更像是把数据看作是对小型文件系统的一系列快照。在 Git 中，每当你提交更新或保存项目状态时，它基本上就会对当时的全部文件创建一个快照并保存这个快照的索引。为了效率，如果文件没有修改，Git 不再重新存储该文件，而是只保留一个链接指向之前存储的文件。Git 对待数据更像是一个 *快照流*。

### 批注

这句话直接决定了三个日常事实：

1. **提交不是「打补丁」，而是「拍一张全量照片」。** 所以 `git diff` 是「拿两个快照比」，`git log` 是「翻相册」，不是逐条重放补丁。
2. **照片拍的是「暂存区当时的样子」，不是「你现在磁盘上的样子」。** 这一点是第 1 题的全部要害：`git add` 之后又改文件，照片已经拍好了，磁盘上的新改动不在照片里。
3. **快照之间只存差异作为优化，但概念模型始终是快照。** 因此后面「分支只是指向某个快照的指针」才成立。

---

## 2. 三个区域与文件状态

### 原文（Pro Git, 1.3 — The Three States）

> Pay attention now -- here is the main thing to remember about Git if you want the rest of your learning process to go smoothly.
> Git has three main states that your files can reside in: _modified_, _staged_, and _committed_:
>
> * Modified means that you have changed the file but have not committed it to your database yet.
> * Staged means that you have marked a modified file in its current version to go into your next commit snapshot.
> * Committed means that the data is safely stored in your local database.
>
> This leads us to the three main sections of a Git project: the working tree, the staging area, and the Git directory.
>
> The working tree is a single checkout of one version of the project.
> These files are pulled out of the compressed database in the Git directory and placed on disk for you to use or modify.
>
> The staging area is a file, generally contained in your Git directory, that stores information about what will go into your next commit.
> Its technical name in Git parlance is the "`index`", but the phrase "`staging area`" works just as well.
>
> The Git directory is where Git stores the metadata and object database for your project.
> This is the most important part of Git, and it is what is copied when you _clone_ a repository from another computer.
>
> The basic Git workflow goes something like this:
>
> 1. You modify files in your working tree.
> 2. You selectively stage just those changes you want to be part of your next commit, which adds _only_ those changes to the staging area.
> 3. You do a commit, which takes the files as they are in the staging area and stores that snapshot permanently to your Git directory.

### 译文（Pro Git 中文版，1.3 — 三种状态）

> 现在请注意，如果你希望后面的学习更顺利，请记住下面这些关于 Git 的概念。Git 有三种状态，你的文件可能处于其中之一：*已提交（committed）*、*已修改（modified）* 和 *已暂存（staged）*。
>
> * 已修改表示修改了文件，但还没保存到数据库中。
> * 已暂存表示对一个已修改文件的当前版本做了标记，使之包含在下次提交的快照中。
> * 已提交表示数据已经安全地保存在本地数据库中。
>
> 这会让我们的 Git 项目拥有三个阶段：工作区、暂存区以及 Git 目录。
>
> 工作区是对项目的某个版本独立提取出来的内容。这些从 Git 仓库的压缩数据库中提取出来的文件，放在磁盘上供你使用或修改。
>
> 暂存区是一个文件，保存了下次将要提交的文件列表信息，一般在 Git 仓库目录中。按照 Git 的术语叫做“索引”，不过一般说法还是叫“暂存区”。
>
> Git 仓库目录是 Git 用来保存项目的元数据和对象数据库的地方。这是 Git 中最重要的部分，从其它计算机克隆仓库时，复制的就是这里的数据。
>
> 基本的 Git 工作流程如下：
>
> 1. 在工作区中修改文件。
> 2. 将你想要下次提交的更改选择性地暂存，这样只会将更改的部分添加到暂存区。
> 3. 提交更新，找到暂存区的文件，将快照永久性存储到 Git 目录。

### 一张表记住三个位置

| 位置 | Git 里叫什么 | 里面放什么 | 谁改它 |
|---|---|---|---|
| 工作区 | working tree | 你正在编辑的文件 | 编辑器、`git restore --worktree`、切换分支 |
| 暂存区 | staging area / index | 下一次 `git commit` 会拍进快照的内容 | `git add`、`git restore --staged`、`git rm` |
| 提交历史 | Git directory（`.git/objects`） | 已经拍好的快照与提交对象 | `git commit`、`git revert`、`git merge` |

对应到文件状态：**未跟踪（untracked）→ 已暂存（staged）→ 已提交（committed）**，提交之后再改就是**已修改（modified）**，回到暂存区需要再 `git add` 一次。

### 批注

`git add` 不是「把这个文件加入 Git 跟踪，以后改动都自动进提交」。它做的是「**把此刻这份内容写入暂存区**」。这句话在 Pro Git 2.2 里有一句很准确的概括，下一节会引到。

---

## 3. 日常循环：status / diff / add / commit

### 3.1 已跟踪与未跟踪

#### 原文（Pro Git, 2.2 — 开头）

> Remember that each file in your working directory can be in one of two states: _tracked_ or _untracked_.
> Tracked files are files that were in the last snapshot, as well as any newly staged files; they can be unmodified, modified, or staged.
> In short, tracked files are files that Git knows about.
>
> Untracked files are everything else -- any files in your working directory that were not in your last snapshot and are not in your staging area.
> When you first clone a repository, all of your files will be tracked and unmodified because Git just checked them out and you haven't edited anything.
>
> As you edit files, Git sees them as modified, because you've changed them since your last commit.
> As you work, you selectively stage these modified files and then commit all those staged changes, and the cycle repeats.

#### 译文（Pro Git 中文版，2.2 — 开头）

> 请记住，你工作目录下的每一个文件都不外乎这两种状态：*已跟踪* 或 *未跟踪*。已跟踪的文件是指那些被纳入了版本控制的文件，在上一次快照中有它们的记录，在工作一段时间后，它们的状态可能是未修改，已修改或已放入暂存区。简而言之，已跟踪的文件就是 Git 已经知道的文件。
>
> 工作目录中除已跟踪文件外的其它所有文件都属于未跟踪文件，它们既不存在于上次快照的记录中，也没有被放入暂存区。初次克隆某个仓库的时候，工作目录中的所有文件都属于已跟踪文件，并处于未修改状态，因为 Git 刚刚检出了它们，而你尚未编辑过它们。
>
> 编辑过某些文件之后，由于自上次提交后你对它们做了修改，Git 将它们标记为已修改文件。在工作时，你可以选择性地将这些修改过的文件放入暂存区，然后提交所有已暂存的修改，如此反复。

### 3.2 看状态：`git status` 与 `git status -s`

#### 原文（Pro Git, 2.2 — Checking the Status / Short Status）

> The main tool you use to determine which files are in which state is the `git status` command.
> If you run this command directly after a clone, you should see something like this: [...]
> This means you have a clean working directory; in other words, none of your tracked files are modified.
> Git also doesn't see any untracked files, or they would be listed here.
>
> You can see that your new `README` file is untracked, because it's under the "`Untracked files`" heading in your status output.
> Untracked basically means that Git sees a file you didn't have in the previous snapshot (commit), and which hasn't yet been staged; Git won't start including it in your commit snapshots until you explicitly tell it to do so.
>
> While the `git status` output is pretty comprehensive, it's also quite wordy.
> Git also has a short status flag so you can see your changes in a more compact way.
> If you run `git status -s` or `git status --short` you get a far more simplified output from the command: [...]
> There are two columns to the output -- the left-hand column indicates the status of the staging area and the right-hand column indicates the status of the working tree.

#### 译文（Pro Git 中文版，2.2 — 检查当前文件状态 / 状态简览，节选）

> 可以用 `git status` 命令查看哪些文件处于什么状态。如果在克隆仓库后立即使用此命令，会看到类似这样的输出：……
> 这说明你现在的工作目录相当干净。换句话说，所有已跟踪文件在上次提交后都未被更改过。此外，上面的信息还表明，当前目录下没有出现任何处于未跟踪状态的新文件，否则 Git 会在这里列出来。
>
> 在状态报告中可以看到新建的 `README` 文件出现在 `Untracked files` 下面。未跟踪的文件意味着 Git 在之前的快照（提交）中没有这些文件；Git 不会自动将之纳入跟踪范围，除非你明明白白地告诉它“我需要跟踪该文件”。
>
> `git status` 命令的输出十分详细，但其用语有些繁琐。Git 有一个选项可以帮你缩短状态命令的输出，这样可以以简洁的方式查看更改。……输出中有两栏，左栏指明了暂存区的状态，右栏指明了工作区的状态。

#### 实例：无跟踪文件时的完整输出

以下输出来自 `/tmp/eng07-demo2`（我新建的演示仓库，`README.md` 已提交，`app.conf` 刚创建）：

```console
$ git status
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	app.conf

nothing added to commit but untracked files present (use "git add" to track)
```

```console
$ git status -s
?? app.conf
```

#### 批注：短状态两列怎么读

`git status -s` 输出两列：**左列 = 暂存区相对 HEAD**，**右列 = 工作区相对暂存区**。常见组合：

| 输出 | 含义 |
|---|---|
| `?? file` | 未跟踪 |
| `A  file` | 新文件已暂存 |
| ` M file` | 已跟踪文件被改，但未暂存 |
| `M  file` | 已暂存，工作区与暂存区一致 |
| `MM file` | 暂存后又改了（第 1 题的状态） |
| `UU file` | 合并冲突，双方都改了同一处 |

Pro Git 用 ` M README`、`MM Rakefile`、`A  lib/git.rb`、`M  lib/simplegit.rb`、`?? LICENSE.txt` 这组输出解释同一件事：左列看「准备提交什么」，右列看「还没准备什么」。

### 3.3 `git add` 到底做了什么

#### 原文（Pro Git, 2.2 — Staging Modified Files）

> To stage it, you run the `git add` command.
> `git add` is a multipurpose command -- you use it to begin tracking new files, to stage files, and to do other things like marking merge-conflicted files as resolved.
> It may be helpful to think of it more as "`add precisely this content to the next commit`" rather than "`add this file to the project`".
>
> It turns out that Git stages a file exactly as it is when you run the `git add` command.
> If you commit now, the version of `CONTRIBUTING.md` as it was when you last ran the `git add` command is how it will go into the commit, not the version of the file as it looks in your working directory when you run `git commit`.
> If you modify a file after you run `git add`, you have to run `git add` again to stage the latest version of the file. [...]

#### 译文（Pro Git 中文版，2.2 — 暂存已修改的文件，节选）

> 要暂存这次更新，需要运行 `git add` 命令。这是个多功能命令：可以用它开始跟踪新文件，或者把已跟踪的文件放到暂存区，还能用于合并时把有冲突的文件标记为已解决状态等。将这个命令理解为“精确地将内容添加到下一次提交中”而不是“将一个文件添加到项目中”要更加合适。
>
> 实际上 Git 只不过暂存了你运行 `git add` 命令时的版本。如果你现在提交，`CONTRIBUTING.md` 的版本是你最后一次运行 `git add` 命令时的那个版本，而不是你运行 `git commit` 时，在工作目录中的当前版本。所以，运行了 `git add` 之后又作了修订的文件，需要重新运行 `git add` 把最新版本重新暂存起来。

#### 实例：一次 `add` 之后又改，状态变成 `MM`

```console
$ printf 'retries=7\n' > app.conf
$ git add app.conf
$ printf 'retries=9\n' > app.conf
$ git status -s
MM app.conf
```

此时直接 `git commit`，提交的是 **7**，不是 9。`git diff` 与 `git diff --staged` 分别显示两段不同的变化：

```console
$ git diff                 # 工作区 9  vs  暂存区 7
diff --git a/app.conf b/app.conf
@@ -1 +1 @@
-retries=7
+retries=9

$ git diff --staged        # 暂存区 7  vs  HEAD 5
diff --git a/app.conf b/app.conf
@@ -1 +1 @@
-retries=5
+retries=7
```

#### 批注

这就是第 1 题的标准场景：`add` 记录 2，随后改成 3，于是 `git diff` 看到 2→3，`git diff --staged` 看到 1→2；直接 `commit` 只会把 2 写进历史，3 仍留在工作区（状态 ` M`）。

### 3.4 `git diff` 与 `git diff --staged`

#### 原文（Pro Git, 2.2 — Viewing Your Staged and Unstaged Changes）

> If the `git status` command is too vague for you -- you want to know exactly what you changed, not just which files were changed -- you can use the `git diff` command.
> We'll cover `git diff` in more detail later, but you'll probably use it most often to answer these two questions: What have you changed but not yet staged? And what have you staged that you are about to commit?
> Although `git status` answers those questions very generally by listing the file names, `git diff` shows you the exact lines added and removed -- the patch, as it were. [...]
>
> That command compares what is in your working directory with what is in your staging area.
> The result tells you the changes you've made that you haven't yet staged.
>
> If you want to see what you've staged that will go into your next commit, you can use `git diff --staged`.
> This command compares your staged changes to your last commit: [...]
>
> It's important to note that `git diff` by itself doesn't show all changes made since your last commit -- only changes that are still unstaged.
> If you've staged all of your changes, `git diff` will give you no output.
> ( `--staged` and `--cached` are synonyms. )

#### 译文（Pro Git 中文版，2.2 — 查看已暂存和未暂存的修改，节选）

> 如果 `git status` 命令的输出对于你来说过于简略，而你想知道具体修改了什么地方，可以用 `git diff` 命令。你通常可能会用它来回答这两个问题：当前做的哪些更新尚未暂存？有哪些更新已暂存并准备好下次提交？
>
> 此命令比较的是工作目录中当前文件和暂存区域快照之间的差异。也就是修改之后还没有暂存起来的变化内容。
>
> 若要查看已暂存的将要添加到下次提交里的内容，可以用 `git diff --staged` 命令。这条命令将比对已暂存文件与最后一次提交的文件差异。
>
> 请注意，git diff 本身只显示尚未暂存的改动，而不是自上次提交以来所做的所有改动。所以有时候你一下子暂存了所有更新过的文件，运行 `git diff` 后却什么也没有，就是这个原因。（`--staged` 和 `--cached` 是同义词。）

#### 批注：三个比较方向

| 命令 | 比较对象 | 回答的问题 |
|---|---|---|
| `git diff` | 工作区 ↔ 暂存区 | 我还有哪些改动没放进下一次提交？ |
| `git diff --staged` | 暂存区 ↔ HEAD | 下一次提交会比当前提交多什么？ |
| `git diff HEAD` | 工作区 ↔ HEAD | 两者合计一共改了什么？ |

第 4 题要求「用 `diff` 检查要提交的文件」，优先看前两条：先确认舞台上是你要的东西，再确认工作区没有漏进来的杂物。

### 3.5 提交：`git commit` 与 `-a`

#### 原文（Pro Git, 2.2 — Committing Your Changes / Skipping the Staging Area）

> Now that your staging area is set up the way you want it, you can commit your changes.
> Remember that anything that is still unstaged -- any files you have created or modified that you haven't run `git add` on since you edited them -- won't go into this commit.
> They will stay as modified files on your disk. [...]
>
> Remember that the commit records the snapshot you set up in your staging area.
> Anything you didn't stage is still sitting there modified; you can do another commit to add it to your history.
> Every time you perform a commit, you're recording a snapshot of your project that you can revert to or compare to later. [...]
>
> Adding the `-a` option to the `git commit` command makes Git automatically stage every file that is already tracked before doing the commit, letting you skip the `git add` part.
> This is convenient, but be careful; sometimes this flag will cause you to include unwanted changes.

#### 译文（Pro Git 中文版，2.2 — 提交更新 / 跳过使用暂存区域，节选）

> 现在的暂存区已经准备就绪，可以提交了。在此之前，请务必确认还有什么已修改或新建的文件还没有 `git add` 过，否则提交的时候不会记录这些尚未暂存的变化。这些已修改但未暂存的文件只会保留在本地磁盘。
>
> 请记住，提交时记录的是放在暂存区域的快照。任何还未暂存文件的仍然保持已修改状态，可以在下次提交时纳入版本管理。每一次运行提交操作，都是对你项目作一次快照，以后可以回到这个状态，或者进行比较。
>
> 只要在提交的时候，给 `git commit` 加上 `-a` 选项，Git 就会自动把所有已经跟踪过的文件暂存起来一并提交，从而跳过 `git add` 步骤。这很方便，但是要小心，有时这个选项会将不需要的文件添加到提交中。

#### 批注

- `git commit -m "..."` 适合一句话能说清的提交；信息要写「做了什么、为什么」，不是「更新」「修改」。
- `-a` 只自动暂存**已跟踪**文件；新文件仍然要 `git add`。
- `-a` 会把所有已跟踪文件的改动一起提交，做第 1 题那种「只想要 2、不想要 3」的场景时不要用。

### 3.6 `.gitignore`

#### 原文（Pro Git, 2.2 — Ignoring Files，节选）

> Often, you'll have a class of files that you don't want Git to automatically add or even show you as being untracked.
> These are generally automatically generated files such as log files or files produced by your build system.
> In such cases, you can create a file listing patterns to match them named `.gitignore`.
> Here is an example `.gitignore` file:
>
> ```console
> $ cat .gitignore
> *.[oa]
> *~
> ```
>
> The rules for the patterns you can put in the `.gitignore` file are as follows:
>
> * Blank lines or lines starting with `#` are ignored.
> * Standard glob patterns work, and will be applied recursively throughout the entire working tree.
> * You can start patterns with a forward slash (`/`) to avoid recursivity.
> * You can end patterns with a forward slash (`/`) to specify a directory.
> * You can negate a pattern by starting it with an exclamation point (`!`).

#### 译文（Pro Git 中文版，2.2 — 忽略文件，节选）

> 一般我们总会有些文件无需纳入 Git 的管理，也不希望它们总出现在未跟踪文件列表。通常都是些自动生成的文件，比如日志文件，或者编译过程中创建的临时文件等。在这种情况下，我们可以创建一个名为 `.gitignore` 的文件，列出要忽略的文件的模式。
>
> 文件 `.gitignore` 的格式规范如下：
>
> * 所有空行或者以 `#` 开头的行都会被 Git 忽略。
> * 可以使用标准的 glob 模式匹配，它会递归地应用在整个工作区中。
> * 匹配模式可以以（`/`）开头防止递归。
> * 匹配模式可以以（`/`）结尾指定目录。
> * 要忽略指定模式以外的文件或目录，可以在模式前加上叹号（`!`）取反。

#### 实例：忽略 `logs/` 与 `*.log`

```console
$ printf '*.log\nlogs/\n' > .gitignore
$ mkdir -p logs && printf 'run 1: ok\n' > logs/run.log
$ git status -s
?? .gitignore
$ git check-ignore -v logs/run.log
.gitignore:2:logs/	logs/run.log
```

`git status -s` 里看不到 `logs/run.log`，因为第 2 条规则把它排除了；`.gitignore` 自身是未跟踪文件，需要单独 `git add`。

#### 批注

`.gitignore` **只影响未跟踪文件**。已经进过提交的文件不会被它「删掉」，需要 `git rm --cached <file>` 从索引移除（文件仍在磁盘），再提交。第 4 题里 `.venv`、`build/`、大 `runs/` 属于这一类。

---

## 4. 撤销：改的是哪个位置

### 4.1 改最后一次提交：`git commit --amend`

#### 原文（Pro Git, 2.4 Undoing Things）

> One of the common undos takes place when you commit too early and possibly forget to add some files, or you mess up your commit message.
> If you want to redo that commit, make the additional changes you forgot, stage them, and commit again using the `--amend` option:
>
> ```console
> $ git commit --amend
> ```
>
> This command takes your staging area and uses it for the commit.
> If you've made no changes since your last commit (for instance, you run this command immediately after your previous commit), then your snapshot will look exactly the same, and all you'll change is your commit message. [...]
>
> It's important to understand that when you're amending your last commit, you're not so much fixing it as _replacing_ it entirely with a new, improved commit that pushes the old commit out of the way and puts the new commit in its place.
> Effectively, it's as if the previous commit never happened, and it won't show up in your repository history.
>
> Only amend commits that are still local and have not been pushed somewhere.

#### 译文（Pro Git 中文版，2.4 撤消操作）

> 有时候我们提交完了才发现漏掉了几个文件没有添加，或者提交信息写错了。此时，可以运行带有 `--amend` 选项的提交命令来重新提交：
>
> ```console
> $ git commit --amend
> ```
>
> 这个命令会将暂存区中的文件提交。如果自上次提交以来你还未做任何修改（例如，在上次提交后马上执行了此命令），那么快照会保持不变，而你所修改的只是提交信息。……
>
> 当你在修补最后的提交时，与其说是修复旧提交，倒不如说是完全用一个 *新的提交* 替换旧的提交，理解这一点非常重要。从效果上来说，就像是旧有的提交从未存在过一样，它并不会出现在仓库的历史中。

#### 批注

`--amend` 不是「编辑历史」，而是「**新建一个提交替换旧的**」。如果旧提交已经推送到共享分支，别人可能已经基于它工作，此时修补会让对方的历史对不上。本项目自己的仓库在推送前可以放心用。

### 4.2 取消暂存：`git restore --staged`

#### 原文（Pro Git, 2.4 — Unstaging a Staged File with git restore）

> Git version 2.23.0 introduced a new command: `git restore`.
> It's basically an alternative to `git reset` which we just covered.
> From Git version 2.23.0 onwards, Git will use `git restore` instead of `git reset` for many undo operations.
>
> The next two sections demonstrate how to work with your staging area and working directory changes with `git restore`.
> For example, let's say you've changed two files and want to commit them as two separate changes, but you accidentally type `git add *` and stage them both.
> How can you unstage one of the two?
> The `git status` command reminds you:
>
> ```console
> $ git add *
> $ git status
> On branch master
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
> 	modified:   CONTRIBUTING.md
> 	renamed:    README.md -> README
> ```
>
> Right below the "`Changes to be committed`" text, it says use `git restore --staged <file>...` to unstage.
> So, let's use that advice to unstage the `CONTRIBUTING.md` file:
>
> ```console
> $ git restore --staged CONTRIBUTING.md
> $ git status
> ...
> Changes not staged for commit:
>   (use "git add <file>..." to update what will be committed)
>   (use "git restore <file>..." to discard changes in working directory)
> 	modified:   CONTRIBUTING.md
> ```
>
> The `CONTRIBUTING.md` file is modified but once again unstaged.

<!-- 官方中文版此处尚未同步 git restore 小节，以下为对上述英文的逐句直译。 -->

#### 译文（本节中文版尚未收录，以下是逐句直译）

> Git 2.23.0 引入了一个新命令：`git restore`。它基本上是我们刚介绍过的 `git reset` 的替代品。从 Git 2.23.0 起，Git 在许多撤销操作中会用 `git restore` 代替 `git reset`。
>
> 接下来的两小节演示如何用 `git restore` 处理暂存区和工作区的改动。例如，你改了两个文件、想把它们分成两次提交，却不小心输入了 `git add *` 把两个都暂存了。怎么取消其中一个？`git status` 会提醒你：
>
> ```
> $ git add *
> $ git status
> On branch master
> Changes to be committed:
>   (use "git restore --staged <file>..." to unstage)
> 	modified:   CONTRIBUTING.md
> 	renamed:    README.md -> README
> ```
>
> 在 "Changes to be committed" 正文下面，它写着用 `git restore --staged <file>...` 取消暂存。所以我们就照着提示取消 `CONTRIBUTING.md` 的暂存：
>
> ```
> $ git restore --staged CONTRIBUTING.md
> $ git status
> ...
> Changes not staged for commit:
>   (use "git add <file>..." to update what will be committed)
>   (use "git restore <file>..." to discard changes in working directory)
> 	modified:   CONTRIBUTING.md
> ```
>
> `CONTRIBUTING.md` 仍然是已修改，但重新变成了未暂存状态。

#### 实例：`M ` → ` M`

```console
$ git add app.conf
$ git status -s
M  app.conf
$ git restore --staged app.conf
$ git status -s
 M app.conf
```

暂存区被恢复成 HEAD 的内容，**工作区文件一点没动**（`app.conf` 里仍是 `retries=9`）。

#### 批注

`git restore --staged` 只改暂存区；把它想成「把要拍的照片从相册里撤下来，但磁盘上的文件还在」。要同时改工作区，再加 `--worktree`（默认只改工作区，不带 `--staged` 时反而危险，见 4.3）。

### 4.3 丢弃工作区修改：`git restore`

#### 原文（Pro Git, 2.4 — Unmodifying a Modified File with git restore）

> What if you realize that you don't want to keep your changes to the `CONTRIBUTING.md` file?
> How can you easily unmodify it -- revert it back to what it looked like when you last committed (or initially cloned, or however you got it into your working directory)?
> Luckily, `git status` tells you how to do that, too. [...]
>
> ```console
> $ git restore CONTRIBUTING.md
> ```
>
> It's important to understand that `git restore <file>` is a dangerous command.
> Any local changes you made to that file are gone -- Git just replaced that file with the last staged or committed version.
> Don't ever use this command unless you absolutely know that you don't want those unsaved local changes.

#### 译文（本节中文版尚未收录，以下是逐句直译）

> 如果你发现不想保留对 `CONTRIBUTING.md` 的修改，怎么办？怎样才能方便地「取消修改」——把它还原成上次提交（或最初克隆、或任何把它放进工作目录时）的样子？幸运的是，`git status` 也会告诉你该怎么做。
>
> ```
> $ git restore CONTRIBUTING.md
> ```
>
> 务必理解 `git restore <file>` 是一个危险的命令。你对这个文件所做的任何本地修改都会消失——Git 只是用最近一次暂存或提交的版本替换了它。除非你完全确定不想要这些未保存的本地修改，否则不要使用这个命令。

#### 实例：`restore` 后回到暂存区版本

```console
$ git status -s
 M app.conf
$ git restore app.conf
$ cat app.conf
retries=7
$ git status -s
```

第 3 题场景 2 就是这样：`notes.txt` 工作区里有一份确认不要的修改，`git restore notes.txt` 把它还原成暂存区内容。**这份修改不会进 Git，也无法再找回。**

#### 批注

`git restore` 默认从**暂存区**取内容覆盖工作区。若暂存区与 HEAD 一致，效果就是「回到上次提交」；若暂存区里有新内容（`M `），恢复的是暂存区那份。要指定来源可以用 `--source=<commit>`。

### 4.4 创建一个反向提交：`git revert`

#### 原文（git-revert 手册 DESCRIPTION / EXAMPLES）

> Given one or more existing commits, revert the changes that the related patches introduce, and record some new commits that record them.
> This requires your working tree to be clean (no modifications from the HEAD commit).
>
> Note: _git revert_ is used to record some new commits to reverse the effect of some earlier commits (often only a faulty one).
> If you want to throw away all uncommitted changes in your working directory, you should see git-reset[1], particularly the `--hard` option.
> If you want to extract specific files as they were in another commit, you should see git-restore[1], specifically the `--source` option. [...]
>
> `git revert HEAD~3`
>
> Revert the changes specified by the fourth last commit in HEAD and create a new commit with the reverted changes.

#### 译文（git-revert 手册简体中文版，描述 / 实例）

> 给定一个或多个现有提交，还原相关补丁引入的更改，并记录一些新提交来记录这些更改。这要求你的工作区是干净的（没有对 HEAD 提交的修改）。
>
> 注意：*git revert* 用于记录一些新的提交，以扭转先前提交（通常只是错误的提交）的影响。如果您想丢弃工作区中所有未提交的改动，请参阅 git-reset[1]，尤其是 `--hard` 选项。如果你想提取其他提交中的特定文件，请参阅 git-restore[1]，尤其是 `--source` 选项。使用这些选项时要小心，因为它们都会丢弃工作区中未提交的改动。
>
> `git revert HEAD~3`
>
> 还原 HEAD 中倒数第四个提交指定的更改，并创建一个包含还原更改的新提交。

#### 实例：撤销最近一次实验提交

```console
$ printf 'retries=retry(3)\n' > app.conf
$ git add app.conf && git commit -qm "exp: switch retries to retry(3)"
$ git revert --no-edit HEAD
[main 1d5636d] Revert "exp: switch retries to retry(3)"
 1 file changed, 1 insertion(+), 1 deletion(-)
$ cat app.conf
retries=7
$ git log --oneline -4
1d5636d Revert "exp: switch retries to retry(3)"
0294d5d exp: switch retries to retry(3)
0b9e121 chore: bump retries to 7
3233607 feat: add app.conf
```

历史里多了一条 `Revert "..."`，旧提交仍在。这正是「保留历史、撤销效果」：适合已经提交、甚至已经推送的提交。

#### 批注：四种「撤销」对照

| 命令 | 改动位置 | 历史 | 典型场景 | 危险性 |
|---|---|---|---|---|
| `git commit --amend` | 用暂存区替换最后一次提交 | 重写最后一条 | 漏文件、写错信息，尚未推送 | 已推送后使用会害到协作者 |
| `git restore --staged <file>` | 暂存区 → HEAD | 不动 | 误 `add`，想拆开提交 | 低 |
| `git restore <file>` | 工作区 → 暂存区 | 不动 | 确认丢弃未暂存修改 | **高**，未提交修改永久丢失 |
| `git revert <commit>` | 新增一个反向提交 | 追加 | 撤销已提交（甚至已推送）的提交 | 低，但冲突时要手工解决 |
| `git reset --hard <commit>` | 工作区 + 暂存区 + 分支指针 | 丢弃之后的提交 | 本地彻底回退 | **最高**，本课不要求 |

---

## 5. 分支与合并

### 5.1 分支只是一个指针

#### 原文（Pro Git, 3.1 Branches in a Nutshell，节选）

> A branch in Git is simply a lightweight movable pointer to one of these commits.
> The default branch name in Git is `master`.
> As you start making commits, you're given a `master` branch that points to the last commit you made.
> Every time you commit, the `master` branch pointer moves forward automatically. [...]
>
> Because a branch in Git is actually a simple file that contains the 40 character SHA-1 checksum of the commit it points to, branches are cheap to create and destroy.
> Creating a new branch is as quick and simple as writing 41 bytes to a file (40 characters and a newline).

#### 译文（Pro Git 中文版，3.1 分支简介，节选）

> Git 的分支，其实本质上仅仅是指向提交对象的可变指针。Git 的默认分支名字是 `master`。在多次提交操作之后，你其实已经有一个指向最后那个提交对象的 `master` 分支。`master` 分支会在每次提交时自动向前移动。
>
> 由于 Git 的分支实质上仅是包含所指对象校验和（长度为 40 的 SHA-1 值字符串）的文件，所以它的创建和销毁都异常高效。创建一个新分支就相当于往一个文件中写入 41 个字节（40 个字符和 1 个换行符）。

#### 批注

所以「开分支」不复制文件、不占额外空间，只是多了一个指针文件。`HEAD` 则指向「你当前在哪个分支上」。

### 5.2 切换分支：`git switch` / `git checkout`

#### 原文（Pro Git, 3.1 — Switching Branches，节选）

> To switch to an existing branch, you run the `git checkout` command.
> Let's switch to the new `testing` branch: [...]
> This moves `HEAD` to point to the `testing` branch. [...]
>
> It's important to note that when you switch branches in Git, files in your working directory will change.
> If you switch to an older branch, your working directory will be reverted to look like it did the last time you committed on that branch.
> If Git cannot do it cleanly, it will not let you switch at all.
>
> From Git version 2.23 onwards you can use `git switch` instead of `git checkout` to:
> * Switch to an existing branch: `git switch testing-branch`.
> * Create a new branch and switch to it: `git switch -c new-branch`.
> * Return to your previously checked out branch: `git switch -`.

#### 译文（Pro Git 中文版，3.1 分支切换，节选）

> 要切换到一个已存在的分支，你需要使用 `git checkout` 命令。……这样 `HEAD` 就指向 `testing` 分支了。
>
> 在切换分支时，一定要注意你工作目录里的文件会被改变。如果是切换到一个较旧的分支，你的工作目录会恢复到该分支最后一次提交时的样子。如果 Git 不能干净利落地完成这个任务，它将禁止切换分支。

#### 批注

`switch` 是 2.23 之后的新命令，语义比 `checkout` 清楚（`checkout` 还能检出文件，容易和「切换分支」混淆）。本仓库的 Git 版本支持 `switch`，练习里用哪个都行，但同一份记录里最好统一。

### 5.3 合并：快进与三方合并

#### 原文（Pro Git, 3.2 Basic Branching and Merging，节选）

> You'll notice the phrase "`fast-forward`" in that merge.
> Because the commit pointed to by the branch you merged in was directly upstream of the commit you're on, Git simply moves the pointer forward.
> To phrase that another way, when you try to merge one commit with a commit that can be reached by following the first commit's history, Git simplifies things by moving the pointer forward because there is no divergent work to merge together -- this is called a "`fast-forward`". [...]
>
> In this case, your development history has diverged from some older point.
> Because the commit on the branch you're on isn't a direct ancestor of the branch you're merging in, Git has to do some work.
> In this case, Git does a simple three-way merge, using the two snapshots pointed to by the branch tips and the common ancestor of the two. [...]
>
> Instead of just moving the branch pointer forward, Git creates a new snapshot that results from this three-way merge and automatically creates a new commit that points to it.
> This is referred to as a merge commit, and is special in that it has more than one parent.

#### 译文（Pro Git 中文版，3.2 分支的新建与合并，节选）

> 在合并的时候，你应该注意到了“快进（fast-forward）”这个词。由于你想要合并的分支所指向的提交是你所在的提交的直接后继，因此 Git 会直接将指针向前移动。换句话说，当你试图合并两个分支时，如果顺着一个分支走下去能够到达另一个分支，那么 Git 在合并两者的时候，只会简单地将指针向前推进……这就叫做“快进（fast-forward）”。
>
> 在这种情况下，你的开发历史从一个更早的地方开始分叉开来（diverged）。因为，你所在分支的提交并不是要合并分支所在提交的直接祖先，Git 不得不做一些额外的工作。出现这种情况的时候，Git 会使用两个分支的末端所指的快照以及这两个分支的公共祖先，做一个简单的三方合并。
>
> 和之前将分支指针向前推进所不同的是，Git 将此次三方合并的结果做了一个新的快照并且自动创建一个新的提交指向它。这个被称作一次合并提交，它的特别之处在于它有不止一个父提交。

#### 批注

快进：`main` 没动过，直接「快进」到 `feature` 的位置，历史是一条直线。
三方合并：两边都前进过，Git 用「共同祖先 + 两边末端」合成一个新快照，生成带两个父提交的 merge commit。

### 5.4 冲突：同一处被两边改

#### 原文（Pro Git, 3.2 — Basic Merge Conflicts，节选）

> Occasionally, this process doesn't go smoothly.
> If you changed the same part of the same file differently in the two branches you're merging together, Git won't be able to merge them cleanly. [...]
>
> ```console
> $ git merge iss53
> Auto-merging index.html
> CONFLICT (content): Merge conflict in index.html
> Automatic merge failed; fix conflicts and then commit the result.
> ```
>
> Git hasn't automatically created a new merge commit.
> It has paused the process while you resolve the conflict.
>
> Anything that has merge conflicts and hasn't been resolved is listed as unmerged.
> Git adds standard conflict-resolution markers to the files that have conflicts, so you can open them manually and resolve those conflicts. [...]
>
> This means the version in `HEAD` (your `master` branch, because that was what you had checked out when you ran your merge command) is the top part of that block (everything above the `=======`), while the version in your `iss53` branch looks like everything in the bottom part.
> In order to resolve the conflict, you have to either choose one side or the other or merge the contents yourself. [...]
>
> After you've resolved each of these sections in each conflicted file, run `git add` on each file to mark it as resolved.
> Staging the file marks it as resolved in Git.
> If you're happy with that, and you verify that everything that had conflicts has been staged, you can type `git commit` to finalize the merge commit.

#### 译文（Pro Git 中文版，3.2 — 遇到冲突时的分支合并，节选）

> 有时候合并操作不会如此顺利。如果你在两个不同的分支中，对同一个文件的同一个部分进行了不同的修改，Git 就没法干净地合并它们。
>
> 此时 Git 做了合并，但是没有自动地创建一个新的合并提交。Git 会暂停下来，等待你去解决合并产生的冲突。
>
> 任何因包含合并冲突而有待解决的文件，都会以未合并状态标识出来。Git 会在有冲突的文件中加入标准的冲突解决标记，这样你可以打开这些包含冲突的文件然后手动解决冲突。
>
> 这表示 `HEAD` 所指示的版本（也就是你运行 merge 命令时检出的分支）在这个区段的上半部分（`=======` 的上半部分），而要合并进来的分支版本在 `=======` 的下半部分。为了解决冲突，你必须选择使用由 `=======` 分割的两部分中的一个，或者你也可以自行合并这些内容。
>
> 在你解决了所有文件里的冲突之后，对每个文件使用 `git add` 命令来将其标记为冲突已解决。一旦暂存这些原本有冲突的文件，Git 就会将它们标记为冲突已解决。如果对结果满意，并且确认所有冲突文件都已暂存，就可以输入 `git commit` 完成合并提交。

#### 实例：真实的同一行冲突

```console
$ git switch -c feature          # 从 main 建分支并切过去
$ printf '# Demo project\n\ncontact: robot@example.com\n' > README.md
$ git add README.md && git commit -qm "feat: change contact to robot"
$ git switch main
$ printf '# Demo project\n\ncontact: lab@example.com\n' > README.md
$ git add README.md && git commit -qm "fix: change contact to lab"
$ git merge feature
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
Automatic merge failed; fix conflicts and then commit the result.
$ git status -s
UU README.md
$ cat README.md
# Demo project

<<<<<<< HEAD
contact: lab@example.com
=======
contact: robot@example.com
>>>>>>> feature
```

解决：编辑 `README.md`，删掉 `<<<<<<<`、`=======`、`>>>>>>>` 三行，留下或合并你需要的正文，然后：

```console
$ printf '# Demo project\n\ncontact: robot@example.com\n' > README.md
$ git add README.md
$ git commit -m "merge: keep robot contact"
$ git log --oneline --graph -4
*   9c711ed merge: keep robot contact
|\
| * 1981b16 feat: change contact to robot
* | e47ae97 fix: change contact to lab
|/
* 1d5636d Revert "exp: switch retries to retry(3)"
```

#### 批注

- 冲突时 `git status` 会进入 `You have unmerged paths.`，`UU` 表示 both modified；`git add` 之后变成 `M`，`git commit` 完成合并。
- 想放弃这次合并：`git merge --abort` 回到合并前状态；已经 `add` 但没 `commit` 时也可以先 `git restore --staged .` 再改。
- 解决冲突不是「删掉标记」就完了：第 2 题要求你**说清两边为什么改、你最后为什么选这个结果**，这比标记本身重要。

---

## 6. 一页命令速查

| 目的 | 命令 | 备注 |
|---|---|---|
| 看当前状态 | `git status` / `git status -s` | 两列：暂存区 / 工作区 |
| 看未暂存改动 | `git diff` | 工作区 ↔ 暂存区 |
| 看已暂存改动 | `git diff --staged` | 暂存区 ↔ HEAD |
| 暂存某个文件 | `git add <file>` | 只暂存此刻内容 |
| 取消暂存 | `git restore --staged <file>` | 工作区不动 |
| 丢弃工作区修改 | `git restore <file>` | **危险**，未提交修改消失 |
| 提交 | `git commit -m "..."` | 记录暂存区快照 |
| 修补最后一次提交 | `git commit --amend` | 仅限本地、未推送 |
| 撤销某个提交（保留历史） | `git revert <commit>` | 生成反向提交 |
| 看历史 | `git log --oneline --graph --decorate` | `--all` 看所有分支 |
| 建分支并切换 | `git switch -c <name>` | 旧写法 `git checkout -b` |
| 切换分支 | `git switch <name>` | 旧写法 `git checkout` |
| 合并 | `git merge <branch>` | 在当前分支上执行 |
| 放弃合并 | `git merge --abort` | 回到合并前 |
| 忽略规则 | `.gitignore` + `git check-ignore -v <path>` | 只对未跟踪文件生效 |

---

## 7. 和 ENG-07 四道题的对应

| 题目 | 先读 | 关键点 |
|---|---|---|
| 第 1 题「改的 3 为什么没进提交」 | §3.2—§3.5 | `add` 记录的是当时内容；`git diff` 与 `git diff --staged` 方向不同；直接 commit 只提交暂存区 |
| 第 2 题 同一行冲突 | §5.1—§5.4 | 分支是指针；冲突标记 `<<<<<<<` / `=======` / `>>>>>>>`；`git add` 标记已解决；说明双方意图 |
| 第 3 题 三种撤销 | §4.2—§4.4 | `restore --staged` 只退暂存区；`restore` 丢工作区；`revert` 追加反向提交；先写「保留什么、改变什么」 |
| 第 4 题 两次可解释的提交 | §3.3—§3.6 + 本文 §6 | 一次提交一件完整修改；用 `diff` 检查；`.gitignore` 排除虚拟环境与大产物 |

---

## 8. 出处与版本

- Pro Git, 2nd Edition（Scott Chacon, Ben Straub），英文原文：<https://git-scm.com/book/en/v2>；简体中文版：<https://git-scm.com/book/zh/v2>。本文件引用的英文章节为 1.3、2.2、2.4、3.1、3.2；中文译文引自 Pro Git 中文版对应章节，个别小节（`git restore`）中文版尚未同步，已标注为逐句直译。
- `git revert` 手册：英文 <https://git-scm.com/docs/git-revert>；简体中文 <https://git-scm.com/docs/git-revert/zh_HANS-CN>。
- 原文与译文版权：Pro Git 采用 CC BY-NC-SA 3.0；本文件仅作个人学习摘录，保留出处与署名。
- 实例运行环境：Git 2.x（本机 `git version` 见仓库 README），演示仓库位于 `/tmp/eng07-demo` 与 `/tmp/eng07-demo2`，所有输出为实际运行结果，示例文件 `README.md`、`app.conf` 与 `logs/run.log` 均为临时构造，与 `学习记录/练习` 无关。
- 访问日期：2026-11-20。
