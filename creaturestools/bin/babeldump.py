import sys

from creaturestools.pcaps import *


class AutoRepr:
    def __repr__(self):
        s = "<"
        s += type(self).__name__
        s += " "
        for i, (k, v) in enumerate(vars(self).items()):
            if i != 0:
                s += " "
            s += k
            s += "="
            s += repr(v)
        s += ">"
        return s


def warn_matches(name, actual, desired):
    if actual != desired:
        print(f"Warning: {name}: expected {repr(desired)} but got {repr(actual)}")


def check_matches(name, actual, desired):
    if not isinstance(desired, (list, tuple)):
        desired = (desired,)
    if all(actual != _ for _ in desired):
        raise Exception(f"Bad {name}: expected {repr(desired)} but got {repr(actual)}")


class NetBabelHeader(AutoRepr):
    pass


def parse_netbabel_header(f):
    header = NetBabelHeader()
    header.package_type = read_u32le(f)
    header.echo_load = list(read_exact(f, 8))
    header.user_id = read_u32le(f)
    header.user_hid = read_u16le(f)
    header.unknown2 = read_u16le(f)
    # if source == 'client':
    #     check_matches("NetBabelHeader.unknown2", header.unknown2, (0, 10))
    # else:
    #     assert False
    header.request_id = read_u32le(f)
    header.payload_length = read_u32le(f)
    header.unknown3 = read_u16le(f)
    # elif source == 'client':
    #     check_matches("NetBabelHeader.unknown3", header.unknown3, (0, 3))
    # else:
    #     assert False
    header.unknown4 = read_u16le(f)
    # elif source == 'client':
    #     check_matches("NetBabelHeader.unknown4", header.unknown4, 0)
    # else:
    #     assert False

    return header


def parse_net_line_response(f, header):
    class NetLineResponse(AutoRepr):
        pass

    class NetLineResponseServer(AutoRepr):
        pass

    header = NetLineResponse()

    header.unknown1 = read_u32le(f)
    check_matches("NetLineResponse.unknown1", header.unknown1, 0)
    header.unknown2 = read_u32le(f)
    check_matches("NetLineResponse.unknown2", header.unknown2, (0, 3))
    header.unknown3 = read_u32le(f)
    check_matches("NetLineResponse.unknown3", header.unknown3, (0, 1))

    header.length_of_remaining_data = read_u32le(f)
    header.unknown4 = read_u32le(f)
    check_matches("NetLineResponse.unknown4", header.unknown4, 1)
    header.unknown5 = read_u32le(f)
    check_matches("NetLineResponse.unknown5", header.unknown5, 1)
    header.number_servers = read_u32le(f)
    data_consumed = 16

    header.servers = []
    for _ in range(header.number_servers):
        server = NetLineResponseServer()
        header.servers.append(server)
        server.port = read_u32le(f)
        server.id = read_u32le(f)
        server.address = read_null_terminated_string(f)
        server.friendly_name = read_null_terminated_string(f)
        data_consumed += 8 + len(server.address) + len(server.friendly_name)

    check_matches("length of data", header.length_of_remaining_data, data_consumed)

    # check_matches("rest of data", f.read(), b"")
    return header


def parse_as_server(packets):
    r = TimestampedReader(packets)

    while r.peek():
        timestamp = r.current_timestamp
        header = parse_netbabel_header(r)
        print(header)

        if header.unknown2 == 34115:
            # this is most likely bad data
            raise Exception(
                "header.unknown2 = 34115, assuming from previous udp parse error"
            )
        check_matches(
            "NetBabelHeader.unknown2", header.unknown2, (0, 10, 11, 15647, 34115)
        )
        check_matches(
            "NetBabelHeader.unknown3", header.unknown3, (0, 1, 10, 11, 17684, 42840)
        )
        check_matches("NetBabelHeader.unknown4", header.unknown4, (0, 29455, 46318))

        if header.package_type == 0xA:
            # one of the messages types that doesn't use payload length in the header...
            msg = parse_net_line_response(r, header)
            print(msg)

        break

    # while packets:
    #     timestamp = packets[0][0]
    #     data = packets[0][1]

    # r = TimestampedReader(packets)
    # print(r.current_timestamp)
    # print(r.read(1))
    # print(r.read(1))
    # print(r.read(5))
    # print(r.current_timestamp)


def parse_as_client(packets):
    pass


def main():
    data = read_pcap_file(sys.argv[1])

    for stream_key, packets in data.items():
        if stream_key[0].split(":")[1] == "49152":
            # server
            print(stream_key)
            parse_as_server(packets)
        else:
            # client
            parse_as_client(packets)


if __name__ == "__main__":
    main()
