import os
import pandas as pd
import logging

def generatePredictorResultsAsCSV(folder, filenames, predictions_results, gps_coordinates, addresses, generate_new_csv, csv_path=None):
    logging.info("Generating results CSV...")
    predictedclass = predictions_results["predictions"]
    predictedscore = predictions_results["scores"]
    dates = predictions_results["dates"]
    counts = predictions_results["counts"]
    newdf = pd.DataFrame({
        'filename':filenames, 
        'dates':dates, 
        'city':addresses,
        'gps':gps_coordinates,
        'prediction':predictedclass, 
        'counts':counts,
        'score':predictedscore
    })
    # Create 'data' folder inside VIDEOPATH if it doesn't exist
    data_folder = os.path.join(folder, "data")
    os.makedirs(data_folder, exist_ok=True)
    # If csv_path is provided, append to that CSV
    if csv_path:
        try:
            existing_df = pd.read_csv(csv_path)
            combined_df = pd.concat([existing_df, newdf], ignore_index=True)
            combined_df.to_csv(csv_path, index=False)
            logging.info('Done, results appended to ' + csv_path)
        except Exception as e:
            logging.error(f"Failed to append to CSV {csv_path}: {e}")
            raise
    if generate_new_csv:
        # Always save as 'deepFaune_results.csv' in the 'data' folder
        csv_out_path = os.path.join(data_folder, "deepFaune_results.csv")
        newdf.to_csv(csv_out_path, index=False)
        logging.info('Done, results saved in ' + csv_out_path)