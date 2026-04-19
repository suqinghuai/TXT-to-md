#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天记录转换工具 - 将txt格式的聊天记录转换为简洁的markdown格式

功能：
- 读取同级目录下的所有txt文件
- 将聊天记录转换为markdown格式
- 使用不同颜色和样式区分发送者
- 每条消息独立显示
- 每4000条消息生成一个md文件
- 简化输出格式，避免文件过大
"""

import os
import re
import sys
from datetime import datetime
from typing import List, Tuple, Optional


class ChatRecordConverter:
    def __init__(self):
        # 用于解析消息的正则表达式
        self.message_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \'(.+?)\'$')

        # 消息计数器
        self.message_count = 0

    def parse_message(self, line: str) -> Optional[Tuple[str, str]]:
        """解析单行消息，返回(时间+用户, 消息内容)"""
        match = self.message_pattern.match(line.strip())
        if match:
            timestamp, user = match.groups()
            return f"{timestamp} - {user}", user
        return None

    def convert_message_to_markdown_simple(self, timestamp_user: str, content: str, user: str) -> str:
        """将单条消息转换为简化的markdown格式"""
        # 处理特殊内容（图片、视频等）
        if content.startswith('[') and content.endswith(']'):
            content_type = content[1:-1]
            if content_type in ['图片', '视频', '语音', '文件']:
                content = f"[{content_type}]"

        # 简化的markdown格式
        if user == '我':
            # 我的消息 - 右对齐
            return f"""
<div style="text-align: right; margin: 8px 0; clear: both;">
    <div style="display: inline-block; max-width: 70%; background: #DCF8C6;
                border-radius: 12px 12px 0 12px; padding: 8px 12px;
                border: 1px solid #A5D6A7;">
        <div style="font-size: 11px; color: #666; margin-bottom: 2px;">{timestamp_user}</div>
        <div style="font-size: 14px; line-height: 1.3;">{content}</div>
    </div>
</div>"""
        else:
            # 其他人的消息 - 左对齐
            return f"""
<div style="text-align: left; margin: 8px 0; clear: both;">
    <div style="display: inline-block; max-width: 70%; background: #FFFFFF;
                border-radius: 12px 12px 12px 0; padding: 8px 12px;
                border: 1px solid #E0E0E0;">
        <div style="font-size: 11px; color: #666; margin-bottom: 2px;">{timestamp_user}</div>
        <div style="font-size: 14px; line-height: 1.3;">{content}</div>
    </div>
</div>"""

    def convert_txt_to_markdown(self, txt_file_path: str) -> List[str]:
        """将txt文件转换为markdown格式，返回生成的文件列表"""
        try:
            with open(txt_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"读取文件 {txt_file_path} 失败: {e}")
            return []

        # 获取文件名作为标题
        file_name = os.path.basename(txt_file_path)
        title = file_name.replace('.txt', '')

        # 生成markdown头部（简化版）
        header = f"""# {title}

<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px; margin: 0 auto; padding: 15px;">

<p style="text-align: center; color: #666; font-size: 12px; margin-bottom: 20px;">
    聊天记录生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</p>

"""

        markdown_files = []
        current_content = header
        self.message_count = 0
        file_index = 1

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:  # 跳过空行
                i += 1
                continue

            # 尝试解析消息头
            parsed = self.parse_message(line)
            if parsed:
                timestamp_user, user = parsed

                # 收集消息内容（可能跨多行）
                content_lines = []
                i += 1

                # 读取后续的非消息头行作为内容
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:  # 空行作为消息分隔
                        i += 1
                        break

                    # 检查是否是新的消息头
                    if self.message_pattern.match(next_line):
                        break

                    content_lines.append(next_line)
                    i += 1

                content = '\n'.join(content_lines)
                if content:
                    # 添加消息到当前文件
                    current_content += self.convert_message_to_markdown_simple(timestamp_user, content, user)
                    self.message_count += 1

                    # 每4000条消息创建新文件
                    if self.message_count % 4000 == 0:
                        # 完成当前文件
                        current_content += "\n</div>"

                        # 生成文件名
                        if file_index == 1:
                            output_file = f"{title}.md"
                        else:
                            output_file = f"{title}_part{file_index}.md"

                        markdown_files.append((output_file, current_content))

                        # 开始新文件
                        file_index += 1
                        current_content = header

                continue

            i += 1

        # 添加最后的内容
        if current_content != header:  # 如果有内容
            current_content += "\n</div>"

            # 生成最后一个文件名
            if file_index == 1:
                output_file = f"{title}.md"
            else:
                output_file = f"{title}_part{file_index}.md"

            markdown_files.append((output_file, current_content))

        return markdown_files

    def process_directory(self, directory: str = ".") -> List[str]:
        """处理指定目录下的所有txt文件"""
        converted_files = []

        # 确保目录存在
        if not os.path.exists(directory):
            print(f"目录不存在: {directory}")
            return converted_files

        # 获取目录下所有txt文件
        txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

        if not txt_files:
            print(f"在目录 {directory} 中未找到txt文件")
            return converted_files

        print(f"找到 {len(txt_files)} 个txt文件:")
        for file in txt_files:
            print(f"  - {file}")

        for txt_file in txt_files:
            txt_path = os.path.join(directory, txt_file)
            print(f"\n正在处理: {txt_file}")

            # 转换为markdown
            markdown_files = self.convert_txt_to_markdown(txt_path)

            if markdown_files:
                for output_file, content in markdown_files:
                    output_path = os.path.join(directory, output_file)

                    # 写入markdown文件
                    try:
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                        print(f"  [OK] 已生成: {output_file}")
                        converted_files.append(output_path)

                    except Exception as e:
                        print(f"  [ERROR] 写入文件失败 {output_file}: {e}")
            else:
                print(f"  [ERROR] 转换失败: {txt_file}")

        return converted_files


def main():
    """主函数"""
    print("聊天记录转换工具")
    print("=" * 50)

    # 获取程序所在目录（支持打包后的exe）
    if getattr(sys, 'frozen', False):
        # 打包后的exe文件
        program_dir = os.path.dirname(sys.executable)
    else:
        # 正常运行的py文件
        program_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"程序所在目录: {program_dir}")
    print()

    converter = ChatRecordConverter()

    # 处理程序所在目录
    converted_files = converter.process_directory(program_dir)

    print("\n" + "=" * 50)
    if converted_files:
        print(f"转换完成！共生成 {len(converted_files)} 个markdown文件:")
        for file in converted_files:
            print(f"  - {os.path.basename(file)}")
        print("\n提示: 生成的markdown文件可以用任何markdown编辑器或浏览器打开查看")
        print("注意: 每4000条消息会自动分割成单独的文件")
    else:
        print("没有成功转换任何文件")

    print("\n" + "=" * 50)
    print("按任意键退出...")
    input()


if __name__ == "__main__":
    main()