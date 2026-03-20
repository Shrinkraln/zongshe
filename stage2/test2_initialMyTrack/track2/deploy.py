#!/usr/bin/env python3
"""
每次重新生成 DAE 后运行此脚本部署到 Ignition worlds 目录
"""
import re

MESH_DIR = '/home/shrinkraln/codes/gazebo_models/world5/meshes'
WORLD_PATH = '/opt/ros/humble/share/turtlebot4_ignition_bringup/worlds/custom_track_lidar.sdf'

# 官方 world 基础内容（与 maze.sdf 格式完全一致，无 Sensors 插件）
BASE_WORLD = '''<?xml version="1.0"?>
<sdf version='1.8'>
    <world name='custom_track_lidar'>
        <physics name='1ms' type='ignored'>
            <max_step_size>0.003</max_step_size>
            <real_time_factor>1</real_time_factor>
            <real_time_update_rate>1000</real_time_update_rate>
        </physics>
        <plugin name='ignition::gazebo::systems::Physics' filename='ignition-gazebo-physics-system' />
        <plugin name='ignition::gazebo::systems::UserCommands' filename='ignition-gazebo-user-commands-system' />
        <plugin name='ignition::gazebo::systems::SceneBroadcaster' filename='ignition-gazebo-scene-broadcaster-system' />
        <plugin name='ignition::gazebo::systems::Contact' filename='ignition-gazebo-contact-system' />
        <light name='sun' type='directional'>
            <cast_shadows>1</cast_shadows>
            <pose>0 0 10 0 -0 0</pose>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.2 0.2 0.2 1</specular>
            <attenuation>
                <range>1000</range>
                <constant>0.90000000000000002</constant>
                <linear>0.01</linear>
                <quadratic>0.001</quadratic>
            </attenuation>
            <direction>-0.5 0.1 -0.9</direction>
            <spot><inner_angle>0</inner_angle><outer_angle>0</outer_angle><falloff>0</falloff></spot>
        </light>
        <gravity>0 0 -9.8</gravity>
        <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
        <atmosphere type='adiabatic' />
        <scene>
            <ambient>0.4 0.4 0.4 1</ambient>
            <background>0.7 0.7 0.7 1</background>
            <shadows>1</shadows>
        </scene>
        <model name='ground_plane'>
            <static>1</static>
            <link name='link'>
                <collision name='collision'>
                    <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
                    <surface><friction><ode /></friction><bounce /><contact /></surface>
                </collision>
                <visual name='visual'>
                    <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
                    <material>
                        <ambient>0.8 0.8 0.8 1</ambient>
                        <diffuse>0.8 0.8 0.8 1</diffuse>
                        <specular>0.8 0.8 0.8 1</specular>
                    </material>
                    <plugin name='__default__' filename='__default__' />
                </visual>
            </link>
            <plugin name='__default__' filename='__default__' />
            <pose>0 0 0 0 -0 0</pose>
        </model>

        <model name="wall_0">
            <static>true</static>
            <pose>0 0 0 0 0 0</pose>
            <link name="link">
                <collision name="col">
                    <geometry><mesh><uri>file://{mesh_dir}/track_outer.dae</uri></mesh></geometry>
                </collision>
                <visual name="vis">
                    <geometry><mesh><uri>file://{mesh_dir}/track_outer.dae</uri></mesh></geometry>
                    <material><ambient>0.85 0.15 0.15 1</ambient><diffuse>0.85 0.15 0.15 1</diffuse></material>
                </visual>
            </link>
        </model>

        <model name="wall_1">
            <static>true</static>
            <pose>0 0 0 0 0 0</pose>
            <link name="link">
                <collision name="col">
                    <geometry><mesh><uri>file://{mesh_dir}/track_inner.dae</uri></mesh></geometry>
                </collision>
                <visual name="vis">
                    <geometry><mesh><uri>file://{mesh_dir}/track_inner.dae</uri></mesh></geometry>
                    <material><ambient>0.15 0.15 0.85 1</ambient><diffuse>0.15 0.15 0.85 1</diffuse></material>
                </visual>
            </link>
        </model>

    </world>
</sdf>'''

content = BASE_WORLD.replace('{mesh_dir}', MESH_DIR)
with open(WORLD_PATH, 'w') as f:
    f.write(content)

with open(WORLD_PATH) as f:
    c = f.read()
assert c.count('wall_0') == 1
assert c.count('ground_plane') == 1
assert 'custom_track_lidar' in c
assert 'Sensors' not in c
print("部署成功")
print(f"  ground_plane: {c.count('ground_plane')}")
print(f"  wall_0:       {c.count('wall_0')}")
print(f"  wall_1:       {c.count('wall_1')}")
print(f"  Sensors插件:  {'有(错误)' if 'Sensors' in c else '无(正确)'}")