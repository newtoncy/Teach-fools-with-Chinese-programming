# -*- coding: utf-8 -*-
# @File    : python内建函数.py
# @Date    : 2023-09-08
# @Author  : 王超逸
# @Brief   :

# 修改用C语言提供的对象需要重新编译代码
# 为了省事，这里用代理意思意思
class 字符串(str):
    def 替换(self, *args, **kwargs):
        return 字符串(super().replace(*args, **kwargs))

    def __add__(self, other):
        return 字符串(super().__add__(other))


class 列表(list):
    def __add__(self, other):
        return 列表(super() + other)

    def __mul__(self, other):
        return 列表(super().__mul__(other))


下一个 = next
输入 = input
长度 = len
标准输出 = print
