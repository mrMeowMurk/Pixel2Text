from PIL import Image
import argparse

# Градации яркости от темного к светлому
ASCII_CHARS = '@%#*+=-:. '

def resize_image(image, new_width=80):
    width, height = image.size
    ratio = height / width / 1.65  # Учитываем пропорции символов
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def image_to_grayscale(image):
    return image.convert('L')

def pixels_to_ascii(image, invert=False):
    pixels = image.getdata()
    chars = list(ASCII_CHARS)
    
    if invert:
        chars = chars[::-1]  # Инвертируем градации
    
    step = 256 / len(chars)
    return ''.join([chars[int(pixel / step)] for pixel in pixels])

def main():
    parser = argparse.ArgumentParser(description='Конвертер изображений в ASCII-арт')
    parser.add_argument('image', help='Путь к входному изображению')
    parser.add_argument('--width', type=int, default=80, help='Ширина ASCII-арта')
    parser.add_argument('--invert', action='store_true', help='Инвертировать цвета')
    parser.add_argument('--output', help='Файл для сохранения результата')
    args = parser.parse_args()

    try:
        image = Image.open(args.image)
    except Exception as e:
        print(f'Ошибка открытия изображения: {e}')
        return

    # Обработка изображения
    image = resize_image(image, args.width)
    image = image_to_grayscale(image)
    
    # Генерация ASCII
    ascii_art = pixels_to_ascii(image, args.invert)
    pixel_count = len(ascii_art)
    ascii_art = '\n'.join(
        [ascii_art[index:(index + args.width)] 
        for index in range(0, pixel_count, args.width)]
    )

    # Вывод результата
    if args.output:
        with open(args.output, 'w') as f:
            f.write(ascii_art)
        print(f'ASCII-арт сохранен в {args.output}')
    else:
        print(ascii_art)

if __name__ == '__main__':
    main()