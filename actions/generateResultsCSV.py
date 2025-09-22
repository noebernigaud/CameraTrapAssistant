import os
import pandas as pd
import logging

def generatePredictorResultsAsCSV(folder, filenames, predictions_results, gps_coordinates, addresses):
    logging.info("Generating results CSV...")
    predictedclass = predictions_results["predictions"]
    predictedscore = predictions_results["scores"]
    dates = predictions_results["dates"]
    preddf = pd.DataFrame({
        'filename':filenames, 
        'dates':dates, 
        'city':addresses,
        'gps':gps_coordinates,
        'prediction':predictedclass, 
        'score':predictedscore
    })
    # Create 'data' folder inside VIDEOPATH if it doesn't exist
    data_folder = os.path.join(folder, "data")
    os.makedirs(data_folder, exist_ok=True)
    # Always save as 'results.csv' in the 'data' folder
    csv_out_path = os.path.join(data_folder, "results.csv")
    preddf.to_csv(csv_out_path, index=False)
    logging.info('Done, results saved in ' + csv_out_path)