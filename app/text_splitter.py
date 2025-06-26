# -*- coding: utf-8 -*-
import re

alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|edu|me)"
digits = "([0-9])"
multiple_dots = r'\.{2,}'


def get_text_parts(text: str, parts_count: int, is_split_by_sentences: bool, remove_dots_at_the_end: bool) -> list[str]:
    if parts_count == 1: return [clear_text(text, remove_dots_at_the_end)]
    result = split_by_sentences(text) if is_split_by_sentences else split_by_delimiters(text)
    if len(result) > parts_count:
        result = combine_into_parts(result, parts_count)

    for i in range(len(result)):
        result[i] = clear_text(result[i], remove_dots_at_the_end)

    return result


def clear_text(text: str, remove_dots_at_the_end: bool) -> str:
    result = clear_end_of_text(text)
    if remove_dots_at_the_end:
        result = remove_dot(result)
    return result


# from https://stackoverflow.com/a/31505798
def split_by_sentences(text: str) -> list[str]:
    """
    Split the text into sentences.

    If the text contains substrings "<prd>" or "<stop>", they would lead
    to incorrect splitting because they are used as markers for splitting.

    :param text: text to be split into sentences
    :type text: str

    :return: list of sentences
    :rtype: list[str]
    """
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
    if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
    text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
    text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = [s.strip() for s in sentences]
    if sentences and not sentences[-1]: sentences = sentences[:-1]
    return sentences


def split_by_delimiters(text: str) -> list[str]:
    """
    The function splits strings into substrings by delimiters

    :param text: text to be split by delimiters
    :type text: str

    :return: list of substrings separated by delimiters
    :rtype: list[str]
    """
    text = text.rstrip(";:,.!?")
    return re.split(r'\.\.\.|[;:,.!?]', text)


def combine_into_parts(sentences: list[str], parts_count: int) -> list[str]:
    """
    Combines sentences into text parts so that the number of text parts matches the number passed in parts_count

    :param sentences: sentences that will be combined into text parts
    :type sentences: list[str]

    :param parts_count: number of parts of text
    :type parts_count: int

    :return: list of text parts
    :rtype: list[str]
    """

    # Sentences size
    total_sentences = len(sentences)

    # Calculate size of each part
    part_size = total_sentences // parts_count
    remainder = total_sentences % parts_count

    # Create list for parts
    result: list[str] = list()
    start_index = 0

    for i in range(parts_count):
        # Determine the size of the current part
        current_part_size = part_size + (1 if i < remainder else 0)
        end_index = start_index + current_part_size

        part = ' '.join(sentences[start_index:end_index])

        # Add a part to the result
        result.append(part)

        # Updating the index for the next part
        start_index = end_index

    return result


def clear_end_of_text(text: str) -> str:
    """
    Return a copy of the string with "trash trailing characters" removed.
    """
    return text.rstrip(";:,@{}#&%$№/''…")


def remove_dot(string: str) -> str:
    """
    Removes the dot at the end of the line if there is one
    """
    if string.endswith('.'):
        return string[:-1]
    return string
