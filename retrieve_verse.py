from meaningless import WebExtractor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, A3
from reportlab.lib.units import inch

def getText(book, ch_from, v_from, ch_to, v_to, version='ESVUK', bible=None):
    if bible is None or not isinstance(bible, WebExtractor):
        bible = WebExtractor(translation=version)
    if v_to == 'end':
        v_to = 200
    return bible.get_passage_range(book, ch_from, v_from, ch_to, v_to)


if __name__ == '__main__':
    # Settings to change
    text = getText('John', 5, 1, 5, 'end')
    left_margin, right_margin, top_margin, bottom_margin = 20, 20, 10, 10
    paragraph_spacing = 0
    portrait = True
    columns = 1
    print_on_A3 = False
    fileName = 'sample.pdf'
    font_size = 11
    line_spacing = 1.5  # multiplier

    # Don't change the below
    documentTitle = 'sample'
    paragraphs = text.split('\n')
    # registering a external font in python
    pdfmetrics.registerFont(TTFont('Alegreya Sans', 'AlegreyaSans-Regular.ttf'))

    style = ParagraphStyle(name='BodyText', fontName='Alegreya Sans', fontSize=font_size,
                           leading=font_size * line_spacing)
    indent_style = ParagraphStyle(name='IndentedBodyText', parent=style, leftIndent=15)

    if print_on_A3:
        paper_size = A3
    else:
        paper_size = A4
    if not portrait:
        paper_size = paper_size[-1:-3:-1]

    canv = canvas.Canvas(fileName, pagesize=paper_size)
    page_width, page_height = paper_size
    canv.setTitle(documentTitle)
    available_width = page_width - left_margin - right_margin
    available_height = page_height - top_margin - bottom_margin
    for paragraph_text in paragraphs:
        while True:
            if paragraph_text[0:4] == ' ' * 4:
                paragraph = Paragraph(paragraph_text, indent_style)
            else:
                paragraph = Paragraph(paragraph_text, style)
            para_width, para_height = paragraph.wrap(available_width, available_height - bottom_margin)
            if para_width > available_width:
                raise Exception("Paragraph width greater than available width")

            if para_height > available_height:
                canv.showPage()
                available_width = page_width - left_margin - right_margin
                available_height = page_height - top_margin - bottom_margin
                continue
            else:
                paragraph.drawOn(canv, left_margin, available_height - para_height)
                available_height -= (para_height + paragraph_spacing)
                break


    # saving the pdf
    canv.save()

    # TODO: Paragraphs across pages
    # TODO: column options