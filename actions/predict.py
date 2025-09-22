import logging
import sys
from logging.handlers import QueueListener
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor
import os
import sys

def _predict_videos_worker(filenames, threshold, LANG, log_queue):
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

    predictions, scores, _, _ = predictor.getPredictions()
    dates = predictor.getDates()

    return {
        "predictions": predictions,
        "scores": scores,
        "dates": dates,
    }

def predict_videos(filenames, LANG="fr", threshold=0.8):
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
                                     filenames, threshold, LANG, log_queue)
            result = future.result()
    finally:
        listener.stop()

    return result