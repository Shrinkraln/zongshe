# 1. 青煜恒
主要负责在ubuntu系统上调试原生espidf框架，到目前为止前期同样是在win的pio上进行实践，然后中期查询发现整个项目后期可能性能要求在虚拟机上有所欠缺，于是安装ubuntu系统，

## 1. ros,espidf,pio环境冲突
在项目编译过程，如果将ros和espidf直接在系统环境source的话，会遇到python版本冲突以及工具链使用不齐全的情况，以及经典的ros环境启动后espidf环境无法启动（检查到$ROS_DOSTRO定义之后会跳过espidf的环境启动），为了保持环境不互相污染，使用conda隔离ros,同时创建环境先espidf启动再ros启动。
![alt text](./md_resources/image.png)
## 2. ros通讯节点
 本机linux使用的espidf原生框架，在使用micro-ROS2时，区别于*idf.py create_project my_project*创建完整的espidf框架，在ros2_ws工作区*ros2 run micro_ros_setup create_firmware_ws.sh freertos esp32*创建框架，路径下功能（项目）文件放在<a>~/ros2_ws/firmware/freertos_apps/apps/</a>下面的文件夹，文件夹里面存放app.c文件就是普通espidf框架的src/main.c
### 1. micro-ROS的ESP-IDF使用
```bash
# 安装 micro-ROS setup 工具
mkdir -p ~/uros_ws/src && cd ~/uros_ws
git clone -b humble https://github.com/micro-ROS/micro_ros_setup src/micro_ros_setup
rosdep update && rosdep install --from-paths src --ignore-src -y
#获取espidf事例应用
colcon build
source install/setup.bash
cd ~/uros_ws
ros2 run micro_ros_setup create_firmware_ws.sh freertos esp32   #只需要执行一次
#选择应用并配置
ros2 run micro_ros_setup configure_firmware.sh int32_publisher -t serial -d /dev/ttyUSB
#编译和烧录
ros2 run micro_ros_setup build_firmware.sh
ros2 run micro_ros_setup flash_firmware.sh
```
一点注意事项：
1. 除了烧录，环境是ROS2+ESP-IDF的conda环境
2. 烧录的环境是系统环境conda deactivate两次实现
3. 退出之后要启动ROS2自己的虚拟环境
```bash
source /opt/ros/humble/setup.bash
cd ~/uros_ws
source install/setup.bash
```
4. 串口权限设置
```bash
#$USER是自己的用户名
sudo usermod -a -G dialout $USER
```
**已经初始化之后的启动流程**
```bash
conda activate espidf_ros2_env
cd uros_ws
ros2 run micro_ros_setup build_firmware.sh
conda deactivate
conda deactivate
#source /opt/ros/humble/setup.bash
cd ~/uros_ws
source install/setup.bash
ros2 run micro_ros_setup flash_firmware.sh

```
### 2. agent安装并启动
**在系统环境下安装**
1. 一些准备
```bash
#安装colcon构建工具
sudo apt install python3-colcon-common-extensions
#安装依赖
sudo apt install git wget cmake build-essential oython3-pip python3-rosdep
sudo rosdep init
rosdep update
pip install catkin_pkg empy lark
```
2. 创建工作区及构建
```bash
mkdir -p ~/micro-ros-agent_ws/src
#拉取代码
cd ~/micro-ros-agent_ws
ros2 run micro_ros_setup create_agent_ws.sh udp
#检查结构，里面应该有 micro-ros-agent
ls ~/micro-ros-agent_ws/src
#清理旧构建 
cd ~/micro-ros-agent_ws
rm -rf build install log
#启动ROS2环境
source /opt/ros/humble/setup.bash
#编译
colcon build --symlink-install
```
3. 运行agent
```bash
source ~/micro-ros-agent_ws/install/setup.bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```
### 3. 代码包的可能修改
遇到了事例代码版本号较落后，rcl等头文件的路径错误导致cmake报错。
主要修改了makelist中的idf_componnent_register路径修改以及明确完善

### 4. 编辑流程的修改
到上一次为止，整个流程最后的问题是烧录无法进入串口，控制版是没有问题的，查询的结果确指向控制版操作，进一步查询后ai解答是项目配置构建流程不对，到目前还在试验阶段。