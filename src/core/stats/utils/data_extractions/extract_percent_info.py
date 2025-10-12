def getFilesWithAnimalsProportions(file_number, predictedclass):
    num_with_animals = sum(1 for p in predictedclass if p not in ["empty", "undefined", "vehicle"])
    percent_with_animals = round(100 * num_with_animals / file_number, 1) if file_number else 0
    return num_with_animals, percent_with_animals