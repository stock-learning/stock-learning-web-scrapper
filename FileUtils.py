import os


def get_only_filename_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            return os.path.join(directory, file)


def directory_has_file(directory):
    return get_only_filename_in_directory(directory) != None
