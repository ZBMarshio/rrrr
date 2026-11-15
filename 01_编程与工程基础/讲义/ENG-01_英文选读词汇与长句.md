# ENG-01 英文选读：词汇与长句对照

[ENG-01 讲义](ENG-01_Python模块类与异常.md) · [第一章学习指南](../学习指南.md)

这份材料是给“读官方英文教程、但英语不够稳”的时候用的**随身字典**：只覆盖 ENG-01 要求读的那几段，按原文顺序列出可能卡住的单词和长句。原文依据 Python 3.12 官方教程（2026-11-07 抓取），句子是原文节选，译文按“读代码的人需要理解的意思”来译，不追求文学性。

## 怎么用（很重要）

1. **先硬读英文**，一段一段来，不要一上来就对着中文读。读不懂时再回来查，查完继续读原文。
2. 词表按出现顺序排，看到哪个词卡住就查哪个；不必背，混个眼熟即可。
3. 长句部分给了“拆解”，是用来看懂句子结构的，不是语法课。**先自己断句，再看拆解**。
4. 每节末尾有“读完自检”，就是讲义里要求你能回答的问题；答不上来再回读对应段落。
5. 标记：**★ 必读**（对应讲义要求）；☆ 按需（讲义说“按需/只按需”，时间紧可跳）。

### 先认识这 12 个词，能省一半查词时间

| 英文 | 中文 | 说明 |
|---|---|---|
| statement | 语句 | 一行代码，如 `x = 1` |
| expression | 表达式 | 能算出值的一段代码，如 `a + b` |
| argument / parameter | 实参 / 形参 | 调用时传的是实参，定义里写的是形参 |
| attribute | 属性 | 用 `obj.name` 取到的东西 |
| instance | 实例 | 由类创建出来的具体对象 |
| namespace | 命名空间 | 名字到对象的映射表 |
| scope | 作用域 | 一个名字在哪儿可见 |
| exception | 异常 | 运行期出错时抛出的对象 |
| raise | 抛出 | 主动抛出异常（其他语言常叫 throw） |
| handle | 处理 | 捕获并应对异常 |
| traceback | 栈回溯 | 报错时那一大段“调用链” |
| mutable | 可变的 | 内容能原地修改，如 list、dict |

### 关于章节编号

讲义写的是“4.7 定义函数；4.8 中默认参数”。在 3.12 的页面上实际是：

- **4.8 Defining Functions**（定义函数）
- **4.9.1 Default Argument Values**（默认参数值）

编号会随文档版本漂移，**按标题找**就不会错。下面一律用标题。

---

## 0. 本次要读的四段

| 章节 | 英文标题 | 中文 | 篇幅 | 读完要能回答 |
|---|---|---|---|---|
| 4.8 + 4.9.1 | Defining Functions / Default Argument Values | 定义函数、默认参数 | 约 3 屏 | 形参、实参、return 分别在哪？默认列表为什么危险？ |
| 6.1—6.1.2 | More on Modules / Executing modules as scripts / The Module Search Path | 模块、作为脚本执行、模块搜索路径 | 约 3 屏 | import 会执行哪些顶层语句？主入口如何保护？ |
| 9.3.2—9.3.5 | Class Objects / Instance Objects / Method Objects / Class and Instance Variables | 类对象、实例对象、方法对象、类变量与实例变量 | 约 4 屏 | 对象属性、实例方法、类属性有什么区别？ |
| 9.5 ☆ | Inheritance | 继承 | 约 1 屏 | 只按需；方法重写和 `super` 的直觉 |
| 8.2—8.5 + 8.8 | Exceptions / Handling / Raising / Chaining / Predefined Clean-up Actions | 异常、处理、抛出、链接、with 清理 | 约 5 屏 | 如何读最后一条错误、抛异常和用 with 释放文件？ |

阅读时建议的顺序就是上表顺序：函数 → 模块 → 类 → 异常。9.5 放最后，读不动可以只读第一段和 `isinstance` 那段。

---

## 1. 4.8 Defining Functions（定义函数）★

这一节在讲：函数怎么定义、`def` 后面跟什么、docstring 是什么、函数体里的名字去哪儿找（符号表）、参数到底是“按值”还是“按引用”、以及没有 return 时返回什么。

### 1.1 生词

| 英文 | 词性/搭配 | 中文 |
|---|---|---|
| arbitrary | adj. | 任意的，随意的（`an arbitrary boundary` 任意边界） |
| boundary | n. | 边界，界限 |
| parenthesized | adj. | 加了括号的（`parenthesized list` 括号里的列表） |
| formal parameter | n. | 形参（函数定义里写的参数） |
| indented | adj. | 缩进的（`must be indented` 必须缩进） |
| string literal | n. | 字符串字面量（直接写出来的 `"..."`） |
| optionally | adv. | 可选地，可有可无地 |
| docstring | n. | 文档字符串（函数体第一句字符串） |
| interactively | adv. | 交互式地 |
| browse | v. | 浏览 |
| make a habit of it | 短语 | 养成习惯 |
| execution | n. | 执行 |
| symbol table | n. | 符号表（名字 → 对象 的表） |
| local variable | n. | 局部变量 |
| precisely | adv. | 确切地说 |
| assignment | n. | 赋值（`variable assignment` 变量赋值） |
| reference | n. | 引用（`variable reference` 变量引用） |
| enclosing | adj. | 外层的，包围的（`enclosing functions` 外层函数） |
| global | adj. | 全局的 |
| built-in | adj. | 内置的 |
| nonlocal | 关键字 | 非局部（声明“我要改外层函数的变量”） |
| actual parameter / argument | n. | 实参（调用时真正传进去的值） |
| call by value | 短语 | 按值调用 |
| object reference | 短语 | 对象引用（指向对象的那张“标签”） |
| recursively | adv. | 递归地 |
| associate A with B | 短语 | 把 A 和 B 关联起来 |
| interpreter | n. | 解释器 |
| user-defined | adj. | 用户定义的 |
| procedure | n. | 过程（没有返回值的子程序，其他语言的说法） |
| object | v. | 反对（`you might object that...` 你可能会反驳说） |
| albeit | conj. | 尽管，虽然（后接名词或形容词，不接完整句） |
| boring | adj. | 无聊的，乏味的 |
| suppress | v. | 抑制，不显示 |
| demonstrate | v. | 演示，说明 |
| append | v. | 追加（加到末尾） |
| efficient | adj. | 高效的 |
| equivalent | adj. | 等价的（`is equivalent to` 等价于） |
| ambiguity | n. | 歧义 |
| belong to | 短语 | 属于 |
| falling off the end of a function | 短语 | 从函数末尾“掉出去”（执行到结尾、没遇到 return） |

