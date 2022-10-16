from PIL import Image
from os.path import exists
from os import stat
import numpy
import math
from textwrap import wrap

HEADER_SIZE = 580


def change_bit(bit: int, val: int) -> int:
    """
    Function that changes last bit in r,g or b value
    :param bit: int to be encoded
    :param val: int value of r,g or b
    :return: edited value of r,g or b
    """
    return val & ~1 if bit == 0 else val | 1


def encode_loop(input_image: Image, bits_data: list, header_l: list, enc_type: int) -> Image:
    """
    Function that loops through every pixel of image and puts new bits to LSB
    :param header_l:
    :param input_image: input_image in which the data are encoded
    :param bits_data: data of bits (either string of bits or array of bits)
    :return: Image
    """

    next_bit = None
    header_l.extend(bits_data)
    data = iter(header_l)
    counter = 0
    counter_bits = 0

    for x in range(input_image.width):
        for y in range(input_image.height):
            if enc_type == 0 \
                    or (enc_type == 1 and counter % 2 == 0) \
                    or counter_bits < HEADER_SIZE:
                pixels = list(input_image.getpixel((x, y)))

                next_bit = next(data, None)
                if next_bit is not None:
                    # change r
                    pixels[0] = change_bit(int(next_bit), pixels[0])
                    counter_bits += 1
                else:
                    input_image.putpixel((x, y), tuple(pixels))
                    break

                if counter_bits == HEADER_SIZE:
                    counter_bits += 1
                    counter += 1
                    continue

                next_bit = next(data, None)
                if next_bit is not None:
                    # change g
                    pixels[1] = change_bit(int(next_bit), pixels[1])
                    counter_bits += 1
                else:
                    input_image.putpixel((x, y), tuple(pixels))
                    break

                if counter_bits == HEADER_SIZE:
                    counter_bits += 1
                    counter += 1
                    continue

                next_bit = next(data, None)
                if next_bit is not None:
                    # change b
                    pixels[2] = change_bit(int(next_bit), pixels[2])
                    counter_bits += 1
                else:
                    input_image.putpixel((x, y), tuple(pixels))
                    break

                input_image.putpixel((x, y), tuple(pixels))
            counter += 1

        if next_bit is None:
            break

    return input_image


def encode(user_input: str, image: Image, header: str, enc_type: int) -> Image:
    """
    Function to encode
    :param user_input: user input string
    :param image: Image
    :param header:
    :param: enc_type
    :return: Image
    """
    if is_file(user_input):
        # can do this as in this point I know it exist
        f_bytes = numpy.fromfile(user_input, dtype="uint8")
        f_bits = numpy.unpackbits(f_bytes)

        return encode_loop(image, list(f_bits), list(header), enc_type)
    else:
        return encode_loop(image, list(convert_text_to_bits(user_input)), list(header), enc_type)


def convert_text_to_bits(text: str) -> str:
    """
    Converts text to string of bits
    :param text: text to be converted
    :return: converted string
    """
    return str(''.join(format(ord(i), '08b') for i in text))


def set_header(u_input: str, enc_type: int) -> str:
    """
    Function that sets header info
    :param u_input:
    :param enc_type:
    :return: str
    """
    if is_file(u_input):
        file_type = '1'  # file
        file_stats = stat(u_input)
        # get file size in bits
        size_bits = file_stats.st_size * 8 + HEADER_SIZE if enc_type == 0 else file_stats.st_size * 8 * 2 + HEADER_SIZE
    else:
        file_type = '0'  # text
        size_bits = len(u_input) * 8 + HEADER_SIZE if enc_type == 0 else len(u_input) * 8 * 2 + HEADER_SIZE

    # max length of file name to store
    if len(u_input) > 64:
        print('File name to store is too long. \n')
        exit(2)
    else:
        if is_file(u_input):
            file_name = convert_text_to_bits(u_input)
        else:
            file_name = '0'

        k = 512 - len(file_name)
        file_name = file_name.rjust(k + len(file_name), '0')

    enc_start = str(bin(HEADER_SIZE + 1)).replace('b', '')
    k = 32 - len(enc_start)
    enc_start = enc_start.rjust(k + len(enc_start), '0')
    enc_end = str(bin(size_bits)).replace('b', '')
    k = 32 - len(enc_end)

    if len(enc_end) > 32:
        print('Program does not allow this big encryption.\n')
        exit(42)

    enc_end = enc_end.rjust(k + len(enc_end), '0')

    enc_type = str(bin(enc_type)).replace('b', '')
    k = 3 - len(enc_type)
    enc_type = enc_type.rjust(k + len(enc_type), '0')

    return file_type + enc_type + file_name + enc_start + enc_end


