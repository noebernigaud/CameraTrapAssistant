from datetime import datetime
import logging


def get_predictions_results_with_valid_dates(predictions_results):
    logging.info("Filtering prediction results to only include entries with valid date information...")

    # original lists
    predictedscore = predictions_results["scores"]
    predictedclass = predictions_results["predictions"]
    predictedCount = predictions_results["counts"]
    date_objs: list[datetime] = predictions_results["dates"]
    original_length = len(predictedclass)

    # filter out indexes with no date information
    filtered_indexes = [i for i, d in enumerate(date_objs) if is_valid_date(d)]
    predictedclass = [predictedclass[i] for i in filtered_indexes]
    predictedCount = [predictedCount[i] for i in filtered_indexes]
    date_objs = [date_objs[i] for i in filtered_indexes]
    predictedscore = [predictedscore[i] for i in filtered_indexes]
    logging.info(f"Number of files with date information: {len(predictedclass)}/{original_length}. All other files will be ignored for stats generation.")

    return {
        "predictions": predictedclass,
        "scores": predictedscore,
        "dates": date_objs,
        "counts": predictedCount
    }

def is_valid_date(d):
    if isinstance(d, datetime):
        return True
    if isinstance(d, str):
        try:
            datetime.fromisoformat(d)
            return True
        except Exception:
            return False
    return False