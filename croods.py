import PIL as p
import fitz

path = "Clean_Document.pdf"

document = fitz.open(path)


def margin_is_empty_nic(pix_map):
    coords = []
    pxw = pix_map.width
    pxh = pix_map.height

    area = pxw * pxh

    for x in range(pxw):
        for y in range(pxh):
            pixel = pix_map.pixel(x, y)
            if pixel != (255, 255, 255):
                coords.append((x, y))
    print("coord length: ", len(coords))
    print("3% of area: ", (0.03 * area))

    return True if len(coords) < (0.03 * area) else False


def margins_passed(pdf_file):
    inch = 72

    for page in pdf_file:
        p_width = page.rect.width
        p_height = page.rect.height

        r_header = fitz.Rect(0, 0, p_width, inch)
        r_footer = fitz.Rect(0, p_height - inch, p_width, p_height)
        r_left = fitz.Rect(0, 0, inch, p_height)
        r_right = fitz.Rect(p_width - inch, 0, p_width, p_height)

        header = page.get_pixmap(clip=r_header)
        footer = page.get_pixmap(clip=r_footer)
        left = page.get_pixmap(clip=r_left)
        right = page.get_pixmap(clip=r_right)

        margins = [header, footer, left, right]

        # for i in range(len(margins)):
        #     margins[i].save(f'margin-{i}.png')

        for margin in margins:
            if not margin_is_empty_nic(margin):
                return False
    return True


print(margins_passed(document))
