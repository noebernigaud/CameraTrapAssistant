import os
import logging

# Move videos categorized as 'vide' to 'empty' subfolder beside 'data'
def moveEmptyVideos(folder, filenames, predicted_classes):
    logging.info("Moving empty videos to 'empty/' subfolder...")
    empty_folder = os.path.join(folder, "empty")
    os.makedirs(empty_folder, exist_ok=True)
    for fname, pred in zip(filenames, predicted_classes):
        if str(pred).strip().lower() == "vide":
            try:
                dest = os.path.join(empty_folder, os.path.basename(fname))
                if not os.path.exists(dest):
                    os.rename(fname, dest)
            except Exception as e:
                logging.info(f"Could not move {fname} to empty/: {e}")

# Move videos categorized as 'indéfini' to 'undefined' subfolder beside 'data'
def moveUndefinedVideos(folder, filenames, predicted_classes):
    logging.info("Moving undefined videos to 'undefined/' subfolder...")
    undefined_folder = os.path.join(folder, "undefined")
    os.makedirs(undefined_folder, exist_ok=True)
    for fname, pred in zip(filenames, predicted_classes):
        if str(pred).strip().lower() == "indéfini":
            try:
                dest = os.path.join(undefined_folder, os.path.basename(fname))
                if not os.path.exists(dest):
                    os.rename(fname, dest)
            except Exception as e:
                logging.info(f"Could not move {fname} to undefined/: {e}")