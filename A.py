# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Time  : 2/29/24 10:29 PM
# Author: bc
# Email : itbc9527@163.com

STRING = b'ZingFront'


def get_alpha_map(string):
    """
    生成字母对应的索引列表
    :param string:
    :return:
    """
    res = {}
    for i in range(len(string)):
        res.setdefault(string[i], []).append(i)
    return res


def answer1(str_array):
    alpha_map = get_alpha_map(STRING)
    print(alpha_map)
    for i in range(len(str_array)):
        if i not in alpha_map:
            return False
        indexes = alpha_map[i]
        # 如果没有可用的索引, 说明有多余的字符, 那么不能得到一样的字符串, 返回False
        if len(indexes) == 0:
            return False
        index = indexes.pop()
        if i == index:
            continue




if __name__ == '__main__':
    answer1(bytearray(b'rontFingZ'))