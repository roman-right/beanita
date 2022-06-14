class Cursor:
    def __init__(self, cur):
        self.cur = cur

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return self.cur.next()
        except StopIteration:
            raise StopAsyncIteration

    async def to_list(self, length=None):
        res = []
        ind = 0
        for i in self.cur:
            if length is not None and length == ind:
                break
            res.append(i)
            ind += 1
        return res
