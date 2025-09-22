from pathlib import Path

from actions.exifGPS import add_and_extract_gps, extract_existing_gps, getCity
from actions.moveEmptyFiles import moveEmptyVideos, moveUndefinedVideos
from actions.generateResultsCSV import generatePredictorResultsAsCSV
from actions.predict import predict_videos
import logging
from actions.renameFiles import rename_videos_with_date_and_info

def runWithArgs(folder, shouldGenerateData, shouldMoveEmptyVideos, shouldMoveUndefinedVideos, shouldRenameFiles, shouldAddGPS=False, lat=None, lon=None):
    ## VIDEOS FILE
    filenames = sorted(
            [str(f) for f in Path(folder).rglob('*.[Aa][Vv][Ii]')] +
            [str(f) for f in Path(folder).rglob('*.[Mm][Pp]4')] +
            [str(f) for f in Path(folder).rglob('*.[Mm][Pp][Ee][Gg]')] +
            [str(f) for f in Path(folder).rglob('*.[Mm][Oo][Vv]')] +
            [str(f) for f in Path(folder).rglob('*.[Mm]4[Vv]')]
        )
    
    if shouldAddGPS and lat is not None and lon is not None:
        gps_coordinates, addresses = add_and_extract_gps(filenames, lat, lon)
    else :
        gps_coordinates, addresses = extract_existing_gps(filenames, True)

    if not (shouldGenerateData or shouldMoveEmptyVideos):
        logging.info("No data generation or moving of empty videos selected, skipping prediction step.")

    if shouldGenerateData or shouldMoveEmptyVideos:
        prediction_results = predict_videos(filenames)

    if shouldRenameFiles:
        rename_videos_with_date_and_info(filenames, prediction_results["predictions"], prediction_results["dates"])

    if shouldGenerateData:
        generatePredictorResultsAsCSV(folder, filenames, prediction_results, gps_coordinates, [getCity(address) for address in addresses])

    if shouldMoveEmptyVideos:
        moveEmptyVideos(folder, filenames, prediction_results["predictions"])

    if shouldMoveUndefinedVideos:
        moveUndefinedVideos(folder, filenames, prediction_results["predictions"])
