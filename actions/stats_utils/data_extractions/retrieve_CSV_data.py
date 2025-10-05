import logging


def retrieveDataFromCSV(csv_path):
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        # Extract columns to reconstruct predictions_results, gps_coordinates, addresses
        predictions_results = {
            "predictions": df["prediction"].tolist(),
            "scores": df["score"].tolist(),
            "dates": df["dates"].tolist(),
            "counts": df["counts"].tolist(),
        }
        return predictions_results
    except Exception as e:
        logging.info(f"Failed to read CSV file at {csv_path}: {e}")
        raise ValueError(f"Error reading CSV file at {csv_path}: {e}")