import platform
import subprocess
from os import path
from typing import Optional

import main.helpers.tshark_helper as tshark_helper
from main.helpers.environment_helper import EnvironmentHelper
from main.helpers.file import file_move_helper, file_name_helper, file_path_helper, file_read_helper
from main.helpers.file.file_name_helper import get_new_filename
from main.helpers.print_helper import PrintHelper


def run_tshark(filename) -> None:
    program_path = detect_platform()
    if program_path is None:
        error_text = "No wireshark folder found. Please install Wireshark into the standard folder"
        PrintHelper.print_error(error_text)
        return

    new_filename = get_new_filename(filename, "csv", "capture-")
    with open(new_filename, "w") as out_file:
        start_tshark(filename, out_file, program_path)
        return


def detect_platform() -> Optional[str]:
    program_path = None

    if platform.system() == "Windows":
        program_path = test_tshark_windows()

    elif platform.system() == "Linux":
        program_path = test_tshark_linux()

    return program_path


def test_tshark_windows() -> Optional[str]:
    windows_defaults = tshark_helper.get_windows_defaults()
    return_value = None

    if path.isfile(windows_defaults["x86"]):
        return_value = windows_defaults["x86"]

    elif path.isfile(windows_defaults["x64"]):
        return_value = windows_defaults["x64"]

    return return_value


def test_tshark_linux() -> Optional[str]:
    return_value = None
    if path.isfile("/usr/bin/tshark"):
        return_value = "tshark"

    return return_value


def start_tshark(filename, out_file, program_path) -> None:
    arguments = tshark_helper.get_arguments(filename)
    subprocess.run([program_path] + arguments, stdout=out_file)


def main() -> None:
    environment_helper = EnvironmentHelper()
    run(environment_helper.get_environment())


def run(environment_variables) -> None:
    config_name = "traffic-analyzer.conf"
    key = "pcap_location"
    pcap_path = file_read_helper.get_config_value(config_name, key)

    pcap_processed_path = environment_variables["pcap_processed_path"]
    csv_tmp_path = environment_variables["csv_tmp_path"]

    for file_path in file_path_helper.get_file_paths(pcap_path, file_name_helper.is_pcap_file):
        full_file_path = path.join(file_path["path"], file_path["filename"])
        run_tshark(full_file_path)
        file_move_helper.move_file(
            path.join(full_file_path),
            path.join(pcap_processed_path, file_path["filename"])
        )

    for file_path in file_path_helper.get_file_paths(pcap_path, file_name_helper.is_normal_csv_file):
        file_move_helper.move_file(
            path.join(file_path["path"], file_path["filename"]),
            path.join(csv_tmp_path, file_path["filename"])
        )


if __name__ == "__main__":
    main()
