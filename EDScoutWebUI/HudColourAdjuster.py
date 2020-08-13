import xml.etree.ElementTree as ET


config_file = r"C:\Users\Jon\AppData\Local\Frontier Developments\Elite Dangerous\Options\Graphics\GraphicsConfigurationOverride.xml"

#Todo:
#* Read the above
#* Make the adjustments: https://developer.mozilla.org/en-US/docs/Web/SVG/Element/feColorMatrix
#* read the current .css file
#* Replace all the colours into a new .css file

# Worked out the transform from here:
# https://arkku.com/elite/hud_editor/
# https://developer.mozilla.org/en-US/docs/Web/SVG/Element/feColorMatrix



def get_matrix_values(config_file):
    matrix_values = None
    tree = ET.parse(config_file)
    root = tree.getroot()

    vals = {}
    for element in root.findall("./GUIColour/Default/"):
        if 'Matrix' in element.tag:
            vals[element.tag] = [int(x) for x in element.text.strip().split(',')]

    return vals