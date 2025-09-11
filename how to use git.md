*下载git并安装自行找教程（）*

# 1. 本地项目结构

```bash
#打开文件夹，此文件夹下放需要上传的所有代码和Markdown文档，这个文件夹暂时命名为coding_codes（可根据自身喜好命名，只是这里用此符号表示整个项目的根目录）（后续可能使用~代替coding_codes表示项目的根目录），大致结构如下
coding_codes/                 # 顶层 Git 仓库
├── .git/                     # Git 仓库元数据（统一管理整个 coding_codes）
├── projectA/                 # 一个 PIO 项目
│   ├── platformio.ini        # PIO 项目配置文件（核心）
│   ├── src/                  # 源代码目录
│   │   └── main.c
│   |
│   ├── .pio/                 # PIO 构建生成目录（通常写在 .gitignore）
│   └── README.md             # 项目说明
│
├── projectB/                 # 其他项目（此处省略）
└── projectC/                 # 其他项目（此处省略）
```
```bash
#.gitignore 常见内容（适用于 PIO 项目）：
#在创建远程库的时候会使用（但是在创建流程中没有这两个选项，可以待后续配置（（（吧
.pio/
.vscode/
```

# 2. 远程库的创建

1. 点击New repository

![屏幕截图 2025-09-12 010619](.\md_resources\屏幕截图 2025-09-12 010619.png)

2. 输入远程库名（任意，和本地库所在目录名无关）（注意是public这个选项不是private），然后create

![屏幕截图 2025-09-12 010940](.\md_resources\屏幕截图 2025-09-12 010940.png)

3. 先进行下一步，页面暂时保存

# 3. Git的使用

```bash
#初始化本地git库
#在~/路径右键空白点击"更多"->"Git bash here"
#如果无响应，可以win搜索Git bash，但是需要额外进行以下步骤
cd 你的~文件的路径		
#如果是从win的资源管理器复制的需注意win路径是\而git是/
#git的复制粘贴是ctrl+c/v+shift
#文件名有空格需要双引号引起来""
```

![屏幕截图 2025-09-12 002947](.\md_resources\屏幕截图 2025-09-12 002947.png)

*这里的蓝色的(main)是建立本地库之后才有的，正常步骤这里没有，黄色的路径就是现在git打开的路径，应该是到自己的全部文件根目录~*

```bash
###初始化本地库
git init
###添加文件到缓存区（一般是有稳定运的版本才进行此操作以及后续操作，并且是对指定文件夹（即一个项目文件夹进行操作
#全部
git add .
#指定文件（常用
git add project1
###从缓存区删除全部文件
git rm --cached -r .
###将缓存区文件保存到本地git库
git commit -m"你要提交到本地库并且附带的信息"		#比如说 -m"light a led"
###本地库连接远程库（github上的
#在远程库的create之后最下方有代码，执行即可
```

![屏幕截图 2025-09-12 011807](.\md_resources\屏幕截图 2025-09-12 011807.png)

```bash
###后续代码提交到本地库之后，再提交到远程库执行
git push
```

# 4. 查看他人文件

```bash
#可以在线查看别人的文档，也可以进行如下克隆到本地
#但是需要在克隆的文件地址先初始化
git init
git clone git@github.com:Shrinkraln/zongshe.git
```

