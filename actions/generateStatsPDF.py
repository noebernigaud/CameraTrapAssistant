import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import os
import matplotlib
import logging

matplotlib.use('agg')   
import matplotlib.pyplot as plt

from actions.exifGPS import getCity
from actions.stats_utils.data_extractions.extract_dates_info import getDatesRange
from actions.stats_utils.data_extractions.extract_percent_info import getFilesWithAnimalsProportions
from actions.stats_utils.data_extractions.retrieve_CSV_data import retrieveDataFromCSV
from actions.stats_utils.graphics_data_generation.generate_animals_table_data import buildAnimalsTableData


def generateStatsPDF(folder, filenames, predictions_results, addresses, csv_path=None):
    # Extract data
    predictedclass = predictions_results["predictions"]
    predictedCount = predictions_results["counts"]
    date_objs: list[datetime.datetime] = predictions_results["dates"]
    species_set = set(predictedclass)

    # Get existing CSV data if provided
    existing_csv_predictions = None
    if csv_path:
        existing_csv_predictions = retrieveDataFromCSV(csv_path)  

    # Calculate stats
    num_videos = len(filenames)
    num_with_animals, percent_with_animals = getFilesWithAnimalsProportions(num_videos, predictedclass)

    # Dates
    start_date_str, end_date_str, total_days = getDatesRange(date_objs)

    # City/address
    city = getCity(addresses[0]) if addresses else "Unknown location"

    # Matplotlib graph
    # Dynamically set figure height based on number of dates (min 3, max 15 inches)
    MAX_DATES_PER_GRAPH = 50
    if date_objs:
        min_date = min(date_objs).date()
        max_date = max(date_objs).date()
        all_dates = [min_date]
        while all_dates[-1] < max_date:
            all_dates.append(all_dates[-1] + (max_date - min_date).__class__(1))
    else:
        all_dates = []
    # Split all_dates into chunks of MAX_DATES_PER_GRAPH
    def chunk_dates(dates, n):
        return [dates[i:i+n] for i in range(0, len(dates), n)]
    date_chunks = chunk_dates(all_dates, MAX_DATES_PER_GRAPH) if all_dates else []
    logging.info(f"Generating PDF with {len(date_chunks)} graph(s) for {len(all_dates)} date(s)")

    # PDF generation
    data_folder = os.path.join(folder, "data")
    os.makedirs(data_folder, exist_ok=True)
    doc = SimpleDocTemplate(os.path.join(data_folder, "stats.pdf"), pagesize=letter)
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

    # --- Add one graph per chunk of dates ---
    if "empty" in species_set:
        species_set.remove("empty")
    if "undefined" in species_set:
        species_set.remove("undefined")
    if "vehicle" in species_set:
        species_set.remove("vehicle")
    species_colors = {s: plt.cm.tab20(i) for i, s in enumerate(sorted(species_set))}
    hours = list(range(24))
    if date_chunks:
        for chunk_idx, chunk_dates_list in enumerate(date_chunks):
            chunk_dates_list = sorted(chunk_dates_list, reverse=True)
            num_dates = len(chunk_dates_list)
            fig_height = min(2 + (num_dates * 0.12), 8)
            plt.figure(figsize=(9, fig_height))
            # Plot points for this chunk only
            for species in species_set:
                indices = [i for i, s in enumerate(predictedclass) if s == species and date_objs[i].date() in chunk_dates_list]
                if not indices:
                    continue
                y = [date_objs[i].date() for i in indices]
                x = [date_objs[i].hour + date_objs[i].minute/60.0 for i in indices]
                plt.scatter(x, y, label=species, color=species_colors[species])
            plt.xlabel("Hour of Day")
            plt.ylabel("Date")
            plt.title(f"Detections by Species (dates {chunk_dates_list[-1]} to {chunk_dates_list[0]})")
            plt.xlim(0, 24)
            plt.xticks(hours, [f"{h:02d}:00" for h in hours], rotation=45)
            plt.yticks(chunk_dates_list, [d.strftime("%m-%d") for d in chunk_dates_list])
            plt.ylim(chunk_dates_list[0] + (chunk_dates_list[-1] - chunk_dates_list[0]).__class__(1),
                     chunk_dates_list[-1] - (chunk_dates_list[-1] - chunk_dates_list[0]).__class__(1))
            plt.grid(True, which='both', axis='both', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
            plt.legend(fontsize=8)
            plt.tight_layout()
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='PNG', dpi=150)
            plt.close()
            img_buffer.seek(0)
            img_width = 500
            img_height = int(fig_height * 72)
            img = Image(img_buffer, width=img_width, height=img_height)
            elements.append(img)
            elements.append(Spacer(1, 24))
    else:
        # No dates, add a placeholder
        elements.append(Paragraph("No detections to plot.", styles['Normal']))

    doc.build(elements)
