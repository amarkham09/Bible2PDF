import argparse, os
from sys import exit

from meaningless import WebExtractor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.flowables import BalancedColumns
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, A3

# Defaults
LEFT_MARGIN = 20
RIGHT_MARGIN = 20
TOP_MARGIN = 10
BOTTOM_MARGIN = 10
NUM_COLUMNS = 1
COL_PADDING = 50
FONT_SIZE = 11
LINE_SPACING = 1.5
PORTRAIT_ORIENTATION = True
PRINT_ON_A3 = False

VALID_REF = 'Bible reference in format "Book W:X-Y:Z" or "Book W:X-Z" or "Book W-Y:Z" or "Book W-Y" or "Book W", ' \
            'where Z can optionally be "end". '

def getText(book_name, ch_from, v_from, ch_to, v_to, version='ESVUK', bible=None):
    if bible is None or not isinstance(bible, WebExtractor):
        bible = WebExtractor(translation=version)
    if v_to.lower() == 'end':
        v_to = 200
    return bible.get_passage_range(book_name, ch_from, v_from, ch_to, v_to)


def createDocument(bible_text, path, left_margin=LEFT_MARGIN, right_margin=RIGHT_MARGIN, top_margin=TOP_MARGIN,
                   bottom_margin=BOTTOM_MARGIN, num_columns=NUM_COLUMNS,
                   col_padding=COL_PADDING,
                   font_size=FONT_SIZE, line_spacing=LINE_SPACING, portrait_orientation=PORTRAIT_ORIENTATION,
                   print_on_A3=PRINT_ON_A3):
    paragraphs = bible_text.split('\n')
    # registering a external font in python
    pdfmetrics.registerFont(TTFont('Alegreya Sans', 'AlegreyaSans-Regular.ttf'))

    style = ParagraphStyle(name='BodyText', alignment=4, fontName='Alegreya Sans', fontSize=font_size,
                           leading=font_size * line_spacing)
    indent_style = ParagraphStyle(name='IndentedBodyText', parent=style, leftIndent=15)

    if print_on_A3:
        paper_size = A3
    else:
        paper_size = A4
    if not portrait_orientation:
        paper_size = paper_size[-1:-3:-1]

    doc = SimpleDocTemplate(path, pagesize=paper_size, leftMargin=left_margin,
                            rightMargin=right_margin,
                            topMargin=top_margin, bottomMargin=bottom_margin)
    flowables = []

    for paragraph_text in paragraphs:
        if paragraph_text[0:4] == ' ' * 4:
            paragraph = Paragraph(paragraph_text, indent_style)
        else:
            paragraph = Paragraph(paragraph_text, style)
        flowables.append(paragraph)
    if num_columns > 1:
        story = [BalancedColumns(flowables, nCols=num_columns, innerPadding=col_padding)]
    else:
        story = flowables
    doc.build(story)


def cancel():
    print(
        f'Please enter {VALID_REF}')
    exit()


