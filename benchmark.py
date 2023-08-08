import time


def measure_duration(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        duration = round(end - start, 2)

        # check = kwargs.get('directory', '')
        exit_message = f"Conversion complete \nTime elapased: {duration} seconds"
        print(exit_message)

    return wrapper