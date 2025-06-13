import emoji
from markdown import Markdown
from io import StringIO

# from https://stackoverflow.com/a/54923798
def unmark_element(element, stream=None) -> str:
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

# patching Markdown
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False

def give_emoji_free_text(text) -> str:
    return emoji.replace_emoji(text, replace='')

def normalize_text(text) -> str:
    return __md.convert(give_emoji_free_text(text))