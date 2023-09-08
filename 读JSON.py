# -*- coding: utf-8 -*-
# @Author: Admin
# @Date:   2019-11-01 16:52:34
# @Last Modified by:   Admin
# @Last Modified time: 2019-11-01 18:18:14
from pathlib import Path


def 读JSON文件(fileName):
    import json
    assert fileName
    path = Path(__file__).parent / fileName
    with path.open(mode='r', encoding="utf-8") as file:
        return json.loads(file.read())

