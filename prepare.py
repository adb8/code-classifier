import re
import pandas as pd

symbols = [
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ":",
    ",",
    ".",
    "+",
    "-",
    "*",
    "/",
    "%",
    "'",
    '"',
    "'",
    '"',
]

def add_row_to_csv(file_path, row_data):
    try:
        df = pd.read_csv(file_path, sep=";")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=["Label", "Code"])

    new_row = pd.DataFrame([row_data], columns=df.columns)
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(file_path, index=False, sep=";")

def remove_strings_from_input_print(input_string):
    pattern = r"(print|input)\(.*?\)"

    def remove_text(match):
        matched_string = match.group(1)
        inside_string = re.search(r"\((.*?)\)", match.group(0)).group(1)
        if "format" in inside_string:
            return matched_string + "(format)"
        else:
            return matched_string + "()"

    return re.sub(pattern, remove_text, input_string)

def remove_strings_from_quotes(input_string):
    input_string = input_string.replace('"', "'")
    pattern = r"'(.*?)'"
    result_string = re.sub(pattern, "", input_string)
    return result_string

def remove_variables(input_string):
    input_string = " " + input_string
    replaced_text = []

    def replace_text(match):
        matched_string = match.group(1)
        if matched_string not in replaced_text:
            append = True
            for symbol in symbols:
                if symbol in matched_string:
                    append = False
            if append:
                replaced_text.append(matched_string)
                return ""
            else:
                return matched_string
        else:
            return matched_string

    pattern = r"(?<=\s)([^=\s]+)(?=\s=)"
    result_string = re.sub(pattern, replace_text, input_string)
    for word in replaced_text:
        result_string = re.sub(
            r"\b" + re.escape(word) + r"\b", "", result_string
        )
    return result_string[1:]

def remove_functions(input_string):
    pattern = r"def\s(.*?)\("
    matches = re.findall(pattern, input_string)

    for match in matches:
        function_name = match.strip()
        input_string = input_string.replace(f"def {function_name}(", "")
        input_string = re.sub(rf"{function_name}", "", input_string)
    return input_string

def remove_numbers(input_string):
    result_string = re.sub(r"\d+", "", input_string)
    return result_string

def remove_escape_chars(input_string):
    escape_characters = ['\n', '\t']
    for char in escape_characters:
        input_string = input_string.replace(char, ' ')
    return input_string

def remove_symbols(input_string):
    for symbol in symbols:
        input_string = input_string.replace(symbol, " ")
    return input_string

def remove_comments(input_string):
    pattern = r'(?<=#).*?(?=\n)'
    cleaned_string = re.sub(pattern, '', input_string)
    return cleaned_string

def remove_certain_chars(input_string):
    cleaned_string = input_string.replace('\t', ' ').replace('\n', ' ').replace('#', ' ').replace(';', '')
    return cleaned_string

def remove_extra_space(input_string):
    trimmed_string = input_string.strip()
    cleaned_string = re.sub(r'\s+', ' ', trimmed_string)
    return cleaned_string

def lowercase_strings(input_string):
    return input_string.lower()

def prepare_code(input_string):
    input_string = remove_escape_chars(input_string)
    input_string = remove_strings_from_input_print(input_string)
    input_string = remove_strings_from_quotes(input_string)
    input_string = remove_variables(input_string)
    input_string = remove_functions(input_string)
    input_string = remove_numbers(input_string)
    input_string = remove_symbols(input_string)
    input_string = remove_extra_space(input_string)
    return input_string