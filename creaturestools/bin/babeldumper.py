import sys

from creaturestools.babel import *
from creaturestools.pcaps import *


def main():
    data = read_pcap_file(sys.argv[1])

    messages = []
    for stream_key, packets in data.items():
        src = stream_key[0]
        dest = stream_key[1]
        r = TimestampedReader(packets)
        if src.split(":")[1] == "49152":
            is_server = True
        else:
            is_server = False

        while r.peek():
            timestamp = r.current_timestamp
            if is_server:
                messages.append((timestamp, parse_netbabel_server_message(r)))
            else:
                messages.append((timestamp, parse_netbabel_client_message(r)))

    messages = sorted(messages, key=lambda _: _[0])
    for (ts, msg) in messages:
        print("{} {}".format(ts.isoformat(), msg))


if __name__ == "__main__":
    main()
