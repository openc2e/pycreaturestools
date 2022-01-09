import datetime
import io
import struct

from ._io_utils import *

PCAP_MAGIC_BE = b"\xa1\xb2\xc3\xd4"
PCAP_MAGIC_BE_NANOSECOND = b"\xa1\xb2\x3c\x4d"
PCAP_MAGIC_LE = b"\xd4\xc3\xb2\xa1"
PCAP_MAGIC_LE_NANOSECOND = b"\x4d\x3c\xb2\xa1"
PCAP_LINKLAYER_ETHERNET = 1
ETHERTYPE_IP = 8
ETHERTYPE_ARP = 0x608
IPPROTO_TCP = 6
IPPROTO_UDP = 17


def read_pcap_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        # parse PCAP file header
        magic = read_exact(f, 4)
        if magic != PCAP_MAGIC_LE:
            message = f"Expected {PCAP_MAGIC_LE}, but got {magic}"
            if magic == PCAP_MAGIC_LE_NANOSECOND:
                message += " (PCAP_MAGIC_LE_NANOSECOND)"
            elif magic == PCAP_MAGIC_BE:
                message += " (PCAP_MAGIC_BE)"
            elif magic == PCAP_MAGIC_BE_NANOSECOND:
                message += " (PCAP_MAGIC_BE_NANOSECOND)"
            raise NotImplementedError(message)
        header_version_major = read_u16le(f)
        header_version_minor = read_u16le(f)
        header_timezone_correction_seconds = read_s32le(f)
        header_sigfigs = read_u32le(f)
        header_max_length_packets = read_u32le(f)
        header_link_layer_type = read_u32le(f)

        if header_link_layer_type != PCAP_LINKLAYER_ETHERNET:
            raise NotImplementedError(
                f"Expected PCAP_LINKLAYER_ETHERNET, but got {header_link_layer_type}"
            )

        streams = {}
        while f.peek():
            # parse PCAP packet header
            pcap_ts_sec = datetime.datetime.fromtimestamp(read_u32le(f))
            pcap_ts_usec = read_u32le(f)
            pcap_timestamp = pcap_ts_sec + datetime.timedelta(microseconds=pcap_ts_usec)
            pcap_incl_len = read_u32le(f)
            pcap_orig_len = read_u32le(f)

            if pcap_incl_len != pcap_orig_len:
                raise NotImplementedError(
                    f"Expected incl_len {pcap_incl_len} to match orig_len {pcap_orig_len}"
                )

            i = io.BytesIO(read_exact(f, pcap_incl_len))

            # parse ethernet header
            def read_etheraddr_le(_):
                buf = read_exact(_, 6)
                return "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(*buf)

            ether_dest_host = read_etheraddr_le(i)
            ether_src_host = read_etheraddr_le(i)
            ether_packet_type = read_u16le(i)

            if ether_packet_type == ETHERTYPE_ARP:
                # skip it
                continue
            if ether_packet_type != ETHERTYPE_IP:
                raise NotImplementedError(
                    f"Expected ETHERTYPE_IP, but got {ether_packet_type}"
                )

            # parse IPv4 header
            def read_ipaddr_be():
                buf = read_exact(i, 4)
                return f"{buf[0]}.{buf[1]}.{buf[2]}.{buf[3]}"

            ip_version_and_header_length = read_u8(i)
            ip_version = (ip_version_and_header_length & 0b11110000) >> 4
            if ip_version != 4:
                raise NotImplementedError(f"Expected IP version 4, got {ip_version}")
            ip_header_length_quads = ip_version_and_header_length & 0b1111
            if ip_header_length_quads < 5:
                raise Exception(
                    f"Expected IP header length quads to be 5, got {ip_header_length_quads}"
                )
            if ip_header_length_quads > 5:
                raise NotImplementedError(
                    f"Expected IP header length quads to be 5, got {ip_header_length_quads}"
                )

            ip_dscp_and_ecn = read_u8(i)
            ip_total_length = read_u16be(i)
            ip_identification = read_u16be(i)
            # print(ip_identification)
            ip_flags_and_fragment_offset = read_u16be(i)
            ip_flags = (ip_flags_and_fragment_offset & 0b1110000000000000) >> 13
            ip_fragment_offset = ip_flags_and_fragment_offset & 0b1111111111111
            ip_ttl = read_u8(i)
            ip_protocol = read_u8(i)
            ip_header_checksum = read_u16be(i)  # TODO: should validate checksum?
            ip_source_ipaddr = read_ipaddr_be()
            ip_dest_ipaddr = read_ipaddr_be()

            if ip_protocol == IPPROTO_UDP:
                # skip it
                continue
            if ip_protocol != IPPROTO_TCP:
                raise NotImplementedError(f"Expected IPPROTO_TCP, got {ip_protocol}")
            if ip_fragment_offset:
                raise NotImplementedError(
                    f"Expected ip_fragment_offset to be 0, but got {ip_fragment_offset}"
                )
            if ip_total_length > pcap_incl_len - 14:
                raise Exception(
                    f"Expected ip_total_length {ip_total_length} to match pcap_incl_len {pcap_incl_len}"
                )
            ip_length_was_too_short = ip_total_length < pcap_incl_len - 14

            # parse TCP header
            tcp_source_port = read_u16be(i)
            tcp_dest_port = read_u16be(i)
            tcp_sequence_number = read_u32be(i)
            tcp_ack_number = read_u32be(i)

            tcp_data_offset_reserved_and_flags = read_u16be(i)
            tcp_data_offset_quads = (
                tcp_data_offset_reserved_and_flags & 0b1111000000000000
            ) >> 12
            tcp_reserved = (
                tcp_data_offset_reserved_and_flags & 0b0000111000000000
            ) >> 9
            tcp_flags = tcp_data_offset_reserved_and_flags & 0b111111111
            tcp_syn = bool(tcp_flags & 0b10)  # TODO: reset the stream if we see this?
            tcp_ack = bool(tcp_flags & 0b10000)
            if tcp_data_offset_quads < 5:
                raise Exception(
                    f"Expected TCP data offset quads to be >=5, but got {tcp_data_offset_quads}"
                )

            tcp_window_size = read_u16be(i)
            tcp_checksum = read_u16be(i)
            tcp_urgent_pointer = read_u16be(i)
            if tcp_data_offset_quads > 5:
                tcp_extra = read_exact(i, (tcp_data_offset_quads - 5) * 4)

            # read data
            data = i.read()
            if not data:
                continue
            if ip_length_was_too_short:
                if data == b"\x00" * len(data):
                    # meh it's fine, just skip it
                    continue
                else:
                    raise Exception(
                        f"Expected ip_total_length {ip_total_length} to match pcap_incl_len {pcap_incl_len}. Got TCP data: {data}"
                    )

            stream_key = (
                ip_source_ipaddr + ":" + str(tcp_source_port),
                ip_dest_ipaddr + ":" + str(tcp_dest_port),
            )
            if stream_key in streams:
                if tcp_syn:
                    raise NotImplementedError(
                        f"Stream {stream_key} already exists but got a packet with SYN set"
                    )
            else:
                streams[stream_key] = []

            streams[stream_key].append((pcap_timestamp, tcp_sequence_number, data))

    newstreams = {}
    # TCP streams: sort, validate sequence numbers, and remove duplicates
    for (stream_key, packets) in streams.items():
        packets = sorted(packets, key=lambda _: (_[1], -len(_[2])))
        newpackets = []
        last_sequence_number = None
        last_data = None
        for (ts, seq, data) in packets:
            if last_sequence_number is None:
                pass
            elif last_sequence_number == seq:
                min_length = min(len(data), len(last_data))
                if data[:min_length] != last_data[:min_length]:
                    raise Exception(
                        f"Expected duplicate packet data {data} to match existing packet data {last_data}"
                    )
                if len(data) > len(last_data):
                    # this seems right...
                    newpackets.append((ts, data[len(last_data) :]))
                    last_data = data
                continue
            elif last_sequence_number + len(last_data) > seq:
                # uh... assume we got some of this data already I guess?
                data = data[last_sequence_number + len(last_data) - seq :]
            elif last_sequence_number + len(last_data) < seq:
                newpackets.append(
                    (
                        None,
                        None,
                        None,
                        f"missing {seq - (last_sequence_number + len(last_data))} bytes",
                    )
                )
                # raise Exception(f"Expected sequence number {last_sequence_number + len(last_data)} but got {seq}")
            last_sequence_number = seq
            last_data = data
            newpackets.append((ts, data))
        newstreams[stream_key] = newpackets

    return newstreams


class TimestampedReader:
    def __init__(self, packets):
        self._packets = packets
        self._current_timestamp = self._packets[0][0]

    @property
    def current_timestamp(self):
        return self._packets[0][0]

    def peek(self):
        if self._packets:
            return self._packets[0][1]
        else:
            return b""

    def read(self, n):
        ret = b""
        while len(ret) < n:
            if not self._packets:
                raise Exception("Expected {} bytes, but only got {}".format(n, ret))
            need = n - len(ret)
            ret += self._packets[0][1][:need]
            self._packets[0] = (self._packets[0][0], self._packets[0][1][need:])
            if not self._packets[0][1]:
                self._packets.pop(0)
        return ret
