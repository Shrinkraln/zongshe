# 1. 环境搭建

## 1. 项目搭建慢

1. 更改C:\Users\LENOVO\.platformio\penv\pip.config，改变pip安装源

```she
[global]
user=no
index-url=https://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host=mirrors.aliyun.com
```

2. 删除C:\Users\LENOVO\.platformio\.cache文件夹下全部文件

## 2. esp-idf环境搭建

* vsCode里的插件安装之后有py文件未找到的报错

参考https://blog.csdn.net/Freddy_Ssc/article/details/146319577

1. https://dl.espressif.com/dl/esp-idf/下载
2. 打开esp pwershell

```she
PS D:\coding_tools\espidf\5.5\Espressif\frameworks\esp-idf-v5.5> cd D:\coding_codes\robot_base\src\hello_world
PS D:\coding_codes\robot_base\src\hello_world> idf.py set-target esp32s3 //指定目标板
idf.py build
idf.py -p COM4 flash
udf.py -p COM4
```

* 安装之后再在vscode进行advanced配置

* 如果说报错pip not valid，只需删除\Espressif\tools路径下的idf-python文件夹

## 3. 完整版

1.  重新删除pio插件安装，注意原来c盘下的.platformio文件也要删除
2. pio 插件的espidf是自己安装的依赖，无关espidf插件（后者是本机espidf的gui图形界面，本机espidf可以是原生的官网下载的cmd然后导入espidf插件，也可以是espidf插件下载的
3. pio run和idf.py build是两者的界面下的执行原逻辑，两者不能同时执行，，，虽然pio底层仍然是封装espidf，，，pio构建的项目和espidf构建的项目结构不太一样，建议谁创建的谁编译
4. 在项目根目录的cmake加上以下代码，避免报错git库检验

```cm
set(PROJECT_VER "1.0.0")
```

5. 编译的时候删除微软管家，编译进程加快
6. 项目编译失败了要先pio run -t删除缓存，不然容易线程冲突
