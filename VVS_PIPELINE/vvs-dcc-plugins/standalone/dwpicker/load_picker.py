# -*- coding: utf-8 -*-
# This file is a supplement to Dream Wall Picker.
# author: wangruilong
# date: 20250624

import os
import maya.cmds as cmds
from functools import partial
import time
import datetime

# 缓存数据存储结构
CACHE = {
    "projects": {},  # 存储项目/角色/picker信息
    "last_scan_time": 0,  # 最后扫描时间
    "base_path": None  # 基础路径
}

# 缓存有效期（秒） - 减少频繁扫描
CACHE_VALIDITY = 30

def get_base_path():
    """从环境变量获取picker基础路径"""
    # 如果缓存中有且路径有效，直接返回
    if CACHE["base_path"] and os.path.exists(CACHE["base_path"]):
        return CACHE["base_path"]
    
    base_path = os.environ.get("DWPICKER_PROJECT_DIRECTORY")
    
    if not base_path:
        cmds.warning("环境变量 'DWPICKER_PROJECT_DIRECTORY' 未设置")
        return None
    
    if not os.path.exists(base_path):
        cmds.warning(f"环境变量指定的路径不存在: {base_path}")
        return None
    
    # 更新缓存
    CACHE["base_path"] = base_path
    return base_path

def scan_directory(path):
    """扫描目录并返回子文件夹列表（带缓存）"""
    current_time = time.time()
    
    # 检查缓存是否有效
    if path in CACHE["projects"]:
        cache_data = CACHE["projects"][path]
        if current_time - cache_data["timestamp"] < CACHE_VALIDITY:
            return cache_data["folders"]
    
    # 扫描目录
    folders = []
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folders.append(item)
    except Exception as e:
        cmds.warning(f"扫描目录失败: {path} - {str(e)}")
    
    # 更新缓存
    CACHE["projects"][path] = {
        "folders": sorted(folders),
        "timestamp": current_time
    }
    
    return sorted(folders)

def scan_json_files(path):
    """扫描目录中的JSON文件（带缓存和修改时间）"""
    current_time = time.time()
    
    # 检查缓存是否有效
    if path in CACHE["projects"]:
        cache_data = CACHE["projects"][path]
        if "json_files" in cache_data and current_time - cache_data["timestamp"] < CACHE_VALIDITY:
            return cache_data["json_files"]
    
    # 扫描文件并获取修改时间
    json_files = []
    try:
        for item in os.listdir(path):
            if item.lower().endswith('.json'):
                full_path = os.path.join(path, item)
                # 获取文件修改时间
                mtime = os.path.getmtime(full_path)
                # 格式化为可读日期
                mod_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                # 去除扩展名显示
                display_name = os.path.splitext(item)[0]
                # 存储文件名和修改时间
                json_files.append({
                    "name": display_name,
                    "date": mod_date,
                    "full_path": full_path
                })
    except Exception as e:
        cmds.warning(f"扫描JSON文件失败: {path} - {str(e)}")
    
    # 按修改时间降序排序（最新文件在前）
    json_files.sort(key=lambda x: os.path.getmtime(x["full_path"]), reverse=True)
    
    # 更新缓存
    if path in CACHE["projects"]:
        CACHE["projects"][path]["json_files"] = json_files
        CACHE["projects"][path]["timestamp"] = current_time
    else:
        CACHE["projects"][path] = {
            "json_files": json_files,
            "timestamp": current_time
        }
    
    return json_files

