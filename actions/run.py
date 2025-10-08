import datetime
import logging 
import sys
import os
from pathlib import Path

from actions.exifGPS import add_and_extract_gps, extract_existing_gps, getCity
from actions.moveEmptyFiles import moveEmptyVideos, moveUndefinedVideos
from actions.generateResultsCSV import generatePredictorResultsAsCSV
from actions.generateStatsPDF import generateStatsPDF
from actions.predict import predict_videos
from actions.renameFiles import rename_videos_with_date_and_info

# Import project utilities
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from objects.options_config import OptionsConfig
from time_utils.timeOffsetToTimezone import time_offset_to_timezone

def runWithArgs(folder, options_config: OptionsConfig, lat=None, lon=None, csv_path=None):
    ## VIDEOS FILE
    filenames = sorted(
            [str(f) for f in Path(folder).rglob('*.[Aa][Vv][Ii]')] +
            [str(f) for f in Path(folder).rglob('*.[Mm][Pp]4')] +
            [str(f) for f in Path(folder).rglob('*.[Mm][Pp][Ee][Gg]')] +
            [str(f) for f in Path(folder).rglob('*.[Mm][Oo][Vv]')] +
            [str(f) for f in Path(folder).rglob('*.[Mm]4[Vv]')]
        )
    
    if options_config.add_gps and lat is not None and lon is not None:
        gps_coordinates, addresses = add_and_extract_gps(filenames, lat, lon, options_config.use_gps_only_for_data)
    else :
        gps_coordinates, addresses = extract_existing_gps(filenames, options_config.get_gps_from_each_file)

    if options_config.rename_files or options_config.generate_data or options_config.generate_stats or options_config.move_empty or options_config.move_undefined or options_config.combine_with_data:
        timezone: datetime.tzinfo = time_offset_to_timezone(options_config.time_offset)
        prediction_results = predict_videos(filenames, options_config.prediction_threshold, timezone)
    else:
        logging.info("No data generation or moving of empty videos selected, skipping prediction step.")

    if options_config.rename_files:
        rename_videos_with_date_and_info(filenames, prediction_results["predictions"], prediction_results["dates"])

    if options_config.generate_stats:
        generateStatsPDF(folder, "stats", prediction_results, addresses, csv_path)

    if options_config.generate_data or csv_path:
        generatePredictorResultsAsCSV(folder, filenames, prediction_results, gps_coordinates, [getCity(address) for address in addresses], options_config.generate_data, csv_path)

    if options_config.move_empty:
        moveEmptyVideos(folder, filenames, prediction_results["predictions"])

    if options_config.move_undefined:
        moveUndefinedVideos(folder, filenames, prediction_results["predictions"])
