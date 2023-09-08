# -*- coding: utf-8 -*-
# @File    : build.py
# @Date    : 2023-09-08
# @Author  : 王超逸
# @Brief   :

from pathlib import Path
from enum import Enum, auto
from collections import namedtuple
import re

REPLACE_MAP = {
    "导入": "import",
    "从": "from",
    "定义": "def",
    "迭代": "for",
    "之于": "in",
    "当": "while",
    "循环": "while",
    "结果为": "return",
    "恒久": "True",
    "恒久的": "True",
    "从不": "False",
    "对的": "True",
    "错的": "False",
    "真的": "True",
    "假的": "False",
    "真": "True",
    "假": "False",
    "全局的": "global",
    "全局": "global",
    "若": "if",
    "如果": "if",
    "不行就": "elif",
    "否则": "else"
}
Token = namedtuple("Token", ["type", "str"])


class TokenType(Enum):
    identifier = auto()  # 标识符或关键字
    comment = auto()  # 注释
    string = auto()  # 字符串
    mult_line_string = auto()  # 多行字符串
    operator = auto()  # 符号
    num = auto()  # 数字
    space = auto()  # 空格
    LF = auto()  # 换行


def get_token(code, start_pos=0) -> Token:
    # 匹配缩进/空格
    space = re.match(r"^\s+", code[start_pos:])
    if space:
        return Token(TokenType.space, space.group())

    # 匹配注释
    comment = re.match(r"^#.*", code[start_pos:])
    if comment:
        return Token(TokenType.comment, comment.group())

    # 匹配符号
    operator = re.match(r"^[.,!?;:(){}<>\[\]@#$%^&*+=\\|~]+", code[start_pos:])
    if operator:
        return Token(TokenType.operator, operator.group())

    # 匹配字符串
    single_line_string = re.match(r"^[frb]?(['\"]|\"\"\"|''')(?:(?!\1).)*\1", code[start_pos:])
    mult_quote_string = re.match(r"^[frb]?(\"\"\"|''')(?:(?!\1).)*\1", code[start_pos:])
    mult_line_quote = re.match(r"^(\"\"\"|''')", code[start_pos:])
    if mult_quote_string:
        # 已结束的多行字符串
        return Token(TokenType.mult_line_string, mult_quote_string.group())
    if mult_line_quote:
        # 未结束的多行字符串，只返回引号即可，有专门的处理逻辑
        return Token(TokenType.mult_line_string, mult_line_quote.group())
    if single_line_string:
        # 单行字符串
        return Token(TokenType.string, single_line_string.group())

    # 匹配标识符
    identifier = re.match(r"^[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*", code[start_pos:])
    if identifier:
        return Token(TokenType.identifier, identifier.group())

    # 匹配数字
    num = re.match(r"^[-+]?\d*\.?\d+([eE][-+]?\d+)?", code[start_pos:])
    if num:
        return Token(TokenType.num, num.group())
    assert False, "词法正则匹配失败"


def get_next_line(iterator):
    try:
        line = next(iterator).rstrip()
    except StopIteration:
        return None

    # 处理跨行
    while line.endswith("\\"):
        line = line[:-1]
        try:
            next_line = next(iterator).split()
        except StopIteration:
            assert False, "跨行表达式未结束"
        line += " " + next_line
    return line


def replace_key_words(input_str) -> str:
    input_str.replace("\r\n", "\n")
    iterator = iter(input_str.split("\n"))
    token_list = []

    while True:
        line = get_next_line(iterator)
        if line is None:
            break
        pos = 0
        while pos < len(line):
            token = get_token(line, pos)
            assert token.str
            if token.type == TokenType.mult_line_string and len(token.str) == 3:
                # 处理未结束的多行文本
                mult_line_str = []
                mult_line_quote = token.str
                mult_line_str.append(line[pos:])
                while True:
                    # 循环直到多行文本结束
                    try:
                        line = next(iterator)
                    except StopIteration:
                        assert False, "多行文本未结束"
                    if mult_line_quote in line:
                        # 多行文本结束
                        pos = line.find(mult_line_quote) + 3
                        mult_line_str.append(line[:pos])
                        break
                    mult_line_str.append(line)
                token_list.append(Token(TokenType.mult_line_string, "\n".join(mult_line_str)))
            else:
                # 处理其他token
                token_list.append(token)
                pos += len(token.str)
        token_list.append(Token(TokenType.LF, "\n"))

    new_token_list = []
    for i in token_list:
        if i.type == TokenType.identifier and i.str in REPLACE_MAP:
            new_token_list.append(REPLACE_MAP[i.str])
        else:
            new_token_list.append(i.str)
    gen_code = "".join(new_token_list)
    return "from python内建函数 import * \n" + gen_code


def main():
    project_dir = Path(__file__).parent.resolve()
    build_dir = project_dir / "生成"
    for file in project_dir.glob("**/*.pyzh"):
        with file.open("rt", encoding="utf-8") as fp:
            python_code = replace_key_words(fp.read())
        output_file_name = file.name
        assert output_file_name.endswith(".pyzh")
        output_file_name = output_file_name[:-len(".pyzh")] + ".py"
        output_dir = build_dir / file.parent.relative_to(project_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_file_name
        with output_path.open("wt", encoding="utf-8") as fp:
            fp.write(python_code)


if __name__ == '__main__':
    main()
