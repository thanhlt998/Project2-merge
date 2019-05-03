# from pyvi import ViTokenizer
# import re
# from py_stringmatching.similarity_measure.soft_tfidf import SoftTfIdf
# import json
# import time
# import math
#
#
# # Split string to tokens
# def word_split(text):
#     return re.compile("[\\w_]+").findall(ViTokenizer.tokenize(text))
#
#
# # Normalize tokens
# def word_nomalize(text):
#     return [word.lower() for word in text]
#
#
# # Build inverted index
# def invert_index(str_list):
#     inverted = {}
#     for i, s in enumerate(str_list):
#         for word in s:
#             locations = inverted.setdefault(word, [])
#             locations.append(i)
#     return inverted
#
#
# def size_filtering(x, Y, JACCARD_MEASURE):
#     up_bound = len(x) / JACCARD_MEASURE
#     down_bound = len(x) * JACCARD_MEASURE
#     return [y for y in Y if down_bound <= len(y) <= up_bound]
#
#
# def prefix_filtering(inverted_index, x, Y, PREFIX_FILTERING):
#     if len(x) >= PREFIX_FILTERING:
#         # Sort x, y in Y
#         x_ = sort_by_frequency(inverted_index, x)
#         Y_ = []
#         ids = []
#         for i, y in enumerate(Y):
#             if len(y) >= PREFIX_FILTERING:
#                 Y_.append(sort_by_frequency(inverted_index, y)[:len(y) - PREFIX_FILTERING + 1])
#                 ids.append(i)
#         Y_inverted_index = invert_index(Y_)
#         Y_filtered_id = []
#         for x_j in x_[:len(x) - PREFIX_FILTERING + 1]:
#             Y_filtered_id += Y_inverted_index.get(x_j) if Y_inverted_index.get(x_j) is not None else []
#         Y_filtered_id = set(Y_filtered_id)
#         return [Y[ids[i]] for i in Y_filtered_id]
#     else:
#         return []
#
#
# def calc_prefix(x, y, JACCARD_MEASURE):
#     k = math.ceil((JACCARD_MEASURE / (JACCARD_MEASURE + 1)) * (len(x) + len(y)))
#     if len(x) >= k and len(y) >= k:
#         return y, k
#     return None
#
#
# # def position_filtering(inverted_index, x, Y, JACCARD_MEASURE):
# #     Y_prefix = []
# #     for y in Y:
# #         prefix = calc_prefix(x, y, JACCARD_MEASURE)
# #         if prefix is not None:
# #             Y_prefix.append(prefix)
# #
# #     Y_ = [(sort_by_frequency(inverted_index, y_prefix[0])[:len(y_prefix[0]) - y_prefix[1] + 1], i) for i, y_prefix in enumerate(Y_prefix)]
# #     Y_inverted_index = invert_index([y_[0] for y_ in Y_])
# #
# #     x_ = sort_by_frequency(inverted_index, x)
# #     prefix_min = min([y_prefix[1] for y_prefix in Y_prefix])
# #     Y_filtered_id = []
# #
# #     for x_j in x_[:len(x) - prefix_min + 1]:
# #         ids = Y_inverted_index.get(x_j)
# #         if ids is not None:
# #             Y_filtered_id += ids
# #     Y_filtered_id = set(Y_filtered_id)
# #
# #     return [Y[Y_[i][1]] for i in Y_filtered_id]
#
# def position_filtering(inverted_index, x, Y, JACCARD_MEASURE):
#     # Calculate (y, prefix) array, ids keep real indices
#     Y_prefix = []
#     ids = []
#     for i, y in enumerate(Y):
#         prefix = calc_prefix(x, y, JACCARD_MEASURE)
#         if prefix is not None:
#             Y_prefix.append(prefix)
#             ids.append(i)
#
#     # Calculate array of y' = y[len(y) - prefix_filtering + 1] and min_prefix
#     Y_ = []
#     min_prefix = 100000
#     for y in Y_prefix:
#         Y_.append(sort_by_frequency(inverted_index, y[0])[:len(y[0]) - y[1] + 1])
#         if y[1] < min_prefix:
#             min_prefix = y[1]
#
#     # Build inverted index of y'
#     Y_inverted_index = invert_index(Y_)
#
#     # Sort x by frequency of tokens in root index
#     x_ = sort_by_frequency(inverted_index, x)
#
#     # id of y satisfied in Y_
#     Y_filtered_id = []
#
#     for x_j in x_[:len(x) - min_prefix + 1]:
#         id_match = Y_inverted_index.get(x_j)
#         if id_match is not None:
#             Y_filtered_id += id_match
#
#     # Turn Y_filtered_id into a set of unique indices
#     Y_filtered_id = set(Y_filtered_id)
#
#     return [Y[ids[i]] for i in Y_filtered_id]
#
#
# def sort_by_frequency(inverted_index, arr):
#     return sorted(arr,
#                   key=lambda arr_i: len(inverted_index.get(arr_i) if inverted_index.get(arr_i) is not None else []))
#
#
# with open('job_crawl/vieclam24h.json', encoding='utf-8-sig') as f1:
#     X = json.loads(f1.read())
#     f1.close()
#
# with open('job_crawl/careerbuilder.json', encoding='utf-8-sig') as f2:
#     Y = json.loads(f2.read())
#     f2.close()
#
# # Const
# JACCARD_MEASURE = 0.9
# PREFIX_FILTERING = 3
# SIMILARITY_THRESHOLD = 0.95
#
# # Time start
# print(time.strftime("%H:%M:%S", time.localtime()))
#
# # Split
# X_title_split = [word_split(x.get('title')) for x in X]
# Y_title_split = [word_split(y.get('title')) for y in Y]
#
# # Normalize
# X_title_normalize = [word_nomalize(X_title) for X_title in X_title_split]
# Y_title_normalize = [word_nomalize(Y_title) for Y_title in Y_title_split]
#
# # Inverted index of Y
# Y_inverted_index = invert_index(Y_title_normalize)
#
# # Similarity score with SoftTfIdf
# # softTfIdf = SoftTfIdf(X_title_normalize + Y_title_normalize)
# softTfIdf = SoftTfIdf(Y_title_normalize)
#
# X_ = []
#
# for x in X_title_normalize:
#     Y_size_filtering = size_filtering(x, Y_title_normalize, JACCARD_MEASURE)
#     # Y_candidates = prefix_filtering(Y_inverted_index, x, Y_size_filtering, PREFIX_FILTERING)
#     Y_candidates = position_filtering(Y_inverted_index, x, Y_size_filtering, JACCARD_MEASURE)
#     flag = False
#     for y in Y_candidates:
#         if softTfIdf.get_raw_score(x, y) > SIMILARITY_THRESHOLD:
#             print(x, y)
#             flag = True
#             break
#     if not flag:
#         X_.append(x)
#
# print(len(X_))
#
# # Time end
# print(time.strftime("%H:%M:%S", time.localtime()))
