from datetime import datetime

def cluster_datetimes(datetimes: list[datetime], max_gap_seconds=300):
    """Cluster datetimes within max_gap_seconds (default 5 min) and return cluster means."""
    if not datetimes:
        return []
    sorted_datetimes = sorted(datetimes)
    clusters = []
    current_cluster = [sorted_datetimes[0]]
    for dt in sorted_datetimes[1:]:
        if (dt - current_cluster[-1]).total_seconds() <= max_gap_seconds:
            current_cluster.append(dt)
        else:
            mean_dt = current_cluster[0] + (current_cluster[-1] - current_cluster[0]) / 2 if len(current_cluster) > 1 else current_cluster[0]
            clusters.append(mean_dt)
            current_cluster = [dt]
    if current_cluster:
        mean_dt = current_cluster[0] + (current_cluster[-1] - current_cluster[0]) / 2 if len(current_cluster) > 1 else current_cluster[0]
        clusters.append(mean_dt)
    return clusters