# !/usr/bin/python3
# -*- coding:utf-8 -*-
# Time  : 2/25/24 9:38 PM
# Author: bc
# Email : itbc9527@163.com

"""
由于python中没有数组这种数据结构, 故用列表代替
题目一:
解题思路: 采用字典这种数据结构存储学生数据, 建立id到学生信息的映射, 字典的value用两个列表保存,
        列表1按学生id排序存储学生信息, 列表2用于存储学生在列表2的索引位置. 采用内消解法解决哈希冲突
"""
from random import choice


# 扩容阈值
ALLOCATE_THRESHOLD = 2/3
# 缩容阈值
RECYCLE_THRESHOLD = 1/4

# items槽位状态: 已使用
STATE_ACTIVE = 1
# items槽位状态: 已删除(逻辑删除)
STATE_DUMMY = 0


class Stu(object):
    def __init__(self, sid):
        self.id = sid
        self._state = STATE_ACTIVE

    def delete(self):
        self._state = STATE_DUMMY

    @property
    def is_deleted(self):
        return self._state == STATE_DUMMY


class StuDict(object):
    def __init__(self):
        # 用于标记字典的的大小, 大小总是等于2的n次方, 初始大小为4
        self.size = 4
        # 总是等于size-1
        self.size_mask = 3

        # 用于存储学生, 大小等于size*ALLOCATE_THRESHOLD用于节省内存
        self.items = [None] * self.item_allocate_size
        # 用于存储学生在items中的索引, 大小等于self.size
        self.indexes = [None] * self.size

        # 记录存储的学生数量
        self.used = 0
        # 记录id最小的学生
        self._min_id_stu = None

    def set_size(self, size):
        self.size = size
        self.size_mask = min(size-1, 0)

    @property
    def item_allocate_size(self):
        return int(self.size*ALLOCATE_THRESHOLD)

    @property
    def item_recycle_size(self):
        return int(self.size*RECYCLE_THRESHOLD)

    def _hash1(self, n):
        """
        一次hash探测函数: 取模
        :param n:
        :return:
        """
        return n & self.size_mask

    def _hash2(self, n):
        """
        哈希冲突二次探测函数: 平方探测
        :param n:
        :return:
        """
        return (n*n) & self.size_mask

    def _index_ok(self, index, sid, op):
        """
        是否找到合适的索引:
        当前索引位置没有被其他未删除的元素占用
        :param index:
        :param sid:
        :param op:
        :return:
        """
        index_in_items = self.indexes[index]

        if index_in_items is None:
            return True
        if self.items[index_in_items].sid == sid:
            return True
        # 只有设置操作才返回dummy状态的item元素
        if op == 's' and self.items[index_in_items].is_deleted:
            return True
        return False

    def hash(self, sid, op):
        """
        根据sid计算哈希值, 得到在indexes列表的索引
        :param sid:
        :param op:
            s: set
            g: get
            u: update
            d: delete
        :return:
        """
        index = self._hash1(sid)
        if self._index_ok(index, sid, op):
            return index
        # 出现哈希冲突, 二次哈希
        index = self._hash2(index)
        while not self._index_ok(index, sid, op):
            index = self._hash2(index)
        return index

    def allocate(self):
        """
        当self.items列表满时扩容:
        对于indexes列表: 申请一块2倍大小的内存空间, 然后重新设置索引.
        对于items列表, 申请一块item_allocate_size大小的空间, 将未删除的元素复制过去
        :return:
        """
        self.indexes = [None] * (self.size * 2)
        self.set_size(len(self.indexes))

        new_items = [None] * self.item_allocate_size
        i = 0
        for stu in self.items:
            if stu is not None and not stu.is_deleted:
                new_items[i] = stu
                i += 1
        self.items = new_items

        # 重新设置索引
        for i in range(self.used):
            self.set_index(i, self.items[i].id)

    def append_to_items(self, stu: Stu) -> int:
        """
        按先后顺序新增到item列表中
        :param stu:
        :return:
        """
        self.items.append(stu)
        if len(self.items) == 1:
            self._min_id_stu = stu
        elif stu.id < self._min_id_stu:
            self._min_id_stu = stu
        return self.used

    def set_index(self, index_in_item, sid):
        """
        保存学生在item列表中的索引
        :param index_in_item:
        :param sid:
        :return:
        """
        inx = self.hash(sid, op='s')
        self.indexes[inx] = index_in_item

    def set(self, stu: Stu):
        if self.used >= self.item_allocate_size:
            self.allocate()

        index_in_item = self.append_to_items(stu)
        self.set_index(index_in_item, stu.id)
        self.used += 1

    def get(self, sid):
        """
        根据id查询学生信息, 先得到索引, 再根据索引去items列表中查找学生信息
        :param sid:
        :return:
        """
        inx = self.hash(sid, op='g')
        index_in_item = self.indexes[inx]
        if index_in_item is None:
            raise KeyError(f'sid: {sid} not exist')
        return self.items[index_in_item]

    def recycle(self):
        """
        重新设置size, 回收内存, 重新设置索引
        :return:
        """
        new_size = self.size // 2

        # 过滤items中已删除的元素
        stu = self.items[0]
        i = 0
        while stu is not None:
            if not stu.is_deleted:
                self.items[i] = stu
                i += 1
        assert i == self.used, f'fatal error: i={i}, used={self.used}'
        # 将已删除的元素重置为None
        while stu is not None:
            self.items[i] = None
            i += 1

        # 删除多余的空间
        self.set_size(new_size)
        self.items = self.items[:self.item_allocate_size]
        self.indexes = self.indexes[:new_size]
        # 重置索引
        for i in range(new_size):
            self.indexes[i] = None

        for i in range(self.used):
            self.set_index(i, self.items[i].id)

    def delete_from_item(self, index):
        """
        逻辑删除, 保留在indexes中的索引
        :param index:
        :return:
        """
        stu = self.items[index]
        stu.delete()

    def delete(self, sid):
        """
        删除一个学生信息, 惰性释放列表空间
        :param sid:
        :return:
        """
        inx = self.hash(sid, op='g')
        index_in_item = self.indexes[inx]
        if index_in_item is None:
            raise KeyError(f'sid: {sid} not exist')

        self.delete_from_item(index_in_item)
        self.used -= 1
        # 如果未删除学生占indexes列表的容量小于1/4, 那么缩容至1/2 * size
        if self.used / self.size <= RECYCLE_THRESHOLD:
            self.recycle()

    def choice(self):
        """
        随机返回一个学生信息
        :return:
        """
        if self.used == 0:
            return ValueError('empty StuDict')
        stu = choice(self.items[:self.used])
        return stu

    @property
    def min_id_stu(self):
        """
        返回id最小的学生
        :return:
        """
        return self._min_id_stu




