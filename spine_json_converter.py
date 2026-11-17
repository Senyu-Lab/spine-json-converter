import argparse
import json
import shutil
import string
import sys
from pathlib import Path


def convert_json(json_path: Path) -> None:
    # 检查输入文件
    if not json_path.is_file():
        raise FileNotFoundError(f"找不到 JSON 文件：{json_path}")

    backup_path = json_path.with_suffix(json_path.suffix + ".bak")

    if backup_path.exists():
        raise FileExistsError(
            f"备份文件已存在：{backup_path}\n"
            "请先检查或移走已有备份，再运行脚本。"
        )

    # 读取并解析 JSON
    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("JSON 根节点必须是对象。")

    # 检查 skeleton
    skeleton = data.get("skeleton")

    if not isinstance(skeleton, dict):
        raise ValueError("JSON 中不存在有效的 skeleton 对象。")

    # 将 hash 插入 skeleton 对象的最前面
    if "hash" not in skeleton:
        data["skeleton"] = {"hash": "", **skeleton}
        hash_added = True
    else:
        hash_added = False

    # 检查 animations
    animations = data.get("animations", {})

    if not isinstance(animations, dict):
        raise ValueError("animations 必须是对象。")

    changed_timelines = 0
    valid_hex = set(string.hexdigits)

    # 转换 animations -> slots 下的 color 时间轴
    for animation_name, animation in animations.items():
        if not isinstance(animation, dict):
            raise ValueError(f"动画 {animation_name} 的数据格式不正确。")

        slots = animation.get("slots", {})

        if not isinstance(slots, dict):
            raise ValueError(f"动画 {animation_name} 的 slots 格式不正确。")

        for slot_name, slot in slots.items():
            if not isinstance(slot, dict):
                raise ValueError(
                    f"动画 {animation_name} 的插槽 {slot_name} 格式不正确。"
                )

            if "color" not in slot:
                continue

            if "rgba" in slot:
                raise ValueError(
                    f"动画 {animation_name} 的插槽 {slot_name} "
                    "同时存在 color 和 rgba，已停止转换。"
                )

            frames = slot["color"]

            if not isinstance(frames, list):
                raise ValueError(
                    f"动画 {animation_name} 的插槽 {slot_name} "
                    "的 color 时间轴不是列表。"
                )

            # 检查所有关键帧的颜色值
            for frame in frames:
                if not isinstance(frame, dict):
                    raise ValueError("发现格式不正确的 color 关键帧。")

                color = frame.get("color")

                if (
                    not isinstance(color, str)
                    or len(color) != 8
                    or not all(char in valid_hex for char in color)
                ):
                    raise ValueError(
                        f"发现无效的颜色值：{color} "
                        f"（动画：{animation_name}，插槽：{slot_name}）"
                    )

            slot["rgba"] = slot.pop("color")
            changed_timelines += 1

    # 没有任何需要修改的内容
    if not hash_added and changed_timelines == 0:
        print("JSON 无需转换，未修改文件。")
        return

    # 备份原始文件
    shutil.copy2(json_path, backup_path)

    temp_path = json_path.with_suffix(json_path.suffix + ".tmp")

    try:
        # 先写入临时文件，再替换原文件
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")

        temp_path.replace(json_path)

    except Exception:
        if temp_path.exists():
            temp_path.unlink()

        # 尝试恢复原始文件
        shutil.copy2(backup_path, json_path)
        raise

    print("转换成功！")
    print(f"添加 hash：{'是' if hash_added else '否（原本已存在）'}")
    print(f"转换 color 时间轴：{changed_timelines}")
    print(f"输出文件：{json_path}")
    print(f"原始备份：{backup_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert bone3 exported Spine JSON files."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input Spine JSON file."
    )

    args = parser.parse_args()

    try:
        convert_json(args.input)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"转换失败：{error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