### 1.2 长句

**1.** "The execution of a function introduces a new symbol table used for the local variables of the function."

> 译文：执行一个函数会引入一张新的符号表，供该函数的局部变量使用。
> 拆解：主干是 *The execution introduces a table*；`used for...` 是过去分词，修饰 table。

**2.** "More precisely, all variable assignments in a function store the value in the local symbol table; whereas variable references first look in the local symbol table, then in the local symbol tables of enclosing functions, then in the global symbol table, and finally in the table of built-in names."

> 译文：更确切地说，函数里所有的变量赋值都把值存进局部符号表；而变量引用则先查局部符号表，再查外层函数的局部符号表，然后查全局符号表，最后查内置名字表。
> 拆解：分号前讲“写”（赋值存哪儿），分号后讲“读”（引用按什么顺序找）；`whereas` 表对比；四个 `then` 就是查找顺序，记住“由内向外”。

**3.** "Thus, global variables and variables of enclosing functions cannot be directly assigned a value within a function (unless ... named in a global statement ...), although they may be referenced."

> 译文：因此，全局变量和外层函数的变量不能在函数内部被直接赋值（除非用 `global` 或 `nonlocal` 语句声明），不过它们可以被引用。
> 拆解：括号里两个 `unless` 是例外；`although` 转折——**能读，不能直接写**。

**4.** "The actual parameters (arguments) to a function call are introduced in the local symbol table of the called function when it is called; thus, arguments are passed using call by value (where the value is always an object reference, not the value of the object)."

> 译文：函数调用时的实参，会在被调用函数被调用时进入它的局部符号表；因此参数是按值传递的（这里的“值”始终是对象的引用，而不是对象本身的值）。
> 拆解：`actual parameters` 就是实参；括号里解释“按值”到底按的是什么——**传的是引用**，所以函数里改列表，外面看得见。

**5.** "Coming from other languages, you might object that fib is not a function but a procedure since it doesn't return a value. In fact, even functions without a return statement do return a value, albeit a rather boring one."

> 译文：如果你来自其他语言，你可能会反驳说 fib 不是函数而是过程，因为它不返回值。事实上，即使没有 return 语句的函数也确实会返回一个值，尽管这个值相当无聊。
> 拆解：`Coming from...` 是分词状语，可读成“由于你来自……”；`not... but...` 不是……而是……；`albeit` = although，后面只跟名词短语（a rather boring one）。

**6.** "Writing the value None is normally suppressed by the interpreter if it would be the only value written."

> 译文：如果 None 是唯一会被写出的值，解释器通常会把它抑制掉、不显示。
> 拆解：被动句；`it` 指 None；`would be` 表示“如果出现那种情况”。

### 1.3 读的时候注意

- docstring 只是函数体的第一句字符串，**可选**；不会因为它而改变函数行为。
- 没有 `return`，或者 `return` 后面什么都没写，返回值都是 `None`；`print` 和 `return` 是两件事。
- “按值传递”这句最容易被误读：Python 传的是**对象引用**，所以可变对象在函数里被修改，调用方看得见；但给参数重新赋值，不会影响调用方。

**读完自检：** 形参、实参、return 分别在哪里？函数里能直接改全局变量吗？`fib(0)` 和 `print(fib(0))` 输出有什么区别，为什么？

---

## 2. 4.9.1 Default Argument Values（默认参数值）★

这一节只有两个重点：默认值**在定义时求值一次**；默认值是可变对象时，会被所有调用共享。后半段给出的 `L=None` 写法就是标准修法。

### 2.1 生词

| 英文 | 词性/搭配 | 中文 |
|---|---|---|
| a variable number of | 短语 | 可变数量的 |
| specify | v. | 指定 |
| default value | 短语 | 默认值 |
| retries | n. | 重试次数 |
| reminder | n. | 提醒（的话） |
| prompt | n. | 提示语（`input()` 里显示的提示文字） |
| mandatory | adj. | 必填的，必需的 |
| optional | adj. | 可选的 |
| overwrite | v. | 覆盖（写） |
| sequence | n. | 序列（list、tuple、str 这类） |
| evaluate | v. | 求值，算出结果 |
| defining scope | 短语 | 定义时所在的作用域 |
| mutable | adj. | 可变的 |
| accumulate | v. | 累积 |
| subsequent | adj. | 随后的（`subsequent calls` 后续调用） |
| share | v. | 共享 |
| idiom | n. | 惯用法，固定写法 |
| make a difference | 短语 | 有影响，会不一样 |
| warning | n. | 警告 |
| test whether or not | 短语 | 检验是否…… |

