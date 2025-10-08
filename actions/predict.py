import logging
from logging.handlers import QueueListener
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor
import os
import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from time_utils.timeOffsetToTimezone import convert_to_timezone

def _predict_videos_worker(filenames, threshold, timezone, LANG, log_queue):
    """
    Runs in a separate process and sends log messages to the parent via a queue.
    """
    import logging
    from logging.handlers import QueueHandler
    import sys

    # Configure logging to use the queue
    queue_handler = QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # remove any default handlers
    root_logger.addHandler(queue_handler)

    # Import predictor inside subprocess
    curdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    sys.path.append(os.path.join(curdir, "../deepFauneApp/"))
    from predictTools import PredictorVideo

    logging.info("Loading predictor...")
    predictor = PredictorVideo(filenames, threshold, LANG)

    logging.info("Starting predictions...")
    while True:
        batch, k1, _ = predictor.nextBatch()
        if k1 == len(filenames):
            break
        logging.info(f"Making prediction for video {batch} / {len(filenames)}")

    logging.info("Predictions completed")

    predictions, scores, _, counts = predictor.getPredictions()
    dates: list[datetime.datetime] = predictor.getDates()
    logging.info(f"Using timezone: {timezone}")

    # Assume dates are in UTC, convert them to timezone_to_use
    logging.info(f"First video date before timezone adjustment: {dates[0] if dates else 'No dates available'}")
    dates = [convert_to_timezone(d, timezone) for d in dates]
    logging.info(f"First video date after timezone adjustment: {dates[0] if dates else 'No dates available'}")

    return {
        "predictions": predictions,
        "scores": scores,
        "dates": dates,
        "counts": counts
    }

def predict_videos(filenames, threshold, timezone, LANG="en"):
    logging.info("Lauching predictor subprocess...")
    manager = Manager()
    log_queue = manager.Queue()

    # Parent logging setup
    logging.basicConfig(level=logging.INFO,
                        format="PARENT %(asctime)s - %(levelname)s - %(message)s")

    class InfoForwarder(logging.Handler):
        def emit(self, record):
            # Forward child message to the parent's logger
            logging.info(self.format(record))

    forwarder = InfoForwarder()
    forwarder.setFormatter(logging.Formatter("%(message)s"))

    listener = QueueListener(log_queue, forwarder)
    listener.start()

    try:
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_predict_videos_worker,
                                     filenames, threshold, timezone, LANG, log_queue)
            result = future.result()
    finally:
        listener.stop()

    return result