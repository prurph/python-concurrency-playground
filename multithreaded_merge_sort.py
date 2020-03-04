import random
import time
from threading import Thread


def multithreaded_merge_sort(arr):
    return multithreaded_merge_sort_h(arr, 0, len(arr) - 1, [None] * len(arr))


def multithreaded_merge_sort_h(arr, start, end, merge_scratch):
    if start >= end:
        return arr
    mid = start + (end - start) // 2

    workers = (
        Thread(
            name=f"MS[{start}:{mid + 1}]",
            target=multithreaded_merge_sort_h,
            args=(arr, start, mid, merge_scratch),
        ),
        Thread(
            name=f"MS[{mid + 1}:{end}]",
            target=multithreaded_merge_sort_h,
            args=(arr, mid + 1, end, merge_scratch),
        ),
    )

    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    # Copy array into backup array and merge from there
    for i in range(start, end + 1):
        merge_scratch[i] = arr[i]

    return merge(arr, merge_scratch, start, mid, end)


def single_threaded_merge_sort(arr):
    return single_threaded_merge_sort_h(arr, arr[:], 0, len(arr) - 1)


def single_threaded_merge_sort_h(arr, aux_arr, start, end):
    if start == end:
        return arr
    mid = start + (end - start) // 2

    single_threaded_merge_sort_h(aux_arr, arr, start, mid)
    single_threaded_merge_sort_h(aux_arr, arr, mid + 1, end)

    return merge(arr, aux_arr, start, mid, end)


def merge(merge_into, merge_from, start, mid, end):
    left_p, right_p = start, mid + 1
    merge_p = start

    while left_p <= mid and right_p <= end:
        if merge_from[left_p] < merge_from[right_p]:
            merge_into[merge_p] = merge_from[left_p]
            left_p += 1
        else:
            merge_into[merge_p] = merge_from[right_p]
            right_p += 1
        merge_p += 1
    while left_p <= mid:
        merge_into[merge_p] = merge_from[left_p]
        left_p += 1
        merge_p += 1
    while right_p <= end:
        merge_into[merge_p] = merge_from[right_p]
        right_p += 1
        merge_p += 1

    return merge_into


def main():
    # Very predictably this blows up recursively creating thousands of threads if you go any higher
    for test_size in map(lambda x: x[1] ** x[0], enumerate([10] * 4)):
        arr_1 = list(range(test_size))
        random.shuffle(arr_1)
        arr_2 = arr_1[:]

        st_start = time.time()
        single_threaded_merge_sort(arr_1)
        st_end = time.time()
        mt_start = time.time()
        multithreaded_merge_sort(arr_1)
        mt_end = time.time()

        print(
            f"List size: {test_size} Single-threaded: {st_end - st_start:0.5f} Multi-threaded: {mt_end - mt_start:0.5f}"
        )


if __name__ == "__main__":
    main()