### 2.2 长句

**1.** "This creates a function that can be called with fewer arguments than it is defined to allow."

> 译文：这样创建出来的函数，可以用比定义时允许的个数更少的参数来调用。
> 拆解：`fewer ... than it is defined to allow` 是比较结构，allow 后面省略了 arguments。

**2.** "The default values are evaluated at the point of function definition in the defining scope, so that ... will print 5."

> 译文：默认值是在函数定义的那一刻、在定义所在的作用域里求值的，所以……会打印 5。
> 拆解：两个状语叠在一起——时间（定义时）、地点（定义作用域）；`so that` 引出结果。例子先 `i = 5` 定义 `f(arg=i)`，再 `i = 6` 也没用，因为默认值早定死了。

**3.** "The default value is evaluated only once. This makes a difference when the default is a mutable object such as a list, dictionary, or instances of most classes."

> 译文：默认值只求值一次。当默认值是可变的（mutable）对象——比如列表、字典，或大多数类的实例——时，这就会带来差别。
> 拆解：`make a difference` = 有影响；`such as` 列举；`instances of most classes` = 大多数类的实例。

**4.** "For example, the following function accumulates the arguments passed to it on subsequent calls"

> 译文：例如，下面这个函数会把后续每次调用时传给它的参数累积起来。
> 拆解：`passed to it` 是过去分词修饰 arguments；`on subsequent calls` = 在后续调用时。

**5.** "If you don't want the default to be shared between subsequent calls, you can write the function like this instead"

> 译文：如果你不希望这个默认值在后续多次调用之间被共享，可以改成这样写。
> 拆解：`want sth to be done` 结构；`instead` 表示“转而、改成”。

### 2.3 读的时候注意

- `def f(a, L=[])` 里的 `[]` **只创建一次**，之后每次调用都用同一个列表；所以会出现 `[1]`、`[1,2]`、`[1,2,3]`。
- 标准修法是 `L=None`，进函数后 `if L is None: L = []`。注意用 `is None`，不要用 `== None`。
- 默认值也可以是 `i` 这类变量，但取的是**定义那一刻**的值，不是调用时的值。

**读完自检：** 为什么两次 `collect(0.1)`、`collect(0.2)` 会出现“上一轮的数据”？不传 `buffer` 时怎么让每次调用各用新列表？显式传同一个列表时还能不能继续累积？

---

## 3. 6.1 More on Modules（模块）/ 6.1.1 / 6.1.2 ★

三个小节分别回答：import 时到底执行了什么、`__name__ == "__main__"` 是干嘛的、import 一个名字时解释器去哪儿找文件。

### 3.1 生词

| 英文 | 词性/搭配 | 中文 |
|---|---|---|
| executable | adj. | 可执行的 |
| initialize | v. | 初始化 |
| encounter | v. | 遇到 |
| private | adj. | 私有的 |
| namespace | n. | 命名空间 |
| accidental | adj. | 意外的 |
| clash | n. | 冲突（`clashes with` 与……冲突） |
| on the other hand | 短语 | 另一方面 |
| notation | n. | 记法，写法 |
| customary | adj. | 惯常的，通常的 |
| required | adj. | 必需的 |
| for that matter | 短语 | 就此而言，……也一样 |
| top level | 短语 | 顶层（不在任何函数/类里面） |
| variant | n. | 变体，另一种写法 |
| underscore | n. | 下划线 `_` |
| facility | n. | 功能，机制 |
| hide | v. | 遮蔽，隐藏 |
| frown upon | 短语 | 不赞成，不提倡（`is frowned upon`） |
| poorly readable | 短语 | 可读性差的 |
| interactive session | 短语 | 交互式会话（REPL） |
| be bound to | 短语 | 绑定到 |
| effectively | adv. | 实际上，效果上 |
| utilise | v. | 使用（英式拼写，= utilize） |
| efficiency | n. | 效率 |
| interpreter session | 短语 | 解释器会话（一次 python 进程） |
| restart | v. | 重启 |
| reload | v. | 重新加载 |
| parse | v. | 解析（`parses the command line` 解析命令行） |
| usable | adj. | 可用的 |
| importable | adj. | 可被导入的 |
| convenient | adj. | 方便的 |
| test suite | 短语 | 测试套件 |
| search path | 短语 | 搜索路径 |
| built-in module | 短语 | 内置模块 |
| installation-dependent | adj. | 取决于安装位置的 |
| by convention | 短语 | 按惯例 |
| symlink | n. | 符号链接（软链接） |
| follow the symlink | 短语 | 跟随符号链接 |
| ahead of | 短语 | 在……之前 |
| standard library | 短语 | 标准库 |
| replacement | n. | 替换（物） |
| intended | adj. | 有意的，故意的 |
| load | v. | 加载 |
| directory | n. | 目录，文件夹 |

### 3.2 长句

**1.** "A module can contain executable statements as well as function definitions. These statements are intended to initialize the module."

> 译文：一个模块既可以包含函数定义，也可以包含可执行语句。这些语句的用途是初始化该模块。
> 拆解：`as well as` = 以及；`be intended to` = 旨在、用来。

**2.** "They are executed only the first time the module name is encountered in an import statement."

> 译文：只有在 import 语句中第一次遇到该模块名时，它们才会被执行。
> 拆解：`only the first time` 引导时间状语；`encountered` 是被动。

**3.** "Each module has its own private namespace, which is used as the global namespace by all functions defined in the module."

