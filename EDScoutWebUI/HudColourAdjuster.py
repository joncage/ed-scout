import xml.etree.ElementTree as ET
import re


default_config_file = r"C:\Users\Jon\AppData\Local\Frontier Developments\Elite Dangerous\Options\Graphics\GraphicsConfigurationOverride.xml"

#Todo:
#* Read the above
#* Make the adjustments: https://developer.mozilla.org/en-US/docs/Web/SVG/Element/feColorMatrix
#* read the current .css file
#* Replace all the colours into a new .css file

# Worked out the transform from here:
# https://arkku.com/elite/hud_editor/
# https://developer.mozilla.org/en-US/docs/Web/SVG/Element/feColorMatrix


def get_matrix_values(config_file=default_config_file):
    matrix_values = None
    tree = ET.parse(config_file)
    root = tree.getroot()

    vals = {}
    for element in root.findall("./GUIColour/Default/"):
        if 'Matrix' in element.tag:
            vals[element.tag] = [float(x) for x in element.text.strip().split(',')]
    return vals


def clamp_value(value):
    return max(min(value, 1.0), 0.0)


def adjust_colours(original_rgb, colour_matrix):
    # New red = [r1 * old red] + [r2 * old green] + [r3 * old Blue]

    new_red = colour_matrix['MatrixRed'][0]*original_rgb[0] + \
              colour_matrix['MatrixGreen'][0]*original_rgb[1] + \
              colour_matrix['MatrixBlue'][0]*original_rgb[2]
    new_green = colour_matrix['MatrixRed'][1]*original_rgb[0] + \
              colour_matrix['MatrixGreen'][1]*original_rgb[1] + \
              colour_matrix['MatrixBlue'][1]*original_rgb[2]
    new_blue = colour_matrix['MatrixRed'][2]*original_rgb[0] + \
              colour_matrix['MatrixGreen'][2]*original_rgb[1] + \
              colour_matrix['MatrixBlue'][2]*original_rgb[2]

    return [clamp_value(new_red), clamp_value(new_green), clamp_value(new_blue)]


def hex_colour_shift(original_hex, colour_matrix):
    max_colour_val = 255.0

    red = int(original_hex[1:3], 16)/max_colour_val
    green = int(original_hex[3:5], 16)/max_colour_val
    blue = int(original_hex[5:7], 16)/max_colour_val

    rgb_in = [red, green, blue]

    adjusted = adjust_colours(rgb_in, colour_matrix)

    new_red = "%0.2X" % int(adjusted[0]*max_colour_val)
    new_green = "%0.2X" % int(adjusted[1]*max_colour_val)
    new_blue = "%0.2X" % int(adjusted[2]*max_colour_val)

    return f'#{new_red}{new_green}{new_blue}'


def remap_styles(data_to_remap, colour_matrix):

    return re.sub('(#[A-Za-z0-9]{6})', lambda m: hex_colour_shift(m.group(), colour_matrix), data_to_remap)


def remap_style_file(original_file_name, colour_matrix, new_file_name):

    with open(original_file_name, "r") as input:
        css_content = input.read()

    remapped = remap_styles(css_content, colour_matrix)

    with open(new_file_name, "w") as output:
        output.write(remapped)

