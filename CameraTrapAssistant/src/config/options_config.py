from dataclasses import dataclass

@dataclass
class OptionsConfig:
    generate_data: bool
    generate_stats: bool
    move_empty: bool
    move_undefined: bool
    rename_files: bool
    add_gps: bool
    prediction_threshold: float
    get_gps_from_each_file: bool
    use_gps_only_for_data: bool
    combine_with_data: bool
    time_offset: str  # 'auto' or timezone offset like 'UTC+02:00'