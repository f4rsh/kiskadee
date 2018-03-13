"""Initializes kiskadee components.

This module will run monitor and runner as processes.
"""

from multiprocessing import Process

import kiskadee.model
import kiskadee.queue
import kiskadee.database
from kiskadee.runner import Runner
from kiskadee.monitor import Monitor

def init():
    queues = kiskadee.queue.Queues()
    db = kiskadee.database.Database()
    monitor = Monitor(db, queues)
    runner = Runner(queues)
    Process(target=monitor.run,).start()
    runner_process = Process(target=runner.run,)
    runner_process.start()
    runner_process.join()
