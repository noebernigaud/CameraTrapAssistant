 # Rename each video to its creation date, get city and predicted animal
from pathlib import Path
import logging

def rename_videos_with_date_and_info(filenames, predicted_classes, dates):
    logging.info("Renaming videos with date and predicted animal...")
    for i, (file, pred, date) in enumerate(zip(filenames, predicted_classes, dates)):
        old_path = Path(file)
        ext = Path(file).suffix
        if not date:
            date_str = "unknown_date"
        else:
            # Format date en 2025.09.19__22h30
            date_str = date.strftime('%Y.%m.%d_%Hh%M')
        base_name = f"{date_str}__{pred}"

        # === Vérifier doublons ===
        counter = 0
        while True:
            # Suffixe si nécessaire : _1, _2, etc.
            suffix = f"_{counter}" if counter > 0 else ""
            new_name = f"{base_name}{suffix}{ext}"
            new_path = old_path.parent / new_name
            if not new_path.exists():    # pas encore pris → on peut l'utiliser
                break
            counter += 1

        # Renommer
        old_path.rename(new_path)
        filenames[i] = str(new_path)     # mettre à jour la liste