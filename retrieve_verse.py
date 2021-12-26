from meaningless import WebExtractor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.platypus.flowables import BalancedColumns
from reportlab.platypus.frames import ShowBoundaryValue
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, A3


def getText(book, ch_from, v_from, ch_to, v_to, version='ESVUK', bible=None):
    if bible is None or not isinstance(bible, WebExtractor):
        bible = WebExtractor(translation=version)
    if v_to == 'end':
        v_to = 200
    return bible.get_passage_range(book, ch_from, v_from, ch_to, v_to)


def createDocument(text, margins, font, page, file_name):
    paragraphs = text.split('\n')
    # registering a external font in python
    pdfmetrics.registerFont(TTFont('Alegreya Sans', 'AlegreyaSans-Regular.ttf'))

    style = ParagraphStyle(name='BodyText', fontName='Alegreya Sans', fontSize=font['size'],
                           leading=font['size'] * font['line_spacing'])
    indent_style = ParagraphStyle(name='IndentedBodyText', parent=style, leftIndent=15)

    if page['print_on_A3']:
        paper_size = A3
    else:
        paper_size = A4
    if not page['portrait_orientation']:
        paper_size = paper_size[-1:-3:-1]

    doc = SimpleDocTemplate(file_name, pagesize=paper_size, leftMargin=margins['left_margin'],
                            rightMargin=margins['right_margin'],
                            topMargin=margins['top_margin'], bottomMargin=margins['bottom_margin'])
    flowables = []

    for paragraph_text in paragraphs:
        if paragraph_text[0:4] == ' ' * 4:
            paragraph = Paragraph(paragraph_text, indent_style)
        else:
            paragraph = Paragraph(paragraph_text, style)
        flowables.append(paragraph)
    if (n := margins['num_columns']) > 1:
        story = [BalancedColumns(flowables, nCols=n, innerPadding=margins['col_inner_padding'])]
    else:
        story = flowables
    doc.build(story)


def fileName(book, start_ref, end_ref):
    with open('write_loc.txt', 'r') as f:
        path = f.read()

    if start_ref[1] == 1 and end_ref[1] == 'end':
        if start_ref[0] == end_ref[0]:
            return f'{path}{book} {start_ref[0]}.pdf'
        else:
            return f'{path}{book} {start_ref[0]}–{end_ref[0]}.pdf'
    else:
        if start_ref[0] == end_ref[0]:
            return f'{path}{book} {start_ref[0]}.{start_ref[1]}–{end_ref[1]}.pdf'
        else:
            return f'{path}{book} {start_ref[0]}.{start_ref[1]}–{end_ref[0]}.{end_ref[1]}.pdf'


if __name__ == '__main__':
    book = 'John'
    start_ref = [1, 1]
    end_ref = [1, 2]

    bible_text = getText(book, *start_ref, *end_ref)
    margins = {'left_margin': 20,
               'right_margin': 20,
               'top_margin': 10,
               'bottom_margin': 10,
               'num_columns': 2,
               'col_inner_padding': 50}
    font = {'size': 11, 'line_spacing': 1.5}
    page = {'portrait_orientation': True, 'print_on_A3': False}

    createDocument(bible_text, margins, font, page, fileName(book, start_ref, end_ref))

# TODO: Make callable from command line, or alternatively with GUI