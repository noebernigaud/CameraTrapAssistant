import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import os
import matplotlib
import logging
import sys
import numpy as np

from actions.exifGPS import getCity
matplotlib.use('agg')
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.retrieveCSVData import retrieveDataFromCSV

def getDatesRange(date_objs: list[datetime.datetime]):
    if date_objs:
        start_date =  min(date_objs)
        end_date = max(date_objs)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        total_days = (end_date.date() - start_date.date()).days + 1
    else:
        start_date_str = end_date_str = total_days = "N/A"
    return start_date_str, end_date_str, total_days

def getFilesWithVideosProportions(file_number, predictedclass):
    num_with_animals = sum(1 for p in predictedclass if p not in ["empty", "undefined", "vehicle"])
    percent_with_animals = round(100 * num_with_animals / file_number, 1) if file_number else 0
    return num_with_animals, percent_with_animals

def buildAnimalsTableData(species_set: list[str], predictedclass: list[str], predictedCount: list[int], date_objs: list[datetime.datetime]):
    header = ["Species", "Files", "Days", "Max Count", "Peak Hours", "Hour Variability"]
    predicted_rows = buildPredictedStatRows(species_set, predictedclass, predictedCount, date_objs)
    total_row = buildTotalRow(species_set, predicted_rows, predictedclass, date_objs)
    # Separate out empty/undefined rows
    empty_row = next((r for r in predicted_rows if r[0] == "empty"), None)
    undefined_row = next((r for r in predicted_rows if r[0] == "undefined"), None)
    # Remove them from rows
    predicted_rows = [r for r in predicted_rows if r[0] not in ("empty", "undefined")]
    # Sort animal rows by number of files descending
    animal_rows = sorted([r for r in predicted_rows if r[0] not in ("vehicle",)], key=lambda r: r[1], reverse=True)
    return format_table_data(header, total_row, empty_row, undefined_row, animal_rows)

def make_paragraph_row(row, style):
    return [Paragraph(str(cell), style) for cell in row]

def format_table_data(header, total_row, empty_row, undefined_row, animal_rows):
    from reportlab.lib.styles import ParagraphStyle
    styles = getSampleStyleSheet()
    from reportlab.lib.enums import TA_CENTER
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=TA_CENTER)
    italic_style = ParagraphStyle('Italic', parent=styles['Normal'], fontName='Helvetica-Oblique', alignment=TA_CENTER)
    table_data = [header]
    table_data.append(make_paragraph_row(total_row, bold_style))
    if empty_row:
        empty_row[3] = "N/A"
        table_data.append(make_paragraph_row(empty_row, italic_style))
    if undefined_row:
        undefined_row[3] = "N/A"
        table_data.append(make_paragraph_row(undefined_row, italic_style))
    for r in animal_rows:
        table_data.append([str(cell) for cell in r])
    return table_data

def buildPredictedStatRows(species_set: list[str], predictedclass: list[str], predictedCount: list[int], date_objs: list[datetime.datetime]):
    rows = []
    for species in sorted(species_set):
        indices = [i for i, s in enumerate(predictedclass) if s == species]
        species_dates = [date_objs[i] for i in indices]
        species_counts = [predictedCount[i] for i in indices]
        if species_dates:
            num_dates = len(set(d.date() for d in species_dates))
            max_count = max(species_counts) if species_counts else "N/A"
            # Cluster observations within 5 minutes
            sorted_datetimes = sorted(species_dates)
            clustered_obs = []
            if sorted_datetimes:
                current_cluster = [sorted_datetimes[0]]
                for dt in sorted_datetimes[1:]:
                    if (dt - current_cluster[-1]).total_seconds() <= 300:  # 5 minutes
                        current_cluster.append(dt)
                    else:
                        mean_dt = current_cluster[0] + (current_cluster[-1] - current_cluster[0]) / 2 if len(current_cluster) > 1 else current_cluster[0]
                        clustered_obs.append(mean_dt)
                        current_cluster = [dt]
                # Add last cluster
                if current_cluster:
                    mean_dt = current_cluster[0] + (current_cluster[-1] - current_cluster[0]) / 2 if len(current_cluster) > 1 else current_cluster[0]
                    clustered_obs.append(mean_dt)
            hours = [d.hour + d.minute/60.0 for d in clustered_obs]
            if hours:
                hours_rad = np.array(hours) * 2 * np.pi / 24
                mean_sin = np.mean(np.sin(hours_rad))
                mean_cos = np.mean(np.cos(hours_rad))
                mean_angle = np.arctan2(mean_sin, mean_cos)
                if mean_angle < 0:
                    mean_angle += 2 * np.pi
                R = np.sqrt(mean_sin**2 + mean_cos**2)
                circ_std = np.sqrt(-2 * np.log(R)) * 24 / (2 * np.pi) if R > 0 else float('nan')
                sorted_hours = np.sort(hours)
                n = len(sorted_hours)
                if n > 1:
                    k = max(1, int(np.ceil(n * 0.5)))
                    min_width = 24
                    best_start = 0
                    for i in range(n):
                        j = (i + k) % n
                        if j > i:
                            width = sorted_hours[j-1] - sorted_hours[i]
                        else:
                            width = (sorted_hours[-1] - sorted_hours[i]) + (sorted_hours[j-1] - sorted_hours[0]) + 24
                        if width < min_width:
                            min_width = width
                            best_start = i
                    peak_start = sorted_hours[best_start]
                    peak_end = (peak_start + min_width) % 24
                    peak_start_str = f"{int(peak_start):02d}:{int((peak_start%1)*60):02d}"
                    peak_end_str = f"{int(peak_end):02d}:{int((peak_end%1)*60):02d}"
                    peak_hours_str = f"{peak_start_str} - {peak_end_str}"
                    hour_var_str = f"{circ_std:.1f} h" if not np.isnan(circ_std) else "N/A"
                else:
                    peak_hours_str = "N/A"
                    hour_var_str = "N/A"
            else:
                peak_hours_str = hour_var_str = "N/A"
        else:
            num_dates = 0
            peak_hours_str = hour_var_str = "N/A"
            max_count = "N/A"
        rows.append([
            species,
            len(indices),
            num_dates,
            max_count,
            peak_hours_str,
            hour_var_str
        ])
    return rows

