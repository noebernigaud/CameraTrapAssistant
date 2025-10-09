import numpy as np
import datetime
import os
import sys
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_extractions.extract_dates_info import getDatesRange
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from time_utils.cluster_datetimes import cluster_datetimes

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

def compute_hour_stats(hours):
    """Compute circular mean, std, and peak hour range for a list of hours."""
    if not hours:
        return "N/A", "N/A", "N/A"
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
    return peak_hours_str, hour_var_str, circ_std

def buildStatRow(species, indices, predictedclass, predictedCount, date_objs):
    species_dates = [date_objs[i] for i in indices]
    species_counts = [predictedCount[i] for i in indices]
    if species_dates:
        num_dates = len(set(d.date() for d in species_dates))
        max_count = max(species_counts) if species_counts else "N/A"
        clustered_obs = cluster_datetimes(species_dates)
        hours = [d.hour + d.minute/60.0 for d in clustered_obs]
        peak_hours_str, hour_var_str, _ = compute_hour_stats(hours)
    else:
        num_dates = 0
        peak_hours_str = hour_var_str = "N/A"
        max_count = "N/A"
    return [species, len(indices), num_dates, max_count, peak_hours_str, hour_var_str]

def buildPredictedStatRows(species_set: list[str], predictedclass: list[str], predictedCount: list[int], date_objs: list[datetime.datetime]):
    rows = []
    for species in sorted(species_set):
        indices = [i for i, s in enumerate(predictedclass) if s == species]
        row = buildStatRow(species, indices, predictedclass, predictedCount, date_objs)
        rows.append(row)
    return rows

def buildTotalRow(species_set: list[str], rows: list[any], predictedclass: list[str], date_objs: list[datetime.datetime]):
    from data_extractions.extract_dates_info import getDatesRange
    total_days = getDatesRange(date_objs)[2]
    total_files = sum(r[1] for r in rows)
    all_species_dates = []
    for species in sorted(species_set):
        indices = [i for i, s in enumerate(predictedclass) if s == species]
        all_species_dates.extend([date_objs[i] for i in indices])
    clustered_obs = cluster_datetimes(all_species_dates)
    hours = [d.hour + d.minute/60.0 for d in clustered_obs]
    total_peak_hours, total_hour_var, _ = compute_hour_stats(hours)
    return ["Total", total_files, total_days, "N/A", total_peak_hours, total_hour_var]