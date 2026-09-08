"""Extract an agent-reviewed article interval without preceding same-page text."""
import fitz

def extract(source,first,last,first_top=0):
    with fitz.open(source) as original, fitz.open() as article:
        if not 0<=first<=last<len(original):raise ValueError('Page interval is outside original PDF')
        article.insert_pdf(original,from_page=first,to_page=last)
        if first_top:
            box=article[0].rect
            if not 0<first_top<box.height:raise ValueError('First-page crop is outside original page')
            article[0].set_cropbox(fitz.Rect(0,first_top,box.width,box.height))
        return article.tobytes(garbage=4,deflate=True)
