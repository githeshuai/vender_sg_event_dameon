# -*- coding: utf-8 -*-


def union_list(a, b):
    if not b:
        return a
    for i in b:
        if i not in a:
            a.append(i)
    return a
