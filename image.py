from PIL import Image, ImageEnhance
import argparse
import sys
import os
import platform

# Наборы символов для ASCII-арта
ASCII_SETS = {
    'default': '@%#*+=-:. ',
    'simple': '@#. ',
    'complex': '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. '
}

def supports_color():
    """Проверка поддержки цвета в терминале"""
    if platform.system() == 'Windows':
        # Включаем поддержку ANSI на Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except:
            return False
    else:
        # Для Unix-подобных систем
        return 'TERM' in os.environ and os.environ['TERM'] != 'dumb'

def resize_image(image, new_width=80, new_height=None):
    width, height = image.size
    if new_height is None:
        ratio = height / width / 1.65
        new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def adjust_image(image, brightness=1.0, contrast=1.0):
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
    return image

def image_to_grayscale(image):
    return image.convert('L')

def get_ansi_color(r, g, b):
    """Получение ANSI-последовательности для цвета"""
    if not supports_color():
        return ''
    return f'\033[38;2;{r};{g};{b}m'

def pixels_to_ascii(image, chars, invert=False, colored=False):
    if colored and not supports_color():
        print("Внимание: Ваш терминал не поддерживает цвета ANSI. Будет использован черно-белый вывод.")
        colored = False
    
    if colored:
        pixels = image.convert('RGB').getdata()
    else:
        pixels = image.convert('L').getdata()
        
    if invert:
        chars = chars[::-1]
    
    ascii_pixels = []
    step = 256 / len(chars)
    
    for pixel in pixels:
        if colored:
            r, g, b = pixel
            brightness = sum([r, g, b]) / 3
            char = chars[int(brightness / step)]
            ascii_pixels.append(f"{get_ansi_color(r, g, b)}{char}")
        else:
            char = chars[int(pixel / step)]
            ascii_pixels.append(char)
            
    return ascii_pixels

def create_ascii_art(pixels, width, colored=False):
    lines = []
    for i in range(0, len(pixels), width):
        line = ''.join(pixels[i:i + width])
        if colored:
            line += '\033[0m'
        lines.append(line)
    return '\n'.join(lines)

def preview_ascii(ascii_art, max_lines=20):
    lines = ascii_art.split('\n')
    if len(lines) > max_lines:
        middle = len(lines) // 2
        start = middle - max_lines // 2
        end = start + max_lines
        return '\n'.join(lines[start:end])
    return ascii_art

def main():
    parser = argparse.ArgumentParser(description='Конвертер изображений в ASCII-арт')
    parser.add_argument('image', help='Путь к входному изображению')
    parser.add_argument('--width', type=int, default=80, help='Ширина ASCII-арта')
    parser.add_argument('--height', type=int, help='Высота ASCII-арта (опционально)')
    parser.add_argument('--invert', action='store_true', help='Инвертировать цвета')
    parser.add_argument('--output', help='Файл для сохранения результата')
    parser.add_argument('--ascii-set', choices=ASCII_SETS.keys(), default='default',
                      help='Выбор набора ASCII символов')
    parser.add_argument('--brightness', type=float, default=1.0,
                      help='Настройка яркости (0.0-2.0)')
    parser.add_argument('--contrast', type=float, default=1.0,
                      help='Настройка контрастности (0.0-2.0)')
    parser.add_argument('--color', action='store_true',
                      help='Сохранить цветовую информацию (только для терминалов с поддержкой ANSI)')
    parser.add_argument('--preview', action='store_true',
                      help='Показать предпросмотр в консоли')
    
    args = parser.parse_args()

    # Проверка поддержки цвета если запрошен цветной вывод
    if args.color and not supports_color():
        print("Предупреждение: Ваш терминал не поддерживает цвета ANSI.")
        print("Цветной вывод будет отключен.")
        args.color = False

    try:
        image = Image.open(args.image)
    except Exception as e:
        print(f'Ошибка открытия изображения: {e}')
        return

    # Обработка изображения
    image = resize_image(image, args.width, args.height)
    image = adjust_image(image, args.brightness, args.contrast)
    
    # Генерация ASCII
    chars = ASCII_SETS[args.ascii_set]
    ascii_pixels = pixels_to_ascii(image, chars, args.invert, args.color)
    ascii_art = create_ascii_art(ascii_pixels, args.width, args.color)

    # Вывод результата
    if args.preview:
        preview = preview_ascii(ascii_art)
        print("Предпросмотр:")
        print(preview)
        if args.output:
            response = input("\nСохранить полную версию? (y/n): ")
            if response.lower() != 'y':
                return

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(ascii_art)
        print(f'ASCII-арт сохранен в {args.output}')
    else:
        print(ascii_art)

if __name__ == '__main__':
    main()