def fileName(bible_book, ch_start, v_start, ch_end, v_end):
    with open(f'{os.path.dirname(__file__)}/write_loc.txt', 'r') as f:
        path = f.read()

    if v_start == 1 and v_end == 'end':
        if ch_start == ch_end:
            return f'{path}{bible_book} {ch_start}.pdf'
        else:
            return f'{path}{bible_book} {ch_start}–{ch_end}.pdf'
    else:
        if ch_start == ch_end:
            return f'{path}{bible_book} {ch_start}.{v_start}–{v_end}.pdf'
        else:
            return f'{path}{bible_book} {ch_start}.{v_start}–{ch_end}.{v_end}.pdf'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ref',
                        help=VALID_REF)
    parser.add_argument('-lm', '--left_margin', default=LEFT_MARGIN, type=int,
                        help=f'Size of left margin in pixels (default {LEFT_MARGIN}).')
    parser.add_argument('-rm', '--right_margin', default=RIGHT_MARGIN, type=int,
                        help=f'Size of right margin in pixels (default {RIGHT_MARGIN}).')
    parser.add_argument('-tm', '--top_margin', default=TOP_MARGIN, type=int,
                        help=f'Size of top margin in pixels (default {TOP_MARGIN}).')
    parser.add_argument('-bm', '--bottom_margin', default=BOTTOM_MARGIN, type=int,
                        help=f'Size of bottom margin in pixels (default {BOTTOM_MARGIN}).')
    parser.add_argument('-c', '--num_columns', default=NUM_COLUMNS, type=int,
                        help=f'Number of columns (default {NUM_COLUMNS}).')
    parser.add_argument('-cp', '--col_padding', default=COL_PADDING, type=int,
                        help=f'Column inner padding if multiple columns (default {COL_PADDING}).')
    parser.add_argument('-f', '--font_size', default=FONT_SIZE, type=int,
                        help=f'Font size in pt (default {FONT_SIZE}).')
    parser.add_argument('-s', '--line_spacing', default=LINE_SPACING, type=float,
                        help=f'Line spacing multiplier compared with font size (default {LINE_SPACING}).')

    orientation = parser.add_mutually_exclusive_group()
    orientation.add_argument('-p', '--portrait', action='store_true',
                             help=f'Set page orientation to portrait (default {PORTRAIT_ORIENTATION}).')
    orientation.add_argument('-l', '--landscape', action='store_true',
                             help=f'Set page orientation to landscape (default {not PORTRAIT_ORIENTATION}).')

    paper = parser.add_mutually_exclusive_group()
    paper.add_argument('-a3', action='store_true', help=f'Set page size to A3 (default {PRINT_ON_A3}).')
    paper.add_argument('-a4', action='store_true', help=f'Set page size to A4 (default {not PRINT_ON_A3}).')
    args = parser.parse_args()

    # ref must be in format "Book W:X-Y:Z" or "Book W:X-Z" or "Book W-Y:Z" or "Book W-Y" or "Book W",
    # where Z can optionally be "end"
    book, verses, end_ref, start_ref = '', '', '', ''
    # error check each of these, allow multiple forms of input
    try:
        book, verses = args.ref.split()
    except ValueError:
        split_values = args.ref.split()
        if len(split_values) == 3:
            book = ' '.join(split_values[0:2])
            verses = split_values[2]
        else:
            cancel()

    try:
        start, end = verses.split('-')
        start_ref = start.split(':')
        end_ref = end.split(':')
    except ValueError:
        if verses.isnumeric():  # If entered in format "Book W"
            start_ref, end_ref = [verses, 1], [verses, 'end']
        else:
            cancel()

    if len(end_ref) == 1:
        if len(start_ref) == 1:  # If entered in format "Book W-Y"
            start_ref, end_ref = [start_ref[0], 1], [end_ref[0], 'end']
        else:  # If entered in format "Book W:X-Z"
            start_ref, end_ref = start_ref, [start_ref[0], end_ref[0]]
    else:
        if len(start_ref) == 1:  # If entered in format "Book W-Y:Z"
            start_ref, end_ref = [start_ref[0], 1], end_ref

    # If execution reaches here, start_ref and end_ref should be lists of length 2
    text = getText(book, *start_ref, *end_ref)
    file_name = fileName(book, *start_ref, *end_ref)
    if args.portrait:
        print_portrait = True
    elif args.landscape:
        print_portrait = False
    else:
        print_portrait = PORTRAIT_ORIENTATION
    if args.a3:
        print_on_a3 = True
    elif args.a4:
        print_on_a3 = False
    else:
        print_on_a3 = PRINT_ON_A3

    createDocument(bible_text=text, path=file_name, left_margin=args.left_margin, right_margin=args.right_margin,
                   top_margin=args.top_margin, bottom_margin=args.bottom_margin, num_columns=args.num_columns,
                   col_padding=args.col_padding, font_size=args.font_size, line_spacing=args.line_spacing,
                   portrait_orientation=print_portrait, print_on_A3=print_on_a3)
