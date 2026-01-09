import os
import tempfile

from PIL import Image, ImageDraw, ImageFont,ImageOps

default_font = os.path.dirname(__file__) + '/resources/font/MSYH.TTF'
def draw_text(image, position, text, font, color):
    x, y = position
    draw = ImageDraw.Draw(image)
    draw.text((x, y), text, font=font, fill=tuple(color))


def comp(position, title, title_size, text_list,  text_size, image_path,image_bytes,x_thumb,y_thumb, color,space):
    temp_save_file = tempfile.mkdtemp(prefix='playblast_')+'.png'
    _image = Image.open(image_path)
    draw = ImageDraw.Draw(_image)
    font_path=default_font

    _font = ImageFont.truetype(font_path, title_size)

    draw_text(_image, position, title, _font, color)

    x = position[0]
    y = position[1]

    bbox = draw.textbbox((x, y), title, font=_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    y+=text_height

    for text in text_list:
        y += space
        _font = ImageFont.truetype(font_path, text_size)
        draw_text(_image, (x,y), text, _font, color)

    #合成图片
    if os.path.exists(image_bytes):
        with Image.open(image_bytes) as img:
            original_width, original_height = img.size
            new_width, new_height = original_width // 3, original_height // 3
            img_small = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # 给缩小后的截图添加边框
            border_color = (150, 150, 150)  # 灰色边框
            border_size = 2  # 边框大小
            img_small_with_border = ImageOps.expand(img_small, border=border_size, fill=border_color)

            #_image.paste(img_small, (x_thumb, y_thumb))

            _image.paste(img_small_with_border, (x_thumb, y_thumb))
    #print(temp_save_file)
    _image.save(temp_save_file)

    return temp_save_file
