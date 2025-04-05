'''
生成适合该库的点阵数据，存到字典
'''

import os
from PIL import Image, ImageFont, ImageDraw
import sys

def find_font_by_name(font_name):
    # 在系统字体目录中查找字体
    if sys.platform == 'win32':  # Windows 系统
        font_dir = "C:/Windows/Fonts"
        for root, dirs, files in os.walk(font_dir):
            for file in files:
                if font_name.lower() in file.lower():
                    return os.path.join(root, file)
    elif sys.platform == 'darwin':  # macOS 系统
        font_dir = "/System/Library/Fonts"
        for root, dirs, files in os.walk(font_dir):
            for file in files:
                if font_name.lower() in file.lower():
                    return os.path.join(root, file)
    elif sys.platform == 'linux':  # Linux 系统
        font_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", f"/home/{os.getenv('USER')}/.fonts"]
        for font_dir in font_dirs:
            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if font_name.lower() in file.lower():
                        return os.path.join(root, file)
    return None  # 如果找不到字体

def char_to_dot_matrix(char, font_name='simhei', font_size=16):
    if font_size in (16, 24, 32):
        image_size = font_size
        cols = image_size // 8  # 16->2, 24->3, 32->4
    else:
        raise ValueError("不支持的字体大小，仅支持 16, 24, 32")

    font_path = find_font_by_name(font_name)
    if font_path is None:
        raise FileNotFoundError(f"未找到字体：{font_name}")

    image = Image.new("L", (image_size, image_size), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    # 居中绘制字符
    bbox = draw.textbbox((0, 0), char, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (image_size - text_width) // 2
    y = (image_size - text_height) // 2
    draw.text((x, y), char, font=font, fill=0)

    threshold = 128
    # 初始化每个块的数据列表
    blocks = [[] for _ in range(cols)]
    # 按行扫描，分别保存每块的字节
    for y in range(image_size):
        for col in range(cols):
            row_bits = []
            start_x = col * 8
            for x in range(start_x, start_x + 8):
                pixel = image.getpixel((x, y))
                bit = 1 if pixel < threshold else 0
                row_bits.append(bit)
            byte = int("".join(str(b) for b in row_bits), 2)
            blocks[col].append(byte)
    # 拼接各块的数据
    dot_data = []
    for block in blocks:
        dot_data.extend(block)
    return dot_data

def utf8_to_int(char):
    utf8_bytes = char.encode("utf-8")
    return (utf8_bytes[0] << 16) | (utf8_bytes[1] << 8) | utf8_bytes[2]

def generate_fonts_dict(chars, font_name='simhei', font_size=16):
    font_dict = {}
    for ch in chars:
        code = utf8_to_int(ch)
        font_dict[code] = (char_to_dot_matrix(ch, font_name, font_size), ch)
    return font_dict

def save_fonts_py(font_dict, filename="font16.txt", font_size=16):
    cols = font_size // 8
    dict_name = f"font{font_size}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{dict_name} = {{\n")
        for code, (dot_data, char) in font_dict.items():
            f.write(f"    0x{code:06x}:  # {char}\n")
            f.write("        [")
            for i, byte in enumerate(dot_data):
                f.write(f"0x{byte:02X}")
                if i != len(dot_data) - 1:
                    f.write(", ")
                    if (i + 1) % font_size == 0:
                        f.write("\n         ")
            f.write("],\n")
        f.write("}\n")

if __name__ == "__main__":
    chars = "你好我是天才"
    font_name = "simhei"  # 可填字体名，如 'simhei', 'simsun' 等
    font_sizes = [16, 24, 32]
    for font_size in font_sizes:
        font_dict = generate_fonts_dict(chars, font_name, font_size)
        filename = f"font{font_size}.txt"
        save_fonts_py(font_dict, filename, font_size)
        print(f"已生成兼容 _display_font{font_size} 的字库 {filename}")
