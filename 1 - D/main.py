from PIL import Image, ImageDraw
from random import randint

im = Image.new("RGB", (700, 700), (0, 0, 0))
draw = ImageDraw.Draw(im)
count = randint(1, 20)
circles = []
for i in range(count):
    x = randint(0, 9)
    y = randint(0, 9)
    circles.append((x, y))
    draw.ellipse((x * 70 + 20, y * 70 + 20, x * 70 + 50, y * 70 + 50), fill='red')
for x in range(10):
    for y in range(10):
        min_dist = 1000000000
        for c in circles:
            if ((x * 70 + 35) - (c[0] * 70 + 35)) ** 2 + ((y * 70 + 35) - (c[1] * 70 + 35)) ** 2 < min_dist:
                min_dist = ((x * 70 + 35) - (c[0] * 70 + 35)) ** 2 + ((y * 70 + 35) - (c[1] * 70 + 35)) ** 2
                min_x = c[0]
                min_y = c[1]
        if min_dist != 0:
            if y == min_y and x != min_x:
                x_first = (x * 70 + 20)
                x_second = (x * 70 + 50)
                draw.line((x_first, y * 70 + 35, x_second, y * 70 + 35), fill='white', width=2)
                if x < min_x:
                    draw.ellipse((x_second - 2, y * 70 + 33, x_second + 2, y * 70 + 37), fill='yellow')
                else:
                    draw.ellipse((x_first - 2, y * 70 + 33, x_first + 2, y * 70 + 37), fill='yellow')
            elif y != min_y and x == min_x:
                y_first = (y * 70 + 20)
                y_second = (y * 70 + 50)
                draw.line((x * 70 + 35, y_first, x * 70 + 35, y_second), fill='white', width=2)
                if y < min_y:
                    draw.ellipse((x * 70 + 33, y_second - 2, x * 70 + 37, y_second + 2), fill='yellow')
                else:
                    draw.ellipse((x * 70 + 33, y_first - 2, x * 70 + 37, y_first + 2), fill='yellow')
            else:
                y_first = y * 70 + 20
                y_second = y * 70 + 50
                x_first = ((y_first - (min_y * 70 + 35)) / ((y * 70 + 35) - (min_y * 70 + 35))) * \
                          ((x * 70 + 35) - (min_x * 70 + 35)) + (min_x * 70 + 35)
                x_second = ((y_second - (min_y * 70 + 35)) / ((y * 70 + 35) - (min_y * 70 + 35))) * \
                           ((x * 70 + 35) - (min_x * 70 + 35)) + (min_x * 70 + 35)
                if x_first < (x * 70 + 20):
                    x_first = x * 70 + 20
                    y_first = ((x_first - (min_x * 70 + 35)) / ((x * 70 + 35) - (min_x * 70 + 35))) * \
                              ((y * 70 + 35) - (min_y * 70 + 35)) + (min_y * 70 + 35)
                if x_second < (x * 70 + 20):
                    x_second = x * 70 + 20
                    y_second = ((x_second - (min_x * 70 + 35)) / ((x * 70 + 35) - (min_x * 70 + 35))) * \
                               ((y * 70 + 35) - (min_y * 70 + 35)) + (min_y * 70 + 35)
                if x_first > (x * 70 + 50):
                    x_first = x * 70 + 50
                    y_first = ((x_first - (min_x * 70 + 35)) / ((x * 70 + 35) - (min_x * 70 + 35))) * \
                              ((y * 70 + 35) - (min_y * 70 + 35)) + (min_y * 70 + 35)
                if x_second > (x * 70 + 50):
                    x_second = x * 70 + 50
                    y_second = ((x_second - (min_x * 70 + 35)) / ((x * 70 + 35) - (min_x * 70 + 35))) * \
                               ((y * 70 + 35) - (min_y * 70 + 35)) + (min_y * 70 + 35)
                draw.line((x_first, y_first, x_second, y_second), fill='white', width=2)
                if y < min_y:
                    draw.ellipse((x_second - 2, y_second - 2, x_second + 2, y_second + 2), fill='yellow')
                else:
                    draw.ellipse((x_first - 2, y_first - 2, x_first + 2, y_first + 2), fill='yellow')


im.show()