def create_picker_loader():
    # 获取基础路径
    base_path = get_base_path()
    if base_path is None:
        cmds.confirmDialog(title="错误", message="无法获取有效的 picker 路径，请检查环境变量设置", button=["确定"])
        return
    
    # 删除已存在的窗口
    if cmds.window("pickerLoaderWin", exists=True):
        cmds.deleteUI("pickerLoaderWin")
    
    # 创建主窗口
    window = cmds.window("pickerLoaderWin", title="Picker Loader", s=True)

    cmds.formLayout('main_formLayout')
    cmds.formLayout('layout_formLayout')
    cmds.formLayout('col_formLayout')

    # 刷新按钮
    cmds.button(
        'refresh_button', ann='刷新 pickers 文件列表缓存',
        w=40, bgc=[0.41999998688697815, 0.5600000023841858, 0.75],
        l='刷新',
        command=partial(refresh_cache, base_path)
    )

    cmds.formLayout('project_formLayout')

    # 项目选择下拉菜单
    cmds.text('project_text', l='项目：')
    cmds.optionMenu(
        'projectMenu',
        w=80, h=20, 
        changeCommand=partial(update_character_menu, base_path)
    )

    cmds.formLayout('character_formLayout', p='col_formLayout')

    # 角色选择下拉菜单
    cmds.text('character_text', l='角色：')
    cmds.optionMenu(
        'characterMenu',
        w=120, h=20, 
        changeCommand=partial(update_picker_menu, base_path)
    )

    cmds.separator('separator_1', p='layout_formLayout', st='in')
    cmds.formLayout('picker_formLayout', p='layout_formLayout')

    # Picker文件选择下拉菜单
    cmds.text('picker_text', l='Picker 文件：')
    cmds.optionMenu('pickerMenu', h=25, changeCommand=partial(update_date_display, base_path))

    # 日期显示文本
    cmds.text('date_text',p='picker_formLayout',w=120,l='修改: ____-__-__ __:__',al='left')

    # 打开按钮
    cmds.button(
        'open_DW_button', p='layout_formLayout',
        h=30,
        ann='打开 Dream Wall Picker', l='DW',
        command=open_DW
    )
    
    # 导入按钮
    cmds.button(
        'import_button', p='layout_formLayout',
        h=30, bgc=[0.41999998688697815, 0.75, 0.41999998688697815],
        l='打开 Picker',
        command=partial(load_picker, base_path)
    )

    # 布局
    cmds.formLayout('main_formLayout', e=1, af=[['layout_formLayout', 'top', 3], ['layout_formLayout', 'left', 2], ['layout_formLayout', 'right', 2], ['layout_formLayout', 'bottom', 3]])
    cmds.formLayout('layout_formLayout', e=1, af=[['col_formLayout', 'top', 0], ['col_formLayout', 'left', 0], ['col_formLayout', 'right', 0], ['separator_1', 'left', 0], ['separator_1', 'right', 0], ['picker_formLayout', 'left', 0], ['picker_formLayout', 'right', 0], ['import_button', 'right', 0], ['import_button', 'bottom', 0], ['open_DW_button', 'left', 0], ['open_DW_button', 'bottom', 0]], ac=[['separator_1', 'top', 5, 'col_formLayout'], ['picker_formLayout', 'top', 5, 'separator_1'], ['import_button', 'top', 5, 'picker_formLayout'], ['open_DW_button', 'top', 5, 'picker_formLayout']], ap=[['import_button', 'left', 1, 20], ['open_DW_button', 'right', 1, 20]])
    cmds.formLayout('col_formLayout', e=1, af=[['refresh_button', 'top', 0], ['refresh_button', 'left', 0], ['refresh_button', 'bottom', 0], ['project_formLayout', 'top', 0], ['project_formLayout', 'bottom', 0], ['character_formLayout', 'top', 0], ['character_formLayout', 'right', 0], ['character_formLayout', 'bottom', 0]], ac=[['project_formLayout', 'left', 5, 'refresh_button'], ['character_formLayout', 'left', 7, 'project_formLayout']], ap=[['project_formLayout', 'right', 7, 50]])
    cmds.formLayout('project_formLayout', e=1, af=[['project_text', 'top', 0], ['project_text', 'left', 0], ['project_text', 'bottom', 0], ['projectMenu', 'top', 0], ['projectMenu', 'right', 0], ['projectMenu', 'bottom', 0]], ac=[['projectMenu', 'left', 3, 'project_text']])
    cmds.formLayout('character_formLayout', e=1, af=[['character_text', 'top', 0], ['character_text', 'left', 0], ['character_text', 'bottom', 0], ['characterMenu', 'top', 0], ['characterMenu', 'right', 0], ['characterMenu', 'bottom', 0]], ac=[['characterMenu', 'left', 3, 'character_text']])
    cmds.formLayout('picker_formLayout',e=1,af=[['picker_text', 'top', 0], ['picker_text', 'left', 0], ['picker_text', 'bottom', 0], ['pickerMenu', 'top', 0], ['pickerMenu', 'bottom', 0], ['date_text', 'top', 0], ['date_text', 'right', 0], ['date_text', 'bottom', 0]],ac=[['pickerMenu', 'left', 5, 'picker_text'], ['pickerMenu', 'right', 5, 'date_text']])

    # 填充项目菜单
    populate_projects(base_path)
    
    cmds.showWindow(window)

def populate_projects(base_path):
    """填充项目下拉菜单"""
    cmds.optionMenu("projectMenu", edit=True, deleteAllItems=True)
    
    projects = scan_directory(base_path)
    
    if not projects:
        cmds.menuItem(label="未找到项目", parent="projectMenu")
        return
    
    for project in projects:
        cmds.menuItem(label=project, parent="projectMenu")
    
    # 自动更新角色菜单
    update_character_menu(base_path)