> 译文：每个模块都有自己的私有命名空间，模块里定义的所有函数都把它当作全局命名空间来用。
> 拆解：`which` 指 namespace；`be used as` = 被当作……使用。

**4.** "Thus, the author of a module can use global variables in the module without worrying about accidental clashes with a user's global variables."

> 译文：因此，模块作者可以在模块里使用全局变量，而不必担心与使用者的全局变量意外重名冲突。
> 拆解：`without worrying about` = 不必担心；`clash with` = 与……冲突。

**5.** "In most cases Python programmers do not use this facility since it introduces an unknown set of names into the interpreter, possibly hiding some things you have already defined."

> 译文：大多数情况下，Python 程序员不会用这个功能，因为它会把一组未知的名字带进解释器，还可能把你已经定义过的东西遮蔽掉。
> 拆解：`facility` 这里指“功能”；`since` = because；`possibly hiding` 分词表结果。

**6.** "Note that in general the practice of importing * from a module or package is frowned upon, since it often causes poorly readable code."

> 译文：注意，一般来说，从模块或包里 `import *` 这种做法是不被提倡的，因为它经常导致可读性很差的代码。
> 拆解：`the practice of ... is frowned upon` = ……的做法不受欢迎；`poorly readable` = 可读性差。

**7.** "If the module name is followed by as, then the name following as is bound directly to the imported module."

> 译文：如果模块名后面跟了 `as`，那么 `as` 后面的名字就直接绑定到被导入的模块上。
> 拆解：`be followed by` = 后面跟着；`be bound to` = 绑定到。

**8.** "For efficiency reasons, each module is only imported once per interpreter session."

> 译文：出于效率考虑，每个模块在每个解释器会话中只会被导入一次。
> 拆解：`per` = 每。所以改了模块要重启解释器，或者 `importlib.reload()`。

**9.** "the code in the module will be executed, just as if you imported it, but with the `__name__` set to `'__main__'`."

> 译文：模块里的代码会被执行，就像你 import 了它一样，只不过 `__name__` 被设成了 `"__main__"`。
> 拆解：`just as if` = 就好像；`with + 名词 + 过去分词` 表伴随状态。

**10.** "you can make the file usable as a script as well as an importable module"

> 译文：你可以让这个文件既能当脚本用，又能作为模块被导入。
> 拆解：`make + 宾语 + 形容词`（usable）；`as well as` 连接两个身份。

**11.** "When a module named spam is imported, the interpreter first searches for a built-in module with that name."

> 译文：当导入一个名为 spam 的模块时，解释器会先找同名的内置模块。
> 拆解：`named spam` 过去分词修饰 module。

**12.** "The installation-dependent default (by convention including a site-packages directory, handled by the site module)."

> 译文：取决于安装位置的默认值（按惯例会包含一个 site-packages 目录，由 site 模块负责处理）。
> 拆解：这是列表里的一项，不是完整句子；两个括号都是补充说明。

**13.** "On file systems which support symlinks, the directory containing the input script is calculated after the symlink is followed."

> 译文：在支持符号链接的文件系统上，包含输入脚本的目录是在跟随符号链接之后才计算出来的。
> 拆解：`after the symlink is followed` = 跟随符号链接之后；`containing` 分词修饰 directory。

**14.** "This means that scripts in that directory will be loaded instead of modules of the same name in the library directory. This is an error unless the replacement is intended."

> 译文：这意味着，那个目录里的脚本会被加载，而不是库目录里的同名模块。除非你确实想替换，否则这是一个错误。
> 拆解：`instead of` = 而不是；`unless` = 除非；`intended` = 有意的。

### 3.3 读的时候注意

- import 会执行模块**顶层的**语句（函数体、类体里的不算），所以别把读文件、画图、启动循环放在顶层。
- 模块被缓存：同一进程里第二次 import 不会重新执行；改代码后要重启解释器或 `reload`。
- `__name__ == "__main__"` 这行保护的是“只有直接运行才执行”，被 import 时不执行。
- 脚本所在目录会排在 `sys.path` 最前面，所以自己的 `json.py`、`numpy.py` 会盖掉标准库/第三方库，这是讲义反复提醒的坑。

**读完自检：** import 会执行哪些顶层语句？主入口如何保护？为什么把画图代码放在顶层，会让 `import trajectory` 弹出窗口？

---

## 4. 9.3.2—9.3.5 类：类对象、实例对象、方法对象、类/实例变量 ★

这一节的长句最多，但核心就三件事：属性查找怎么走、`self` 从哪来、类变量和实例变量在可变对象上有什么区别。

### 4.1 生词

| 英文 | 词性/搭配 | 中文 |
|---|---|---|
| attribute | n. | 属性 |
| attribute reference | 短语 | 属性引用（`obj.name`） |
| instantiation | n. | 实例化 |
| instantiate | v. | 实例化 |
| valid | adj. | 有效的 |
| respectively | adv. | 分别地 |
| parameterless | adj. | 无参数的 |
| pretend | v. | 假装，姑且认为 |
| customize | v. | 定制 |
| initial state | 短语 | 初始状态 |
| invoke | v. | 调用，触发 |
| flexibility | n. | 灵活性 |
| operator | n. | 运算符 |
| pass on | 短语 | 传递给 |
| instance variable | 短语 | 实例变量 |
| data attribute | 短语 | 数据属性 |
| data member | 短语 | 数据成员（C++ 说法） |
| declare | v. | 声明 |
| spring into existence | 短语 | 凭空出现，突然产生 |
| without leaving a trace | 短语 | 不留痕迹 |
| counter | n. | 计数器 |
| corresponding | adj. | 对应的 |
| bound | adj. | 已绑定的（`bound method` 绑定方法） |
| store away | 短语 | 存起来 |
| exactly | adv. | 确切地 |
| insert | v. | 插入 |
| non-data attribute | 短语 | 非数据属性（方法这类） |
| denote | v. | 表示，指 |
| pack into | 短语 | 打包进 |
| construct | v. | 构造 |
| unique to | 短语 | 为……独有 |
| shared by | 短语 | 被……共享 |
| surprising | adj. | 令人意外的 |
| involve | v. | 涉及 |
| mistaken | adj. | 错误的 |
| unexpectedly | adv. | 出乎意料地 |
| design | n. | 设计 |

