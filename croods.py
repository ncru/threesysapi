import PIL as p
import fitz


# def margin_is_empty_nic(pix_map):
#     coords = []
#     pxw = pix_map.width
#     pxh = pix_map.height

#     area = pxw * pxh

#     for x in range(pxw):
#         for y in range(pxh):
#             pixel = pix_map.pixel(x, y)
#             if pixel != (255, 255, 255):
#                 coords.append((x, y))
#     print("coord length: ", len(coords))
#     print("3% of area: ", (0.03 * area))

#     return True if len(coords) < (0.03 * area) else False


# def margins_passed(pdf_file):
#     inch = 72

#     for page in pdf_file:
#         p_width = page.rect.width
#         p_height = page.rect.height

#         r_header = fitz.Rect(0, 0, p_width, inch)
#         r_footer = fitz.Rect(0, p_height - inch, p_width, p_height)
#         r_left = fitz.Rect(0, 0, inch, p_height)
#         r_right = fitz.Rect(p_width - inch, 0, p_width, p_height)

#         header = page.get_pixmap(clip=r_header)
#         footer = page.get_pixmap(clip=r_footer)
#         left = page.get_pixmap(clip=r_left)
#         right = page.get_pixmap(clip=r_right)

#         margins = [header, footer, left, right]

#         # for i in range(len(margins)):
#         #     margins[i].save(f'margin-{i}.png')

#         for margin in margins:
#             if not margin_is_empty_nic(margin):
#                 return False
#     return True


def check_specific_margin_area(pix_map, dm_location, x_threshold, y_threshold):
    coords = []
    pix_width = pix_map.width
    pix_height = pix_map.height
    for x in range(pix_width):
        for y in range(pix_height):
            pixel = pix_map.pixel(x, y)
            if pixel != (255, 255, 255):
                match dm_location:
                    case 'top-left':
                        if x <= x_threshold and y <= y_threshold:
                            coords.append((x, y))
                    case 'top-right':
                        if x >= x_threshold and y <= y_threshold:
                            coords.append((x, y))
                    case 'bottom-left':
                        if x <= x_threshold and y >= y_threshold:
                            coords.append((x, y))
                    case 'bottom-right':
                        if x >= x_threshold and y >= y_threshold:
                            coords.append((x, y))
    return True if len(coords) == 0 else False


def margin_is_empty(pix_map, dm_location):
    allowance = 3
    dm_width = 72 - (2 * allowance)
    pix_width = pix_map.width
    pix_height = pix_map.height
    padded_dm = dm_width + (2 * allowance)
    match dm_location:
        case 'top-left':
            x_threshold = padded_dm
            y_threshold = padded_dm
        case 'top-right':
            x_threshold = pix_width - padded_dm
            y_threshold = padded_dm
        case 'bottom-left':
            x_threshold = padded_dm
            y_threshold = pix_height - padded_dm
        case 'bottom-right':
            x_threshold = pix_width - padded_dm
            y_threshold = pix_height - padded_dm

    return check_specific_margin_area(pix_map, dm_location, x_threshold, y_threshold)


def margins_passed(pdf_file, dm_location):
    inch = 72

    # for page in pdf_file:
    page = pdf_file[0]
    p_width = page.rect.width
    p_height = page.rect.height

    r_header = fitz.Rect(0, 0, p_width, inch)
    r_footer = fitz.Rect(0, p_height - inch, p_width, p_height)
    r_left = fitz.Rect(0, 0, inch, p_height)
    r_right = fitz.Rect(p_width - inch, 0, p_width, p_height)

    header = page.get_pixmap(clip=r_header)
    footer = page.get_pixmap(clip=r_footer)
    # left = page.get_pixmap(clip=r_left)
    # right = page.get_pixmap(clip=r_right)

    # for i in range(len(margins)):
    #     margins[i].save(f'margin-{i}.png')

    match dm_location:
        case 'top-left':
            return margin_is_empty(header, dm_location)
        case 'top-right':
            return margin_is_empty(header, dm_location)
        case 'bottom-left':
            return margin_is_empty(footer, dm_location)
        case 'bottom-right':
            return margin_is_empty(footer, dm_location)


bl_clean = fitz.open('./margin_testers/bl_clean.pdf')
br_clean = fitz.open('./margin_testers/br_clean.pdf')
tl_clean = fitz.open('./margin_testers/tl_clean.pdf')
tr_clean = fitz.open('./margin_testers/tr_clean.pdf')
dirty = fitz.open('./margin_testers/dirty.pdf')

print(margins_passed(tr_clean, 'top-right'))
print(margins_passed(dirty, 'top-right'))
