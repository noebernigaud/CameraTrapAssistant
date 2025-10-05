import matplotlib
import datetime
import io
from reportlab.platypus import Image

matplotlib.use('agg')   
import matplotlib.pyplot as plt

def generateObservationsByTimeGraph(species_set: list[str], predictedclass: list[str], date_objs: list[datetime.datetime], species_colors: dict[str, str], chunk_dates_list: list[datetime.date]):
    hours = list(range(24))
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
    return Image(img_buffer, width=img_width, height=img_height)

def getDatesChunksForObservationsByTimeGraphs(date_objs: list[datetime.datetime]):
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
    return chunk_dates(all_dates, MAX_DATES_PER_GRAPH) if all_dates else []