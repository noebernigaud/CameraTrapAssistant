import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
import matplotlib
import logging

matplotlib.use('agg')   
import matplotlib.pyplot as plt

from core.file_operations.exif_gps import getCity
from core.stats.utils.data_extractions.extract_dates_info import getDatesRange
from core.stats.utils.data_extractions.extract_percent_info import getFilesWithAnimalsProportions
from core.stats.utils.data_extractions.retrieve_CSV_data import retrieveDataFromCSV
from core.stats.utils.data_extractions.prediction_results_filter import get_predictions_results_with_valid_dates
from core.stats.utils.graphics_data_generation.generate_animals_table_data import buildAnimalsTableData
from core.stats.utils.graphics_data_generation.generate_observations_by_time_graph import generateCircularObservationsGraph, generateObservationsByTimeAndDaysGraph, getDatesChunksForObservationsByTimeGraphs
from utils.meteo_api import getMeteoData


def generateStatsPDF(folder, name, predictions_results, addresses, gps_coordinates, csv_path=None):
    ### Extract data ###
    logging.info("Extracting data for stats PDF generation...")

    predictions_results = get_predictions_results_with_valid_dates(predictions_results)

    predictedclass = predictions_results["predictions"]
    predictedCount = predictions_results["counts"]
    date_objs: list[datetime.datetime] = predictions_results["dates"]

    species_set = set(predictedclass)


    # Get existing CSV data if provided
    existing_csv_predictions = None
    if csv_path:
        logging.info(f"Retrieving existing CSV data from {csv_path} for combined stats generation...")
        existing_csv_predictions = get_predictions_results_with_valid_dates(retrieveDataFromCSV(csv_path))
        if existing_csv_predictions:
            combined_predicted_class = existing_csv_predictions["predictions"] + predictedclass
            combined_predicted_count = existing_csv_predictions["counts"] + predictedCount
            combined_predicted_score = existing_csv_predictions["scores"] + predictions_results.get("scores", [])
            combined_predicted_date_objs = [datetime.datetime.fromisoformat(d) for d in existing_csv_predictions["dates"]] + date_objs
            # Use combined data for PDF generation
            generateStatsPDF(
                folder,
                "combined_" + name,
                {
                    "predictions": combined_predicted_class,
                    "counts": combined_predicted_count,
                    "dates": combined_predicted_date_objs,
                    "scores": combined_predicted_score
                },
                addresses,
                gps_coordinates,
                csv_path=None  # Avoid infinite recursion
            )

    # Calculate stats
    num_videos = len(predictedclass)
    num_with_animals, percent_with_animals = getFilesWithAnimalsProportions(num_videos, predictedclass)

    # Dates
    start_date_str, end_date_str, total_days = getDatesRange(date_objs)

    # City/address
    city = getCity(addresses[0]) if addresses else "Unknown location"


    ### Generation PDG ###
    logging.info(f"Generating {name} PDF...")
    
    data_folder = os.path.join(folder, "data")
    os.makedirs(data_folder, exist_ok=True)
    doc = SimpleDocTemplate(os.path.join(data_folder, f"{name}.pdf"), pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    if city and city != "None":
        title = f"DeepFaune Results for {start_date_str} to {end_date_str}, at {city}"
    else:
        title = f"DeepFaune Results for {start_date_str} to {end_date_str}"
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Subtitle
    subtitle = f"Analyzed {num_videos} videos: {num_with_animals} ({percent_with_animals}%) with animals"
    elements.append(Paragraph(subtitle, styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Table
    t = Table(buildAnimalsTableData(species_set, predictedclass, predictedCount, date_objs), hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t) 
    elements.append(Spacer(1, 24))

    # Matplotlib graph for observation vizualisation by time and dates
    # Remove non-animal classes from species_set for graphing
    if "empty" in species_set:
        species_set.remove("empty")
    if "undefined" in species_set:
        species_set.remove("undefined")
    if "vehicle" in species_set:
        species_set.remove("vehicle")

    # If no species left, skip graph generation
    if not species_set:
        elements.append(Paragraph("No animal detections to plot.", styles['Normal']))
        doc.build(elements)
        logging.info(f"Skipping graphs generation as no animal detections found.")
        logging.info(f"Succesfully generated {name} PDF.")
        return

    # Chucking dates for graphs
    date_chunks = getDatesChunksForObservationsByTimeGraphs(date_objs)

    # --- Add one graph per chunk of dates ---
    species_colors = {s: plt.cm.tab20(i) for i, s in enumerate(sorted(species_set))}

    observations_by_time_and_species_graph = generateCircularObservationsGraph(species_set, predictedclass, date_objs, species_colors)
    elements.append(observations_by_time_and_species_graph)
    elements.append(Spacer(1, 24))

    if date_chunks:
        for _, chunk_dates_list in enumerate(date_chunks):
            # Meteo data (requires lat, lon, start_date, end_date)
            try:
                lat, lon = gps_coordinates
                if date_objs:
                    # Use a sorted copy of date_objs to determine first/last dates without mutating the original list
                    sorted_date_objs = sorted(chunk_dates_list)
                    first_date = sorted_date_objs[0]
                    last_date = sorted_date_objs[-1]
                    meteo_data = getMeteoData(lat, lon, first_date, last_date)
                else:
                    logging.info("No dates available, skipping meteo data retrieval.")
                    meteo_data = None
            except Exception:
                logging.info("Failed to retrieve meteo data.", exc_info=True)
                meteo_data = None
            observations_by_time_and_day_graph = generateObservationsByTimeAndDaysGraph(
                species_set,
                predictedclass,
                date_objs,
                species_colors,
                chunk_dates_list,
                meteo_data
            )
            elements.append(observations_by_time_and_day_graph)
            elements.append(Spacer(1, 24))
    else:
        # No dates, add a placeholder
        elements.append(Paragraph("No detections to plot.", styles['Normal']))

    doc.build(elements)
    logging.info(f"Succesfully generated {name} PDF.")
