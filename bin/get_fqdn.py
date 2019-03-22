import socket
import csv


def is_header(line_number):
    return line_number == 0


def get_fqdns(fqdns, packet):
    src_ip = packet[0]
    dst_ip = packet[1]
    get_fqdn(fqdns, src_ip)
    get_fqdn(fqdns, dst_ip)


def get_fqdn(fqdns, ip_addr):
    if ip_addr in fqdns:
        return
    try:
        fqdns[ip_addr] = socket.getfqdn(ip_addr)
    except socket.herror:
        pass


def main():
    with open('ips.csv', mode="r", encoding='utf-8') as capture:
        fqdns = dict()
        capture_reader = csv.reader(capture, delimiter=',')
        line_counter = 0
        for packet in capture_reader:
            if not is_header(line_counter):
                get_fqdns(fqdns, packet)

            line_counter += 1

    for location in fqdns:
        print(location + " --> " + fqdns[location])


main()