### 4.2 长句

**1.** "Class objects support two kinds of operations: attribute references and instantiation."

> 译文：类对象支持两类操作：属性引用和实例化。
> 拆解：冒号后就是这两类操作的名称，读懂冒号的作用即可。

**2.** "Valid attribute names are all the names that were in the class's namespace when the class object was created."

> 译文：有效的属性名，就是创建类对象时存在于该类命名空间里的所有名字。
> 拆解：`that` 从句修饰 names；注意是“创建时”的快照，后来再往类上加名字，也能成为属性，但这句强调的是定义时那些。

**3.** "Class instantiation uses function notation. Just pretend that the class object is a parameterless function that returns a new instance of the class."

> 译文：类的实例化使用函数调用式的写法。你姑且把类对象当成一个无参数的函数，它返回该类的一个新实例。
> 拆解：`function notation` = 函数写法（类名加括号）；`pretend that` = 姑且认为。

**4.** "Many classes like to create objects with instances customized to a specific initial state."

> 译文：许多类希望创建对象时，就把实例定制成某个特定的初始状态。
> 拆解：`customized to...` 过去分词修饰 instances；`with` 表伴随。

**5.** "Of course, the `__init__()` method may have arguments for greater flexibility. In that case, arguments given to the class instantiation operator are passed on to `__init__()`."

> 译文：当然，`__init__()` 方法可以带参数，以获得更大的灵活性。这种情况下，传给类实例化运算符的参数会被转交给 `__init__()`。
> 拆解：`in that case` = 那种情况下；`given to...` 分词修饰 arguments；`be passed on to` = 被转交给。

**6.** "Data attributes need not be declared; like local variables, they spring into existence when they are first assigned to."

> 译文：数据属性不需要声明；和局部变量一样，第一次给它们赋值时，它们就凭空出现了。
> 拆解：`need not` = 不必；`spring into existence` = 突然出现；`assigned to` 后面省略了 them。

**7.** "By definition, all attributes of a class that are function objects define corresponding methods of its instances."

> 译文：按照定义，类中凡是函数对象的属性，都为它的实例定义了对应的方法。
> 拆解：`that are function objects` 修饰 attributes；`its` 指 class。

**8.** "the special thing about methods is that the instance object is passed as the first argument of the function."

> 译文：方法特别的地方在于，实例对象会作为函数的第一个参数被传进去。
> 拆解：主语是 `the special thing about methods`，表语是 that 从句。

**9.** "In general, calling a method with a list of n arguments is equivalent to calling the corresponding function with an argument list that is created by inserting the method's instance object before the first argument."

> 译文：一般来说，用 n 个参数调用一个方法，等价于调用对应的函数，并在参数列表的最前面插入该方法的实例对象。
> 拆解：`be equivalent to` = 等价于；`that` 从句解释参数列表怎么造出来；`inserting ... before` = 插到……之前。

**10.** "When a non-data attribute of an instance is referenced, the instance's class is searched."

> 译文：当引用实例的一个非数据属性时，会去搜索该实例所属的类。
> 拆解：被动句；`non-data attribute` 指方法这类，先查实例自身，再查类。

**11.** "references to both the instance object and the function object are packed into a method object."

> 译文：对实例对象和函数对象两者的引用，会被打包进一个方法对象里。
> 拆解：`both ... and ...`；`packed into` = 打包进。

**12.** "instance variables are for data unique to each instance and class variables are for attributes and methods shared by all instances of the class"

> 译文：实例变量用于保存每个实例各自独有的数据；类变量用于保存该类所有实例共享的属性和方法。
> 拆解：`be for` = 用于；`unique to` / `shared by` 两个分词短语都作后置定语。

**13.** "shared data can have possibly surprising effects ... with involving mutable objects such as lists and dictionaries"

> 译文：共享数据在涉及列表、字典这类可变对象时，可能产生令人意外的效果。
> 拆解：原句这里有个不太顺的 `with involving`，按 `when involving` 理解即可——重点是“共享 + 可变”会出意外。

**14.** "the tricks list ... should not be used as a class variable because just a single list would be shared by all Dog instances"

> 译文：tricks 这个列表不应被当作类变量使用，因为所有 Dog 实例会共享同一个列表。
> 拆解：`be used as` = 被用作；`a single list` 强调“就一个”。

### 4.3 读的时候注意

- `x.f` 和 `MyClass.f` 不是一回事：前者是**方法对象**（已经绑定了 x），后者是函数对象。
- 调用 `x.f()` 时，Python 自动把 x 作为第一个参数插进去，所以定义里要写 `self`；`x.f()` 等价于 `MyClass.f(x)`。
- 类体里写 `tricks = []` 是**一个**列表，所有实例共用；写在 `__init__` 里的 `self.tricks = []` 才是每个实例各一个。
- `__init__` 的名字前后各两个下划线，别写成 `_init_`。

**读完自检：** 对象属性、实例方法、类属性有什么区别？为什么 `d.add_trick()` 之后 `e.tricks` 也变了？`self` 到底指谁？

