# 1.关系概念
1. pc机上运行节点在路径~/ros/src/zs/，mcu上烧录节点~/ros/src/，这个路径下有/install,/log,/ build,/frimware路径，两者通过agent实现通讯
2. 运行流程
```bash
```
# 2.创建使用流程
1. 在docker容器中使用，优化掉conda的环境
```bash
docker ps -a #查看运行的容器
docker rm < 容器名 > #删除
docker start < 容器名 > --network host < 容器名 > #启动容器并监听宿主端口：这段是添加到命令行快捷键里面的
mkdir ros_docker #创建文件夹，并创建文件Dockerfile
docker build -t ros_dev . #创建镜像
#创建容器以及挂载端口
xhost +local:docker
docker run -it \
  --name ros_espidf_dev \
  -v ~/ros2_ws:/ros2_ws \
  --device /dev/ttyACM0:/dev/ttyACM0 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --network host \
  -e http_proxy=http://127.0.0.1:7890 \
  -e https_proxy=http://127.0.0.1:7890 \
  ros_espidf_dev
#
```
2. espew-s3使用的是原生USB而不是内置，所以插入设备是 dev/ttyACM0
3. 项目创建俺流程ros2 pkg create --build-type ament_python mcu_py_pkg
4. 正确的结构
```bash
/ros2_ws
├── src
│   ├── pc_pkg          # PC 端 ROS2 节点包
│   └── test_agent      # 可能是 micro-ROS 测试程序
├── firmware            # MCU 固件相关
│   ├── freertos_apps   # MCU 端 freertos 示例包
│   └── dev_ws          # MCU 自己的 colcon 工作区
├── build
├── install
└── log
```