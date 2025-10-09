# 1. 项目说明
 本机linux使用的espidf原生框架，在使用micro-ROS2时，区别于*idf.py create_project my_project*创建完整的espidf框架，在ros2_ws工作区*ros2 run micro_ros_setup create_firmware_ws.sh freertos esp32*创建框架，路径下功能（项目）文件放在<a>~/ros2_ws/firmware/freertos_apps/apps/</a>下面的文件夹，文件夹里面存放app.c文件就是普通espidf框架的src/main.c
# 2. micro-ROS的ESP-IDF使用
```bash
# 安装 micro-ROS setup 工具
mkdir -p ~/uros_ws/src && cd ~/uros_ws
git clone -b humble https://github.com/micro-ROS/micro_ros_setup src/micro_ros_setup
rosdep update && rosdep install --from-paths src --ignore-src -y
#获取espidf事例应用
colcon build
source install/setup.bash
cd ~/uros_ws
ros2 run micro_ros_setup create_firmware_ws.sh freertos esp32
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
source /opt/ros/humble/setup.bash
cd ~/uros_ws
source install/setup.bash
ros2 run micro_ros_setup flash_firmware.sh

```
# 3. agent安装并启动
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
# 4. 代码包的可能修改