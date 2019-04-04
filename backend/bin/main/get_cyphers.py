import csv
import re

from os import path, remove
from urllib import request

from main.helpers.Combiner import Combiner


def download_file(mac_vendor_url):
    file_name = mac_vendor_url.split("/")[-1]
    request.urlretrieve(mac_vendor_url, file_name)
    return file_name


def is_header(line_counter):
    return line_counter == 0


def calculate_hex(hex_list):
    first_value = int(hex_list[0], 16) * pow(16, 2)
    second_value = int(hex_list[1], 16)
    return first_value + second_value


def write_rows(line_counter, output_file, row):
    if not is_header(line_counter):
        try:
            cipher_suite_number = calculate_hex(row["Value"].split(","))
            description = row["Description"]
            recommended = row["Recommended"]
            line = Combiner.combine_fields([cipher_suite_number, description, recommended])
            write_line(output_file, line)
        except:
            pass
    return line_counter + 1


def write_line(output_file, line):
    output_file.write(line + "\n")


def main():
    mac_vendor_url = "https://www.iana.org/assignments/tls-parameters/tls-parameters-4.csv"
    file_name = path.join(".", download_file(mac_vendor_url))
    destination_file = path.join("..", "files", "cipher_suites.csv")

    with \
            open(file_name, mode="r", encoding='utf-8') as csv_file, \
            open(destination_file, mode='w', encoding='utf-8') as output_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')

        header = "cipher_suite_number,description,recommended"
        write_line(output_file, header)
        line_counter = 0
        for row in csv_reader:
            line_counter = write_rows(line_counter, output_file, row)

    remove(file_name)


main()
