from typing import Sequence


class BitmapSet:
    '''使用 Bigmap 定义的 Set'''

    def __init__(self, items: Sequence[int]) -> None:
        self.bit_set = bytearray()
        self.update(items)

    @property
    def count(self):
        '''元素数量'''
        n = 0
        for byte in self.bit_set:
            while byte:
                byte &= byte - 1
                n += 1
        return n

    @property
    def length(self) -> int:
        '''字节长度'''
        return len(self.bit_set)

    @property
    def bit_size(self) -> int:
        '''位长度'''
        return self.length * 8

    @staticmethod
    def decompose(num):
        while num:
            yield (num ^ (num - 1)).bit_length()
            num &= (num - 1)

    def expand(self, length):
        '''扩容指定长度字节'''
        self.bit_set.extend(b'\x00' * length)

    def ismember(self, num: int) -> bool:
        '''检查某对象是否是一个成员'''
        idx, offset = divmod(num, 8)
        return bool(self.bit_set[idx] & (1 << offset))

    def member(self, idx: int, offset: int) -> int:
        '''获取某个位置的值'''
        return idx * 8 + offset

    def members(self):
        '''获取所有元素'''
        for idx, num in enumerate(self.bit_set):
            for offset in self.decompose(num):
                yield idx * 8 + offset - 1

    def add(self, num: int) -> None:
        '''添加一个元素'''
        idx, offset = divmod(num, 8)
        need_length = idx + 1

        if self.length < need_length:
            self.expand(need_length - self.length)

        self.bit_set[idx] |= 1 << offset

    def pop(self, num: int) -> None:
        '''弹出一个元素'''
        idx, offset = divmod(num, 8)
        if idx < self.length:
            self.bit_set[idx] &= 0xff ^ (1 << offset)

    def update(self, other: Sequence[int]) -> None:
        '''将一个序列更新到 BitmapSet'''
        for num in other:
            self.add(num)

    def inter(self, other: Sequence[int]) -> 'BitmapSet':
        '''交集'''
        for num in other:
            print(num)

    def diff(self, other: Sequence[int]) -> 'BitmapSet':
        '''差集'''

    def union(self, other: Sequence[int]) -> 'BitmapSet':
        '''并集'''


if __name__ == "__main__":
    items = [0, 1, 2, 3, 4, 7, 8, 9, 15, 16, 17, 19, 63, 64, 71, 81, 97, 100, 1023, 1024, 1025]
    b = BitmapSet(items)
    assert b.count == len(items)
    idx, offset = divmod(max(items), 8)
    assert b.length == idx + 1
    assert b.bit_size >= idx * 8 + offset, f'{b.bit_size} >= {idx * 8 + offset}'

    for i in range(max(items)):
        assert b.ismember(i) == (i in items)

    assert sorted(b.members()) == sorted(items)

    o_cnt = b.count
    b.add(100)
    assert b.count == o_cnt, f'{b.count} != {o_cnt}'

    b.add(111)
    assert b.count == o_cnt + 1, f'{b.count} != {o_cnt+1}'

    b.pop(111)
    assert b.count == o_cnt, f'{b.count} != {o_cnt}'

    b.pop(5)
    assert b.count == o_cnt, f'{b.count} != {o_cnt}'
