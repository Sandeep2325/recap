"""
Multithreading vs Multiprocessing examples.

Run:
  .venv/bin/python examples/concurrency_examples.py

Rule of thumb:
  - threading       -> I/O wait (network, disk, sleep)
  - multiprocessing -> CPU work (math, parsing, heavy loops)
"""

from __future__ import annotations

import time
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def io_task(name: str, seconds: float = 1.0) -> str:
    """Simulates waiting on I/O (API call, DB, file)."""
    print(f"[I/O] {name} started", flush=True)
    time.sleep(seconds)
    print(f"[I/O] {name} done", flush=True)
    return f"{name}-ok"


def cpu_task(n: int) -> int:
    """Simulates CPU-heavy work."""
    total = 0
    for i in range(n):
        total += i * i
    return total


def example_threads_manual():
    print("\n=== Multithreading (manual Thread) ===")
    start = time.perf_counter()

    threads = [
        threading.Thread(target=io_task, args=(f"worker-{i}", 1.0))
        for i in range(4)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Finished in {time.perf_counter() - start:.2f}s (expect ~1s, not 4s)")


def example_thread_pool():
    print("\n=== Multithreading (ThreadPoolExecutor) ===")
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(io_task, [f"api-{i}" for i in range(4)], [1.0] * 4))

    print("Results:", results)
    print(f"Finished in {time.perf_counter() - start:.2f}s")


def example_process_pool():
    print("\n=== Multiprocessing (ProcessPoolExecutor) ===")
    start = time.perf_counter()
    workloads = [3_000_000] * 4

    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(cpu_task, workloads))

    print("Results count:", len(results), "| sample:", results[0])
    print(f"Finished in {time.perf_counter() - start:.2f}s")


def example_mp_pool():
    print("\n=== Multiprocessing (multiprocessing.Pool) ===")
    start = time.perf_counter()
    workloads = [3_000_000] * 4

    with mp.Pool(processes=4) as pool:
        results = pool.map(cpu_task, workloads)

    print("Results count:", len(results), "| sample:", results[0])
    print(f"Finished in {time.perf_counter() - start:.2f}s")


def compare_cpu_thread_vs_process():
    print("\n=== Same CPU work: threads vs processes ===")
    workloads = [2_500_000] * 4

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(cpu_task, workloads))
    thread_time = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(cpu_task, workloads))
    process_time = time.perf_counter() - start

    print(f"Threads (CPU-bound):     {thread_time:.2f}s  <- often slower (GIL)")
    print(f"Processes (CPU-bound):   {process_time:.2f}s  <- usually faster")


def compare_io_thread_vs_process():
    print("\n=== Same I/O work: threads vs processes ===")
    names = [f"job-{i}" for i in range(4)]

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(io_task, names, [0.5] * 4))
    thread_time = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(io_task, names, [0.5] * 4))
    process_time = time.perf_counter() - start

    print(f"Threads (I/O-bound):     {thread_time:.2f}s  <- lighter / preferred")
    print(f"Processes (I/O-bound):   {process_time:.2f}s  <- works, but heavier")


def django_note():
    print(
        """
=== Django tip ===
Don't start long threads/processes inside a normal request view.
Prefer Celery / RQ / Huey / django-q for background jobs,
or async + ASGI for many concurrent I/O waits.
"""
    )


if __name__ == "__main__":
    example_threads_manual()
    example_thread_pool()
    example_mp_pool()
    example_process_pool()
    compare_cpu_thread_vs_process()
    compare_io_thread_vs_process()
    django_note()