---

## 5. 9.5 Inheritance（继承）☆ 按需

讲义说“9.5 继承只按需”，时间紧可以只读第一段和最后 `isinstance`/`issubclass` 那段。

### 5.1 生词

| 英文 | 词性/搭配 | 中文 |
|---|---|---|
| inheritance | n. | 继承 |
| derived class | 短语 | 派生类，子类 |
| base class | 短语 | 基类，父类 |
| worthy of | 短语 | 配得上，值得 |
| accessible | adj. | 可访问的 |
| scope | n. | 作用域 |
| proceed | v. | 进行，继续 |
| remember | v. | 记住，保留（这里指保留基类信息） |
| resolve | v. | 解析，确定 |
| descend | v. | 向下（沿继承链往下找） |
| override | v. | 重写，覆盖 |
| privilege | n. | 特权 |
| end up doing | 短语 | 最终变成，结果却 |
| virtual | adj. | 虚函数（C++ 术语） |
| extend | v. | 扩展 |
| replace | v. | 替换 |
| occasionally | adv. | 偶尔 |
| client | n. | 调用方，使用者 |
| subclass | n. | 子类 |

### 5.2 长句

**1.** "The name BaseClassName must be defined in a namespace accessible from the scope containing the derived class definition."

> 译文：BaseClassName 这个名字必须定义在一个命名空间里，而这个命名空间要能从包含派生类定义的作用域访问到。
> 拆解：`accessible from...` 后置定语修饰 namespace；`containing` 修饰 scope。

**2.** "Because methods have no special privileges when calling other methods of the same object, a method of a base class that calls another method defined in the same base class may end up calling a method of a derived class that overrides it."

> 译文：因为方法在调用同一对象的其他方法时并没有特殊权限，所以基类里某个方法如果调用了同基类中定义的另一个方法，最终可能调用到派生类里重写它的那个方法。
> 拆解：两个 `that` 从句分别修饰 method；`end up doing` = 最终变成；这就是“所有方法实际上都是虚函数”的意思。

**3.** "An overriding method in a derived class may in fact want to extend rather than simply replace the base class method of the same name."

> 译文：派生类里重写的方法，实际上可能想扩展同名基类方法，而不是简单地替换它。
> 拆解：`rather than` = 而不是，连接两个动词；`extend` 与 `replace` 是这一句的对比核心。

### 5.3 读的时候注意

- Python 没有 `super` 的强制要求，但子类 `__init__` 里通常要 `super().__init__(...)`；`super` 不会替你补参数。
- 方法查找沿继承链往下走（先子类，再基类）。
- 讲义说“只按需”，是因为 W01 的练习用不到多继承；读懂“重写”和 `isinstance` 就够了。

---

## 6. 8.2—8.5 Exceptions（异常）+ 8.8 with 清理 ★

这是四段里最长的，但结构清楚：8.2 认识异常，8.3 捕获，8.4 抛出，8.5 异常链，8.8 `with` 自动清理。

### 6.1 生词

| 英文 | 词性/搭配 | 中文 |
|---|---|---|
| syntactically | adv. | 语法上 |
| detect | v. | 检测到 |
| unconditionally | adv. | 无条件地 |
| fatal | adj. | 致命的 |
| handle | v. | 处理 |
| result in | 短语 | 导致，结果是 |
| traceback | n. | 栈回溯（报错时那一大段） |
| concatenate | v. | 拼接，串联 |
| indicate | v. | 表明，指出 |
| identifier | n. | 标识符（名字） |
| reserved keyword | 短语 | 保留关键字 |
| preceding | adj. | 前面的 |
| context | n. | 上下文，现场 |
| stack | n. | 栈 |
| source line | 短语 | 源代码行 |
| standard input | 短语 | 标准输入（键盘） |
| interrupt | v. | 中断 |
| signal | v. | 表示，发出信号 |
| clause | n. | 子句（try/except/else 各算一个） |
| skip | v. | 跳过 |
| match | v. | 匹配 |
| outer | adj. | 外层的 |
| handler | n. | 处理器 |
| unhandled | adj. | 未处理的 |
| parenthesized tuple | 短语 | 括号里的元组 |
| the other way around | 短语 | 反过来 |
| reverse | v. | 颠倒（顺序） |
| trigger | v. | 触发 |
| associated value | 短语 | 关联的值 |
| presence | n. | 有无，存在 |
| bind to | 短语 | 绑定到 |
| typically | adv. | 通常 |
| for convenience | 短语 | 为方便起见 |
| explicitly | adv. | 显式地 |
| wildcard | n. | 通配符 |
| specific | adj. | 具体的，明确的 |
| intend | v. | 打算，想要 |
| propagate | v. | 向上传播 |
| log | v. | 记录日志 |
| re-raise | v. | 重新抛出 |
| avoid | v. | 避免 |
| accidentally | adv. | 意外地 |
| protect | v. | 保护 |
| indirectly | adv. | 间接地 |
| run-time error | 短语 | 运行时错误 |
| force | v. | 强行，强制 |
| sole | adj. | 唯一的 |
| derive from | 短语 | 派生自 |
| implicitly | adv. | 隐式地 |
| constructor | n. | 构造函数 |
| shorthand | n. | 简写 |
| determine | v. | 判断，确定 |
| chaining | n. | 链接 |
| attach | v. | 附加，挂上 |
| consequence | n. | 结果，后果 |
| direct consequence | 短语 | 直接结果 |
| transform | v. | 转换 |
| disable | v. | 关闭，禁用 |
| automatic | adj. | 自动的 |
| mechanics | n. | 机制 |
| clean-up action | 短语 | 清理动作 |
| undertake | v. | 执行，进行 |
| regardless of whether | 短语 | 无论是否 |
| succeed | v. | 成功 |
| fail | v. | 失败 |
| indeterminate | adj. | 不确定的，不定的 |
| issue | n. | 问题 |
| ensure | v. | 确保 |
| promptly | adv. | 及时地 |