def update_character_menu(base_path, *_):
    """更新角色下拉菜单基于当前选择的项目"""
    cmds.optionMenu("characterMenu", edit=True, deleteAllItems=True)
    
    project = cmds.optionMenu("projectMenu", query=True, value=True)
    if not project or project == "未找到项目":
        cmds.menuItem(label="未找到角色", parent="characterMenu")
        return
    
    character_path = os.path.join(base_path, project)
    
    # 使用缓存扫描
    characters = scan_directory(character_path)
    
    if not characters:
        cmds.menuItem(label="未找到角色", parent="characterMenu")
        return
    
    for char in characters:
        cmds.menuItem(label=char, parent="characterMenu")
    
    # 自动更新picker菜单
    update_picker_menu(base_path)

def update_picker_menu(base_path, *_):
    """更新picker文件下拉菜单基于当前选择的角色"""
    cmds.optionMenu("pickerMenu", edit=True, deleteAllItems=True)
    
    project = cmds.optionMenu("projectMenu", query=True, value=True)
    character = cmds.optionMenu("characterMenu", query=True, value=True)
    
    if not project or not character or "未找到" in project or "未找到" in character:
        cmds.menuItem(label="未找到 picker", parent="pickerMenu")
        update_date_display(base_path)  # 清空日期显示
        return
    
    picker_path = os.path.join(base_path, project, character)
    
    # 使用缓存扫描JSON文件
    picker_files = scan_json_files(picker_path)
    
    if not picker_files:
        cmds.menuItem(label="未找到 picker", parent="pickerMenu")
        update_date_display(base_path)  # 清空日期显示
        return
    
    # 创建菜单项
    for picker in picker_files:
        cmds.menuItem(label=picker['name'], parent="pickerMenu")
    
    # 更新日期显示
    update_date_display(base_path)

def update_date_display(base_path, *_):
    """更新日期显示文本"""
    # 获取当前选择的picker项
    picker_name = cmds.optionMenu("pickerMenu", query=True, value=True)
    
    if not picker_name or picker_name == "未找到 picker":
        cmds.text('date_text', edit=True, label='修改: ____-__-__ __:__')
        return
    
    # 获取当前项目、角色和路径
    project = cmds.optionMenu("projectMenu", query=True, value=True)
    character = cmds.optionMenu("characterMenu", query=True, value=True)
    
    if not project or not character or "未找到" in project or "未找到" in character:
        cmds.text('date_text', edit=True, label='修改: ____-__-__ __:__')
        return
    
    picker_path = os.path.join(base_path, project, character)
    
    # 从缓存中获取picker信息
    cache_data = CACHE["projects"].get(picker_path)
    if not cache_data or "json_files" not in cache_data:
        cmds.text('date_text', edit=True, label='修改: ____-__-__ __:__')
        return
    
    # 查找匹配的picker文件
    for picker in cache_data["json_files"]:
        if picker["name"] == picker_name:
            cmds.text('date_text', edit=True, label=f"修改: {picker['date']}")
            return
    
    # 如果没有找到
    cmds.text('date_text', edit=True, label='修改: ____-__-__ __:__')

def refresh_cache(base_path, *_):
    """清除缓存并刷新UI"""
    global CACHE
    CACHE = {"projects": {}, "last_scan_time": 0, "base_path": base_path}
    populate_projects(base_path)
    cmds.warning("缓存已刷新，重新扫描目录...")

def load_picker(base_path, *_):
    """执行导入操作"""
    project = cmds.optionMenu("projectMenu", query=True, value=True)
    character = cmds.optionMenu("characterMenu", query=True, value=True)
    picker_name = cmds.optionMenu("pickerMenu", query=True, value=True)
    
    if not project or not character or not picker_name or "未找到" in project or "未找到" in character or picker_name == "未找到 picker":
        cmds.warning("请选择有效的项目、角色和 picker 文件")
        return
    
    # 构建完整路径
    picker_path = os.path.join(base_path, project, character, f"{picker_name}.json")
    
    if not os.path.exists(picker_path):
        cmds.warning(f"Picker 文件不存在: {picker_path}")
        return
    
    import dwpicker
    dwpicker.show(editable=False, pickers=None, ignore_scene_pickers=True)
    dwpicker.open_picker_file(picker_path)
    print(f"### 找到 picker 文件: {picker_path}")

def open_DW(*_):
    import dwpicker
    dwpicker.show(editable=False, pickers=None, ignore_scene_pickers=True)

# 运行UI
if __name__ == "__main__":
    create_picker_loader()