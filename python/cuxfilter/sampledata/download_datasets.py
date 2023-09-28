#!/usr/bin/env python3
import gzip
import tarfile
import shutil
import os.path
from collections import OrderedDict


def check_folder(dir_name):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def decompress_extract_data(file_path, base_dir):
    """
    identify file (tar, gzip etc and unzip/decompress)
    """

    extentions = OrderedDict(
        [("tar.gz", "tar gzip"), (".tgz", "tar gzip"), (".gz", "gzip")]
    )

    for ext in extentions.keys():
        if file_path.endswith(ext):
            file_ext = extentions[ext]
            break

    if file_ext == "tar gzip":
        with tarfile.open(file_path, mode="r:gz") as tar:

            def is_within_directory(directory, target):
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
                prefix = os.path.commonprefix([abs_directory, abs_target])
                return prefix == abs_directory

            def safe_extract(
                tar, path=".", members=None, *, numeric_owner=False
            ):
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")

                tar.extractall(path, members, numeric_owner=numeric_owner)

            safe_extract(tar, base_dir)
            tar.close()
        print("Extraction complete")
    elif file_ext == "gzip":
        with gzip.open(file_path, "rb") as f_in:
            with open(os.path.splitext(file_path)[0], "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print("Extraction complete")
    else:
        print("Nothing to decompress/extract")


def download_dataset(downloaded_filename, filename, url, base_dir):
    print("Dataset - " + filename)
    if not os.path.isfile(downloaded_filename):
        bash_cmd = "! wget" + " -O " + downloaded_filename + " " + url
        print(
            """
            Dataset not found. Run the following for downloading the dataset:
            """
            + bash_cmd
        )
    else:
        print("\ndataset already downloaded")
        if not os.path.isfile(filename):
            if filename != downloaded_filename:
                print("Extracting ....")
                decompress_extract_data(downloaded_filename, base_dir)


def datasets_check(*args, base_dir="./"):
    dir_name = base_dir

    check_folder(dir_name)

    url = {}
    downloaded_filename = {}
    filename = {}

    # mortgage dataset
    url[
        "mortgage"
    ] = "https://data.rapids.ai/viz-data/146M_predictions_v2.arrow.gz"
    downloaded_filename["mortgage"] = (
        dir_name + "/146M_predictions_v2.arrow.gz"
    )
    filename["mortgage"] = dir_name + "/146M_predictions_v2.arrow"

    # nyc taxi dataset
    url["nyc_taxi"] = "https://data.rapids.ai/viz-data/nyc_taxi.tar.gz"
    downloaded_filename["nyc_taxi"] = dir_name + "/nyc_taxi.tar.gz"
    filename["nyc_taxi"] = dir_name + "/nyc_taxi.csv"

    url[
        "auto_accidents"
    ] = "https://data.rapids.ai/viz-data/auto_accidents.arrow.gz"
    downloaded_filename["auto_accidents"] = (
        dir_name + "/auto_accidents.arrow.gz"
    )
    filename["auto_accidents"] = dir_name + "/auto_accidents.arrow"

    if len(args) == 0:
        for i in list(url.keys()):
            download_dataset(
                downloaded_filename[i], filename[i], url[i], base_dir
            )

    else:
        for i in args:
            download_dataset(
                downloaded_filename[i], filename[i], url[i], base_dir
            )