### 6.2 长句

**1.** "Errors detected during execution are called exceptions and are not unconditionally fatal"

> 译文：在执行期间检测到的错误称为异常，而异常并非无条件致命。
> 拆解：两个并列谓语 `are called` 和 `are not`；`detected during execution` 修饰 errors。

**2.** "Most exceptions are not handled by programs, however, and result in error messages as shown here"

> 译文：不过，大多数异常并没有被程序处理，结果就是像下面这样打印出错误信息。
> 拆解：`however` 插在句中表转折；`result in` = 导致。

**3.** "Standard exception names are built-in identifiers (not reserved keywords)."

> 译文：标准异常名是内置标识符（不是保留关键字）。
> 拆解：这句是说 `ValueError` 这类名字只是普通的内置名字，你可以用，但不能指望它像 `if` 那样是语法关键字。

**4.** "The preceding part of the error message shows the context where the exception occurred, in the form of a stack traceback."

> 译文：错误信息前面的部分，以栈回溯（stack traceback）的形式显示异常发生时的现场。
> 拆解：`where` 定语从句修饰 context；`in the form of` = 以……形式。

**5.** "which asks the user for input until a valid integer has been entered, but allows the user to interrupt the program"

> 译文：它反复要求用户输入，直到输入一个有效整数为止，但允许用户中断程序。
> 拆解：`ask sb for sth` = 向某人要某物；`until` 从句用现在完成时表“直到……为止”。

**6.** "note that a user-generated interruption is signalled by raising the KeyboardInterrupt exception"

> 译文：注意，用户产生的打断是通过抛出 `KeyboardInterrupt` 异常来表示的。
> 拆解：`be signalled by` = 由……表示；`raising` = 抛出。

**7.** "If an exception occurs which does not match the exception named in the except clause, it is passed on to outer try statements; if no handler is found, it is an unhandled exception and execution stops with an error message."

> 译文：如果发生的异常与 except 子句里指定的异常不匹配，它会被传给外层的 try 语句；如果找不到处理器，它就是未处理异常，程序会带着一条错误信息停止。
> 拆解：`which` 从句修饰 exception，被 `If` 从句隔开了（后置定语）；`be passed on to` = 被传递到。

**8.** "Handlers only handle exceptions that occur in the corresponding try clause, not in other handlers of the same try statement."

> 译文：处理器只处理发生在对应 try 子句里的异常，不处理同一个 try 语句中其他处理器里发生的异常。
> 拆解：`not in other handlers` 与前半句共用 handle。

**9.** "A class in an except clause matches exceptions which are instances of the class itself or one of its derived classes (but not the other way around — an except clause listing a derived class does not match instances of its base classes)."

> 译文：except 子句里的类，匹配的是该类本身或其某个派生类的实例所对应的异常（反过来不成立——列出派生类的 except 子句不会匹配其基类的实例）。
> 拆解：`the other way around` = 反过来；破折号后面就是“反过来”的解释。

**10.** "The variable is bound to the exception instance which typically has an args attribute that stores the arguments."

> 译文：这个变量会绑定到异常实例上，该实例通常有一个 `args` 属性，用来保存参数。
> 拆解：两个定语从句套着：`which` 修饰 instance，`that` 修饰 args。

**11.** "Exceptions which are not subclasses of Exception are not typically handled, because they are used to indicate that the program should terminate."

> 译文：不是 `Exception` 子类的异常通常不会被处理，因为它们用来表示程序应当终止。
> 拆解：`terminate` = 终止；`SystemExit`、`KeyboardInterrupt` 就属于这类。

**12.** "Exception can be used as a wildcard that catches (almost) everything. However, it is good practice to be as specific as possible with the types of exceptions that we intend to handle, and to allow any unexpected exceptions to propagate on."

> 译文：`Exception` 可以当作通配符，捕获（几乎）所有异常。不过，好的做法是尽量具体地限定我们要处理的异常类型，并让意料之外的异常继续向上传播。
> 拆解：`be as specific as possible` = 尽可能具体；`allow ... to propagate on` = 让……继续传播。

**13.** "The use of the else clause is better than adding additional code to the try clause because it avoids accidentally catching an exception that wasn't raised by the code being protected by the try … except statement."

> 译文：使用 else 子句，比把额外的代码加进 try 子句更好，因为这样可以避免意外捕获到并非由 try … except 所保护的代码抛出的异常。
> 拆解：`being protected` 现在分词被动，修饰 code；`wasn't raised by` 定语从句修饰 exception。

**14.** "Exception handlers do not handle only exceptions that occur immediately in the try clause, but also those that occur inside functions that are called (even indirectly) in the try clause."

> 译文：异常处理器不仅处理直接在 try 子句里发生的异常，也处理在 try 子句中被调用的函数（哪怕是间接调用）内部发生的异常。
> 拆解：`not only ... but also ...`；`those` 指代 exceptions。

**15.** "This must be either an exception instance or an exception class (a class that derives from BaseException, such as Exception or one of its subclasses)."

> 译文：它必须是一个异常实例，或者一个异常类（即派生自 `BaseException` 的类，比如 `Exception` 或它的某个子类）。
> 拆解：`either ... or ...`；括号里是解释。