def is_image_big_enough(file_size: int, image_size: int, enc_type: int) -> bool:
    """
    Function that checks if file/text size is bigger than image available size
    :param file_size:
    :param image_size:
    :param enc_type:
    :return: bool
    """
    return file_size < image_size if enc_type == 0 else file_size * 2 < image_size


def validate_and_get_size(u_input: str) -> int:
    """
    File that validates user input and returns it size in bits
    :param u_input: user input
    :return: int size in bits
    """
    size = 0
    # if it is file (not checking png for now)
    if '.jpg' in u_input or '.jpeg' in u_input or '.txt' in u_input:
        if exists(u_input):
            file_stats = stat(u_input)
            # get file size in bits
            size = file_stats.st_size * 8 + HEADER_SIZE
        else:
            print('File which you want to encode does not exist.\n')
            exit(2)
    else:
        # get text input size in bits
        size = len(u_input) * 8 + HEADER_SIZE

    return size


def resize_image(init_image: Image, resize_r: float) -> Image:
    """
    Function that resizes image
    :param init_image: image to encode in
    :param resize_r: resize ration
    :return: Image
    """
    return init_image.resize(
        (math.ceil(init_image.width * resize_r), math.ceil(init_image.height * resize_r)),
        Image.ANTIALIAS
    )


def encode_wrapper():
    encryption_data = input('What do you want to encode?\n')

    # check if it is file or string, validate if exists, get size in bits
    size_in_bits = validate_and_get_size(encryption_data)

    encryption_type = input('What type of encryption to use?\n'
                            '0. Every pixel,\n'
                            '1. Every even pixel,\n')

    header = set_header(encryption_data, int(encryption_type))

    # get image to encode in name
    image_to_encode_in = input('In what file do you want to encode it?\n')

    # try to open image
    try:
        image = Image.open(image_to_encode_in)
    except FileNotFoundError:
        print('File in which you want to encode does not exist.\n')
        exit(2)

    # image max bits to encode in
    max_bits = image.width * image.height * 3

    file_output = input('What should be the output file name?(without extension)\n')

    # check if image is big enough to encode data in it
    if is_image_big_enough(size_in_bits, max_bits, int(encryption_type)):
        changed_image = encode(encryption_data, image, header, int(encryption_type))
    else:
        print('The file/text to encode is too big. \n')
        # suggest making image bigger
        make_bigger = input('Do you want to make image to which you are encoding bigger?\n'
                            'yes/no\n')

        if make_bigger.__eq__('yes'):
            resize_ratio = size_in_bits / max_bits / 2
            resized_image = resize_image(image, resize_ratio)

            changed_image = encode(encryption_data, resized_image, header, int(encryption_type))
        else:
            exit(4)

    # save changed image - must save as png, if saving as jpeg the changed bits does not save !! why?
    changed_image.save(file_output + '.png')


