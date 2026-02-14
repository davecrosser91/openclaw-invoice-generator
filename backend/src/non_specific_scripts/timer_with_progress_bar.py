import time
from tqdm import tqdm


def wait_progress_timer(total_waiting_time_in_secs: int, step_size: int = 1) -> None:
    """
    Timer for when a product is not correctly created.
    :param total_waiting_time_in_secs: Number of seconds to wait
    :param step_size: Step size in which the wait time is to be run through. Default: 1sec.
    :return: None. Timer will be displayed
    """
    for _ in tqdm(range(total_waiting_time_in_secs), desc="Processing items"):
        time.sleep(step_size)