**16.** "If an exception class is passed, it will be implicitly instantiated by calling its constructor with no arguments."

> 译文：如果传入的是异常类，它会通过无参调用其构造函数被隐式实例化。
> 拆解：`by calling` 表方式；`its` 指 class。

**17.** "If an unhandled exception occurs inside an except section, it will have the exception being handled attached to it and included in the error message"

> 译文：如果一个未处理的异常发生在 except 块内部，那么正在被处理的异常会被附加到它上面，并包含在错误信息里。
> 拆解：`have sth done` 结构（have the exception attached）；`being handled` 现在分词被动修饰 exception。

**18.** "To indicate that an exception is a direct consequence of another, the raise statement allows an optional from clause"

> 译文：为了表明一个异常是另一个异常的直接结果，raise 语句允许加一个可选的 `from` 子句。
> 拆解：`To indicate that...` 目的状语；`a direct consequence of another` = 另一个的直接结果。

**19.** "It also allows disabling automatic exception chaining using the from None idiom"

> 译文：它还允许用 `from None` 这种写法，关闭自动的异常链接。
> 拆解：`allow doing` 结构；`using ... idiom` 表方式。

**20.** "Some objects define standard clean-up actions to be undertaken when the object is no longer needed, regardless of whether or not the operation using the object succeeded or failed."

> 译文：有些对象定义了标准的清理动作，在对象不再需要时执行，无论使用该对象的操作成功还是失败。
> 拆解：`to be undertaken` 不定式被动修饰 actions；`regardless of whether` = 无论是否。

**21.** "The problem with this code is that it leaves the file open for an indeterminate amount of time after this part of the code has finished executing."

> 译文：这段代码的问题在于，在这部分代码执行完之后，文件还会被打开一段不确定的时间。
> 拆解：`leave + 宾语 + 形容词`（leave the file open）；`for an indeterminate amount of time` = 持续一段不确定的时间。

**22.** "The with statement allows objects like files to be used in a way that ensures they are always cleaned up promptly and correctly."

> 译文：with 语句让文件这类对象能以某种方式被使用，从而确保它们总能被及时、正确地清理。
> 拆解：`allow sth to be done`；`in a way that ensures...` = 以某种能确保……的方式。

### 6.3 读的时候注意

- 看报错先看**最后一行**：异常类型 + 信息；再往上找自己代码的位置。
- `raise` 后面可以是实例 `raise ValueError("bad")`，也可以是类 `raise ValueError`（自动无参实例化）。
- `from exc` 表明“这个异常是那个异常的直接后果”；`from None` 关掉自动链接。
- `try/except/else/finally` 里，`else` 是“没出错才执行”，`finally` 是“无论如何都执行”。
- `with open(...) as f:` 能保证文件被关，不依赖你记得 `close()`；`with` 的对象要实现上下文管理器协议。

**读完自检：** 如何读最后一条错误？`raise` 和 `except ... as e` 分别做什么？为什么 `for line in open(...)` 不如 `with open(...)`？

---

## 7. 最容易混的几组词

| 组 | 区别 | 一句话记忆 |
|---|---|---|
| parameter / argument | 形参 / 实参 | 定义里写的是 parameter，调用时给的是 argument |
| attribute / method | 属性 / 方法 | 方法也是属性的一种（函数对象属性） |
| class variable / instance variable | 类变量 / 实例变量 | 类变量一份共享，实例变量每个对象一份 |
| instance / object | 实例 / 对象 | 实例是“由某个类造出来的对象”，口语里常混用 |
| namespace / scope | 命名空间 / 作用域 | 命名空间是“名字表”，作用域是“哪段代码能看见谁” |
| exception / error | 异常 / 错误 | 异常是运行期抛出的对象；错误是更泛的说法 |
| raise / throw | 抛出 | Python 用 raise，C++/Java 用 throw |
| handle / catch | 处理 / 捕获 | 捕获是手段，处理是结果；Python 用 except 捕获 |
| mutable / immutable | 可变 / 不可变 | list 可变，tuple/str 不可变 |
| override / extend | 重写 / 扩展 | override 换掉实现，extend 在原有基础上加 |
| module / package | 模块 / 包 | 一个 `.py` 是模块，带 `__init__.py` 的目录是包 |
| traceback / stack | 栈回溯 / 栈 | traceback 是打印出来的调用链，stack 是数据结构本身 |

## 8. 读到卡住时的处理顺序

1. **先看代码例子**：教程的文字几乎都在解释上面那段代码，例子看懂了，句子就懂一半。
2. **查词表**：只查卡住的那个词，别整段翻译。
3. **拆句子**：找主语和谓语，把从句用括号圈出来；长句一般就是“主句 + 两三个修饰”。
4. **还不行再看译文**：看完立刻回到英文，把这句话再读一遍。
5. **仍然不懂就跳过**：W01 只要求函数、模块入口和异常；9.5 继承、装饰器、元类都可以以后补。

## 9. 和讲义练习的对应

| 讲义练习 | 对应英文段落 | 读的时候重点看 |
|---|---|---|
| 第 1 题（同一个对象还是两份数据） | 9.3.2—9.3.5 | `self`、实例属性、类变量共享 |
| 第 2 题（默认参数） | 4.9.1 | 默认值只求值一次、可变默认值 |
| 第 3 题（写 `validate_sample`） | 8.2—8.5 | 什么时候 `raise ValueError`、错误信息写什么 |
| 第 4 题（导入工具不启动程序） | 6.1、6.1.1 | 顶层语句、`__name__ == "__main__"` |

读完这四段，再回讲义做练习；练习里卡住时，回到对应小节查词表和长句即可。
