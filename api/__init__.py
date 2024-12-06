# lst = [1, 2, 3, 4]
# first_name = "mohammad"
# dic = {}
# tup = ()

# print(hasattr(lst, "__iter__"))
# print(hasattr(first_name, "__iter__"))
# print(hasattr(dic, "__iter__"))
# print(hasattr(tup, "__iter__"))

# print((hasattr(lst, "__next__")))

# iter_list = iter(lst)


# class Counter:
#     def __init__(self, start, end):
#         self.start = start
#         self.end = end
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         if self.start > self.end:
#             raise StopIteration
#         self.start += 1
#         return self.start - 1


# c10 = Counter(1, 10)

# print(hasattr(Counter, "__iter__"))
# print(hasattr(Counter, "__next__"))

# for i in c10:
#     print(i)