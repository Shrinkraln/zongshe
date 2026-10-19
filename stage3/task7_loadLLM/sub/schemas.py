# -*- coding: utf-8 -*-
"""
五件套工具 Schema · 第7课（task7_loadLLM，P11/P13）
来源：navigate_to（第4课）/ get_semantic_map（第6课）/ capture_and_describe（第5课相机，本课占位）
      say、stop（本课新造；stop 最高优先级、无条件可用）
审计四点（P13 案例①）：① required 齐 ② 无编造字段 ③ description 含纪律 ④ 参数类型与实现一致
冻结：本文件为实验冻结对象（预注册单留 SHA256）——改 description/schema 即重跑十次。
"""

NAVIGATE_DISCIPLINE = "只能使用语义地图或预设点位中存在的位置；禁止编造坐标。"

SCHEMAS = {
    "navigate_to": {
        "description": (
            "导航到目标位置（x, y 为地图坐标，单位米）。"
            + NAVIGATE_DISCIPLINE
            + " label 为可选语义名（命名点位 id，如 W1_door）。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "目标 x 坐标（米）"},
                "y": {"type": "number", "description": "目标 y 坐标（米）"},
                "label": {"type": "string", "description": "可选语义名（命名点位 id）"},
            },
            "required": ["x", "y"],
            "additionalProperties": False,
        },
    },
    "get_semantic_map": {
        "description": "获取语义地图：命名点位、已知物体及其新鲜度（state/age_s）。",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    "capture_and_describe": {
        "description": "用相机拍一张照片并回答关于画面内容的问题（本课占位，第9课点亮）。",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "关于画面的问题"}},
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    "say": {
        "description": "对周围的人说一句话。",
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "要说的话"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    },
    "stop": {
        "description": "立即停止运动。最高优先级、无条件可用。",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}


def build_tools():
    """转成 OpenAI tools 参数格式（供 llm_planner.py 使用）。"""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": spec["description"],
                "parameters": spec["parameters"],
            },
        }
        for name, spec in SCHEMAS.items()
    ]