def buildTotalRow(species_set: list[str], rows: list[any], predictedclass: list[str], date_objs: list[datetime.datetime]):
    # Prepare total row with stats
    total_days = getDatesRange(date_objs)[2]
    total_files = sum(r[1] for r in rows)
    all_species_dates = []
    for species in sorted(species_set):
        indices = [i for i, s in enumerate(predictedclass) if s == species]
        all_species_dates.extend([date_objs[i] for i in indices])
    if all_species_dates:
        # Cluster all observations within 5 minutes
        sorted_datetimes = sorted(all_species_dates)
        clustered_obs = []
        if sorted_datetimes:
            current_cluster = [sorted_datetimes[0]]
            for dt in sorted_datetimes[1:]:
                if (dt - current_cluster[-1]).total_seconds() <= 300:
                    current_cluster.append(dt)
                else:
                    mean_dt = current_cluster[0] + (current_cluster[-1] - current_cluster[0]) / 2 if len(current_cluster) > 1 else current_cluster[0]
                    clustered_obs.append(mean_dt)
                    current_cluster = [dt]
            if current_cluster:
                mean_dt = current_cluster[0] + (current_cluster[-1] - current_cluster[0]) / 2 if len(current_cluster) > 1 else current_cluster[0]
                clustered_obs.append(mean_dt)
        hours = [d.hour + d.minute/60.0 for d in clustered_obs]
        if hours:
            hours_rad = np.array(hours) * 2 * np.pi / 24
            mean_sin = np.mean(np.sin(hours_rad))
            mean_cos = np.mean(np.cos(hours_rad))
            mean_angle = np.arctan2(mean_sin, mean_cos)
            if mean_angle < 0:
                mean_angle += 2 * np.pi
            R = np.sqrt(mean_sin**2 + mean_cos**2)
            circ_std = np.sqrt(-2 * np.log(R)) * 24 / (2 * np.pi) if R > 0 else float('nan')
            sorted_hours = np.sort(hours)
            n = len(sorted_hours)
            if n > 1:
                k = max(1, int(np.ceil(n * 0.5)))
                min_width = 24
                best_start = 0
                for i in range(n):
                    j = (i + k) % n
                    if j > i:
                        width = sorted_hours[j-1] - sorted_hours[i]
                    else:  
                        width = (sorted_hours[-1] - sorted_hours[i]) + (sorted_hours[j-1] - sorted_hours[0]) + 24
                    if width < min_width:
                        min_width = width
                        best_start = i
                peak_start = sorted_hours[best_start]
                peak_end = (peak_start + min_width) % 24
                peak_start_str = f"{int(peak_start):02d}:{int((peak_start%1)*60):02d}"
                peak_end_str = f"{int(peak_end):02d}:{int((peak_end%1)*60):02d}"
                total_peak_hours = f"{peak_start_str}-{peak_end_str}"
            else:
                total_peak_hours = "N/A"
            total_hour_var = f"{circ_std:.1f} h" if not np.isnan(circ_std) else "N/A"
        else:
            total_peak_hours = total_hour_var = "N/A"
    else:
        total_peak_hours = total_hour_var = "N/A"
    return ["Total", total_files, total_days, "N/A", total_peak_hours, total_hour_var]


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
    num_with_animals, percent_with_animals = getFilesWithVideosProportions(num_videos, predictedclass)

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