def get_header(decode_image: Image):
    """
    Function that returns header from image to decode
    :param decode_image:
    :return: tuple
    """
    header_l = []
    counter = 0

    for x in range(decode_image.width):
        for y in range(decode_image.height):
            pixels = list(decode_image.getpixel((x, y)))
            if counter < HEADER_SIZE:
                header_l.append(pixels[0] & 1)
                counter += 1
            else:
                break

            if counter < HEADER_SIZE:
                header_l.append(pixels[1] & 1)
                counter += 1
            else:
                break

            if counter < HEADER_SIZE:
                header_l.append(pixels[2] & 1)
                counter += 1
            else:
                break

        if counter >= HEADER_SIZE:
            break

    f_type = header_l[0]
    enc_type = get_int_from_bits(header_l[1:4])
    file_name = get_string_from_bits_list(header_l[4:516])
    # always
    enc_start = HEADER_SIZE
    enc_end = get_int_from_bits(header_l[548:580])

    return f_type, enc_type, file_name, enc_start, enc_end


def get_string_from_bits_list(bits_l) -> str:
    """
    Function that returns string from bits list
    :param bits_l: list of bits or string of bits
    :return: str
    """
    file_name = ''
    for i in range(0, len(bits_l), 8):
        file_name += chr(get_int_from_bits(bits_l[i: i + 8]))

    return file_name


def get_int_from_bits(bits_l: list) -> int:
    """
    Function that return int from bits list
    :param bits_l: list of bits
    :return: int
    """
    return int(''.join(str(x) for x in bits_l), 2)


def decode_wrapper():
    user_input = input('What image do you want to decode?\n')

    # try to open image
    try:
        image = Image.open(user_input)
    except FileNotFoundError:
        print('File does not exist.\n')
        exit(2)

    header = get_header(image)
    enc_type = header[1]
    enc_start = header[3]
    enc_end = header[4]
    counter_bits = 0
    counter_pixels = 0
    result = ''

    for x in range(image.width):
        for y in range(image.height):
            pixels = list(image.getpixel((x, y)))

            if counter_bits >= enc_end:
                break

            if counter_bits >= enc_start and \
                    (enc_type == 0 or (enc_type == 1 and counter_pixels % 2 == 0)):
                result += str(pixels[0] & 1)

            counter_bits += 1

            if counter_bits >= enc_end:
                break

            if counter_bits >= enc_start and \
                    (enc_type == 0 or (enc_type == 1 and counter_pixels % 2 == 0)):
                result += str(pixels[1] & 1)

            counter_bits += 1

            if counter_bits >= enc_end:
                break

            if counter_bits >= enc_start and \
                    (enc_type == 0 or (enc_type == 1 and counter_pixels % 2 == 0)):
                result += str(pixels[2] & 1)

            counter_bits += 1

            if counter_bits >= enc_end:
                break

            counter_pixels += 1

        if counter_bits >= enc_end:
            break

    file_name_split = header[2].split('.')

    if header[0] == 0:
        result = wrap(result, 8)
        text = ''
        for i in result:
            text += get_string_from_bits_list(i)

        print('Encoded text is: ', format(text))
        exit(2)
    else:
        result = wrap(result, 8)
        bytes_output = []

        for i in result:
            bytes_output.append(eval("0b" + i))

        with open('test-out.' + file_name_split[1], "wb") as output_file:
            output_file.write(bytes(bytes_output))
            output_file.close()


# TODO how to find out NxN to check??
def detect_wrapper():
    user_input = input('Write image name to detect steganography in.\n')

    # try to open image
    try:
        image = Image.open(user_input)
    except FileNotFoundError:
        print('File does not exist.\n')
        exit(2)

    for x in range(image.width):
        for y in range(image.height):
            pixels = list(image.getpixel((x, y)))


def is_file(inp: str) -> bool:
    """
    Function that checks is file condition
    :param inp: user input string
    :return:  bool
    """
    return '.jpg' in inp or '.jpeg' in inp or '.txt' in inp or '.png' in inp


def main():
    what_to_do = input('What do you want to do?\n'
                       '0: Encode,\n'
                       '1: Decode,\n'
                       '2: Detect\n')
    if what_to_do == "0":
        encode_wrapper()
    elif what_to_do == "1":
        decode_wrapper()
    elif what_to_do == "2":
        detect_wrapper()
    else:
        print('Do not be an idiot.\n')
        exit(5)


if __name__ == '__main__':
    main()
