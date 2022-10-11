from PIL import Image


def change_bit(text: str, index: int, val: int) -> int:
    """
    Function that changes last bit in r,g or b value
    :param text: string to be encoded
    :param index: index in text to be checked
    :param val: int value of r,g or b
    :return: edited value of r,g or b
    """
    if text[index] == "0":
        val = val & ~1
    else:
        val = val | 1

    return val


def encode_text(input_image: Image, text: str) -> Image:
    """
    Function that encodes text to image
    :param input_image: input_image in which the text is encoded
    :param text: text to be encoded - already transformed to bites
    :return: Image
    """
    changed = 0

    for x in range(input_image.width):
        for y in range(input_image.height):
            r, g, b = input_image.getpixel((x, y))

            # change r
            r = change_bit(text, changed, r)
            changed += 1

            if changed >= len(text):
                input_image.putpixel((x, y), (r, g, b))
                break

            # change g
            g = change_bit(text, changed, g)
            changed += 1

            if changed >= len(text):
                input_image.putpixel((x, y), (r, g, b))
                break

            # change b
            b = change_bit(text, changed, b)
            changed += 1

            if changed >= len(text):
                input_image.putpixel((x, y), (r, g, b))
                break

            input_image.putpixel((x, y), (r, g, b))

        if changed >= len(text):
            break

    return input_image


def encode_file():
    pass


def decode_text():
    pass


def decode_file():
    pass


def detect_steganography():
    pass


def check_text_input_length(text_input: str, max_bits: int):
    """
    Function that checks if text input length can be encoded to the picture
    :param text_input: string that user wants to encode
    :param max_bits: size of image in bits
    :return:
    """
    text_input_length = len(text_input) * 8

    if text_input_length > max_bits:
        print('Text is too big')
        exit(3)


def convert_text(text: str) -> str:
    """
    Converts text to string of bits
    :param text: text to be converted
    :return: converted string
    """
    res = ''.join(format(ord(i), '08b') for i in text)
    return str(res)


def get_header():
    return ""


def main():
    text_input = input('What text do you want to encode?\n')
    file_input = input('In what file do you want to encode it?\n')

    try:
        image = Image.open(file_input)
    except FileNotFoundError:
        print('File does not exists\n')
        exit(2)

    file_output = input('What should be the output file name?(without extension)\n')
    max_bits = image.width * image.height * 3
    check_text_input_length(text_input, max_bits)
    text_input_binary = convert_text(text_input)
    changed_image = encode_text(image, text_input_binary)
    changed_image.save(file_output+".jpeg")


if __name__ == '__main__':
    main()
