from typing import List, Dict, Tuple, Union
import numpy
from numpy import uint8
from PIL import Image, ImageFont, ImageDraw
import imageio
import mss

# https://stackoverflow.com/questions/36384353/generate-pixel-matrices-from-characters-in-string
# https://stackoverflow.com/questions/9632995/how-to-easily-print-ascii-art-text/27753869#27753869
def generate_pixel_num(format_text: str) -> Union[List[str], Tuple[int, int]]:
    font = ImageFont.truetype('Arial Unicode.ttf', 15) #load the font # TODO what is a stable font to use?
    size = font.getbbox(format_text)[-2:]  #calc the size of text in pixels

    image = Image.new('1', size, 1)  #create a b/w image
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), format_text, font=font) #render the text to the bitmap

    nparray = numpy.asarray(image)
    nparray = nparray[~numpy.all(nparray == 1, axis=1)] # remove all rows with no visible pixels

    color_array = numpy.full((*nparray.shape, 3), (0, 0, 0), dtype=uint8)
    color_array[~nparray] = (255, 255, 255)

    return color_array, color_array.shape

def draw_monitor(image_info: Tuple[int, Dict[str, int]], shifted_left: int, shifted_top: int, dec_size: int, image) -> numpy.array:
    
    image_height: int = int(image_info[1]['height'] / dec_size)
    image_width: int = int(image_info[1]['width'] / dec_size)
    # get the four side positions
    new_top = int((image_info[1]['top'] + shifted_top) / dec_size)
    new_left = int((image_info[1]['left'] + shifted_left) / dec_size)
    new_right = new_left + image_width
    new_bottom = new_top + image_height

    # top horizontal border
    image[new_top, new_left:new_right] = numpy.full((image_width, 3), (0xFF, 0xFF, 0xFF), dtype=numpy.uint8)
    # bottom horizontal border
    image[new_bottom-1, new_left:new_right] = numpy.full((image_width, 3), (0xFF, 0xFF, 0xFF), dtype=numpy.uint8)
    # left vertical border
    image[new_top:new_bottom, new_left] = numpy.full((image_height, 3), (0xFF, 0xFF, 0xFF), dtype=numpy.uint8)
    # right vertical border
    image[new_top:new_bottom, new_right-1] = numpy.full((image_height, 3), (0xFF, 0xFF, 0xFF), dtype=numpy.uint8)

    # drawing the monitor number in the box
    midpoint_vertical: int = new_top + int(image_height / 2)
    midpoint_horizontal: int = new_left + int(image_width / 2)
    #ShowText = '1' # TODO REMOVE

    num_image, num_size = generate_pixel_num(str(image_info[0]))
    # position of pixels to replace (midpoint of box overlap) with odd (extra) pixels going down and to the right
    image[midpoint_vertical - int(num_size[0]/2):midpoint_vertical + int(round(num_size[0]/2)), midpoint_horizontal - int(num_size[1]/2):midpoint_horizontal + int(round(num_size[1]/2))] = num_image

    return image

# monitor positions
''' how monitors should be categorized
-left = left
+left = right
-top = top
top = 0 = bottom
'''
def order_monitors() -> List[List[Tuple[int, Dict[str, int]]]]:
    # generate 2D list of monitors
    with mss.mss() as sct:
        # example: [('monitor number', {'monitor info'})]
        monitors: List[Tuple[int, Dict[str, int]]] = [(i + 1, item) for i,item in enumerate(sct.monitors[1:])]

    # 0,0 is always main screen
    # organize by height then by left to right
    monitors = sorted(monitors, key=lambda x: x[1]['top'])
    rows, column = [], []
    for index, item in enumerate(monitors):
        if not column or item[1]['top'] == column[0][1]['top']:
            column.append(item)
        else:
            rows.append(sorted(column, key=lambda x: x[1]['left']))
            column = []
            column.append(item)
        if index == len(monitors) - 1: # adding the last row
            if column[-1] != item: # for when there are multiple monitors on the bottom
                column.append(item)
            rows.append(sorted(column, key=lambda x: x[1]['left']))
    
    return rows

def main() -> str:
    with mss.mss() as sct:
        # example: [('monitor number', {'monitor info'})]
        total_area: Dict[str, int] = sct.monitors[0]

    # since list of list start at (0,0) and go left to right and then down -- just shift each left and top into their respective non-negative values and generate image from there
    shifted_left: int = -total_area['left']
    shifted_top: int = -total_area['top']
    SIZE_REDUCTION: int = 10 # to speed up image generation and reduce image for usage in rumps
    total_height: int = int(total_area['height'] / SIZE_REDUCTION)
    total_width: int = int(total_area['width'] / SIZE_REDUCTION)

    # https://discuss.python.org/t/create-png-image-from-coordinates/16691
    # setup display 'coverage'
    image = numpy.zeros((total_height, total_width, 3), dtype=numpy.uint8)

    for rows in order_monitors():
        for monitor in rows:
            image = draw_monitor(monitor, shifted_left, shifted_top, SIZE_REDUCTION, image)

    file_name: str = 'test_num_output.png'
    imageio.imwrite(file_name, image) # TODO fix filename
    #print(image)
    return file_name


if __name__ == '__main__':
    main()