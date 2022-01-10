import datetime
import io

from ._io_utils import *
from .pray import read_pray_file


class _AutoRepr:
    def __repr__(self):
        s = "<"
        s += type(self).__name__
        s += " "

        def repr_helper(o):
            if isinstance(o, bytes) and len(o) > 50:
                return repr(o[:50]) + "..."
            if isinstance(o, tuple):
                return "(" + " ".join(repr_helper(_) + "," for _ in o) + ")"
            if isinstance(o, list):
                return "[" + ", ".join(map(repr_helper, o)) + "]"
            return repr(o)

        for i, (k, v) in enumerate(vars(self).items()):
            if i != 0:
                s += " "
            s += k
            s += "="
            s += repr_helper(v)
        s += ">"
        return s


def _check_matches(name, actual, desired):
    if not isinstance(desired, (list, tuple)):
        desired = (desired,)
    if all(actual != _ for _ in desired):
        raise AssertionError(
            f"Bad {name}: expected {repr(desired)} but got {repr(actual)}"
        )


class NetBabelHeader(_AutoRepr):
    pass


def parse_netbabel_header(f):
    header = NetBabelHeader()
    header.package_type = read_u32le(f)
    header.echo_load = "".join("{:02x}".format(_) for _ in read_exact(f, 8))
    header.user_id = read_u32le(f)
    header.user_hid = read_u16le(f)
    header.unknown1 = read_u16le(f)
    header.request_id = read_u32le(f)
    header.payload_length = read_u32le(f)
    header.unknown2 = read_u16le(f)
    header.unknown3 = read_u16le(f)

    return header


def parse_netbabel_server9_pray(f, header):
    class NetBabelServer9PrayMessage(_AutoRepr):
        pass

    f = io.BytesIO(read_exact(f, header.payload_length))

    _check_matches("header.user_id", header.user_id, 0)
    _check_matches("header.user_hid", header.user_hid, 0)

    msg = NetBabelServer9PrayMessage()
    payload_length = read_u32le(f)
    msg.from_hid = read_u16le(f)
    maybe_uninitialized_stack_memory = read_exact(f, 2)
    msg.from_id = read_u32le(f)
    payload_length_minus_twenty_four = read_u32le(f)
    msg.unknown6 = read_u32le(f)
    msg.unknown7 = read_u32le(f)
    msg.unknown8 = read_u32le(f)
    msg.is_net_writ = read_u32le(f)
    msg.unknown10 = read_u32le(f)
    _check_matches("payload_length", payload_length, header.payload_length)
    _check_matches(
        "maybe_uninitialized_stack_memory",
        maybe_uninitialized_stack_memory,
        b"\xcc\xcc",
    )
    _check_matches(
        "payload_length_minus_twenty_four",
        payload_length_minus_twenty_four,
        payload_length - 24,
    )
    _check_matches("unknown6", msg.unknown6, 0)
    _check_matches("unknown7", msg.unknown7, 1)
    _check_matches("unknown8", msg.unknown8, 12)
    _check_matches("is_net_writ", msg.is_net_writ, (0, 1))
    msg.is_net_writ = bool(msg.is_net_writ)
    _check_matches("unknown10", msg.unknown10, 0)

    if not msg.is_net_writ:
        msg.pray = read_exact(f, payload_length - 36)
        msg.pray = read_pray_file(io.BytesIO(msg.pray))
    else:
        msg.channel = decode_creatures_string(read_u32le_prefixed_string(f))
        msg.script_id = read_u32le(f)
        msg.param1_type = read_u32le(f)
        _check_matches("param1_type", msg.param1_type, 2)  # CAOS string type
        msg.param1_value = decode_creatures_string(read_u32le_prefixed_string(f))
        msg.param2_type = read_u32le(f)
        _check_matches("param2_type", msg.param2_type, 2)  # CAOS string type
        msg.param2_value = decode_creatures_string(read_u32le_prefixed_string(f))
    _check_matches("rest of data", f.read(), b"")
    return msg


def parse_netbabel_server10_net_line_response(f, header):
    class NetBabelServer10NetLineResponse(_AutoRepr):
        pass

    class ServerInfo(_AutoRepr):
        pass

    # one of the message types that doesn't use payload length in the header...
    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelServer10NetLineResponse()
    msg.unknown1 = read_u32le(f)
    msg.unknown2 = read_u32le(f)
    msg.unknown3 = read_u32le(f)
    _check_matches("NetLineResponse.unknown1", msg.unknown1, 0)
    _check_matches("NetLineResponse.unknown2", msg.unknown2, (0, 3))
    _check_matches("NetLineResponse.unknown3", msg.unknown3, (0, 1))

    length_of_remaining_data = read_u32le(f)

    f = io.BytesIO(read_exact(f, length_of_remaining_data))

    msg.unknown4 = read_u32le(f)
    _check_matches("NetLineResponse.unknown4", msg.unknown4, 1)
    msg.unknown5 = read_u32le(f)
    _check_matches("NetLineResponse.unknown5", msg.unknown5, 1)
    msg.number_servers = read_u32le(f)

    msg.servers = []
    for _ in range(msg.number_servers):
        server = ServerInfo()
        msg.servers.append(server)
        server.port = read_u32le(f)
        server.id = read_u32le(f)
        server.address = decode_creatures_string(read_null_terminated_string(f))
        server.friendly_name = decode_creatures_string(read_null_terminated_string(f))

    _check_matches("rest of data", f.read(), b"")

    return msg


class NetBabelServer13Message(_AutoRepr):
    pass


def parse_netbabel_server13(f, header):
    # in response to client16
    # same as server15?
    # "yes, you will receive notifications for user (whose-wanted registry)"?

    f = io.BytesIO(read_exact(f, header.payload_length))

    msg = NetBabelServer13Message()
    payload_length = read_u32le(f)
    _check_matches("payload_length", payload_length, header.payload_length)
    msg.user_id = read_u32le(f)
    msg.user_hid = read_u16le(f)
    maybe_uninitialized_stack_memory = read_exact(f, 2)
    _check_matches("user_id", msg.user_id, header.user_id)
    _check_matches("user_hid", msg.user_hid, header.user_hid)
    _check_matches(
        "maybe_uninitialized_stack_memory",
        maybe_uninitialized_stack_memory,
        b"\xcc\xcc",
    )
    firstname_length = read_u32le(f)
    lastname_length = read_u32le(f)
    nickname_length = read_u32le(f)
    msg.firstname = decode_creatures_string(read_exact(f, firstname_length))
    msg.lastname = decode_creatures_string(read_exact(f, lastname_length))
    msg.nickname = decode_creatures_string(read_exact(f, nickname_length))

    _check_matches("rest of data", f.read(), b"")
    return msg


def parse_netbabel_server14(f, header):
    class NetBabelServer14Message(_AutoRepr):
        pass

    f = io.BytesIO(read_exact(f, header.payload_length))

    msg = NetBabelServer14Message()
    msg.payload_length = read_u32le(f)
    msg.user_id = read_u32le(f)
    msg.user_hid = read_u16le(f)
    msg.unknown1 = read_u16le(f)
    _check_matches("unknown1", msg.unknown1, 52428)
    firstname_length = read_u32le(f)
    lastname_length = read_u32le(f)
    nickname_length = read_u32le(f)
    msg.firstname = decode_creatures_string(read_exact(f, firstname_length))
    msg.lastname = decode_creatures_string(read_exact(f, lastname_length))
    msg.nickname = decode_creatures_string(read_exact(f, nickname_length))

    _check_matches("rest of data", f.read(), b"")

    return msg


def parse_netbabel_server15_net_unik_response(f, header):
    class NetBabelServer15UnikResponse(_AutoRepr):
        pass

    f = io.BytesIO(read_exact(f, header.payload_length))

    msg = NetBabelServer15UnikResponse()
    payload_length = read_u32le(f)
    _check_matches("payload_length", payload_length, header.payload_length)
    msg.user_id = read_u32le(f)
    msg.user_hid = read_u16le(f)
    _check_matches("user_id", msg.user_id, header.user_id)
    _check_matches("user_hid", msg.user_hid, header.user_hid)
    maybe_uninitialized_stack_memory = read_exact(f, 2)
    _check_matches(
        "maybe_uninitialized_stack_memory",
        maybe_uninitialized_stack_memory,
        b"\xcc\xcc",
    )
    firstname_length = read_u32le(f)
    lastname_length = read_u32le(f)
    nickname_length = read_u32le(f)
    msg.firstname = decode_creatures_string(read_exact(f, firstname_length))
    msg.lastname = decode_creatures_string(read_exact(f, lastname_length))
    msg.nickname = decode_creatures_string(read_exact(f, nickname_length))

    _check_matches("rest of data", f.read(), b"")
    return msg


class NetBabelServer19UlinResponse(_AutoRepr):
    pass


def parse_netbabel_server19_net_ulin_response(f, header):
    # if the header is zeroes, user is offline
    _check_matches("payload_length", header.payload_length, 0)
    _check_matches("unknown1", header.unknown1, 0)
    _check_matches("unknown2", header.unknown2, (0, 10))
    _check_matches("unknown3", header.unknown3, 0)
    msg = NetBabelServer19UlinResponse()
    return msg


class NetBabelServer24StatResponse(_AutoRepr):
    pass


def parse_netbabel_server24_net_stat_response(f, header):
    # one of the message types that doesn't use payload length in the header...
    msg = NetBabelServer24StatResponse()
    msg.milliseconds_online = read_u32le(f)
    msg.users_online = read_u32le(f)
    msg.bytes_sent = read_u32le(f)
    msg.bytes_received = read_u32le(f)
    return msg


def parse_netbabel_server545_net_ruso_response(f, header):
    class NetBabelServer545RusoResponse(_AutoRepr):
        pass

    # returns user id+hid in header
    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelServer545RusoResponse()
    return msg


def parse_netbabel_server801_creature_history_response(f, header):
    class NetBabelServer801CreatureHistoryResponse(_AutoRepr):
        pass

    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelServer801CreatureHistoryResponse()
    return msg


def parse_netbabel_client9_pray(f, header):
    class NetBabelClient9PrayMessage(_AutoRepr):
        pass

    # one of the message types that doesn't _quite_ use payload length in the header...
    f = io.BytesIO(read_exact(f, header.payload_length + 8))

    msg = NetBabelClient9PrayMessage()
    msg.recipient_id = read_u32le(f)
    msg.recipient_hid = read_u32le(f)
    payload_length_minus_eight = read_u32le(f)
    _check_matches(
        "payload_length_minus_eight",
        payload_length_minus_eight,
        header.payload_length,
    )
    msg.from_hid = read_u32le(f)
    msg.from_id = read_u32le(f)
    _check_matches("from_hid", msg.from_hid, header.user_hid)
    _check_matches("from_id", msg.from_id, header.user_id)
    payload_length_minus_thirty_two = read_u32le(f)
    _check_matches(
        "payload_length_minus_thirty_two",
        payload_length_minus_thirty_two,
        payload_length_minus_eight - 24,
    )
    msg.unknown7 = read_u32le(f)
    msg.unknown8 = read_u32le(f)
    msg.unknown9 = read_u32le(f)
    msg.maybe_is_net_writ = read_u32le(f)
    msg.unknown11 = read_u32le(f)
    _check_matches("unknown7", msg.unknown7, 0)
    _check_matches("unknown8", msg.unknown8, 1)
    _check_matches("unknown9", msg.unknown9, 12)
    _check_matches("maybe_is_net_writ", msg.maybe_is_net_writ, 0)
    _check_matches("unknown11", msg.unknown11, 0)

    r = io.BytesIO(read_exact(f, payload_length_minus_thirty_two - 12))
    msg.pray = read_pray_file(r)
    _check_matches("rest of data", r.read(), b"")
    return msg


class NetBabelClient15NetUnikRequest(_AutoRepr):
    pass


def parse_netbabel_client15_net_unik_request(f, header):
    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelClient15NetUnikRequest()
    return msg


class NetBabelClient16Message(_AutoRepr):
    pass


def parse_netbabel_client16(f, header):
    # NetBabel client message type 16
    # guess it's just empty?
    # sent when configuring warp chamber to send to "Any on-line user", and followed by a NetBabelClient19UlinRequest
    # expects a server13 if message is expected

    _check_matches("payload_length", header.payload_length, 0)
    _check_matches("request_id", header.request_id, 0)
    msg = NetBabelClient16Message()
    return msg


class NetBabelClient17Message(_AutoRepr):
    pass


def parse_netbabel_client17(f, header):
    # NetBabel client message type 17
    # "remove user from whose-wanted list"?
    # net: whof, net: whoz

    _check_matches("payload_length", header.payload_length, 0)
    _check_matches("request_id", header.request_id, 0)
    msg = NetBabelClient17Message()
    return msg


class NetBabelClient19UlinRequest(_AutoRepr):
    pass


def parse_netbabel_client19_net_ulin_request(f, header):
    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelClient19UlinRequest()
    return msg


class NetBabelClient20Message(_AutoRepr):
    pass


def parse_netbabel_client20(f, header):
    # sent by client after "net: writ" when server responds with a server30 ... but what is the expected response?
    # one of the message types that doesn't use payload length in the header...
    _check_matches("payload_length", header.payload_length, 0)
    _check_matches("request_id", header.request_id, 0)
    _check_matches("unknown1", header.unknown1, 0)
    _check_matches("unknown2", header.unknown2, 2)
    _check_matches("unknown3", header.unknown3, 10)
    msg = NetBabelClient20Message()
    msg.unknown1 = read_u32le(f)
    _check_matches("unknown1", msg.unknown1, 14)
    return msg


class NetBabelClient24StatRequest(_AutoRepr):
    pass


def parse_netbabel_client24_net_stat_request(f, header):
    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelClient24StatRequest()
    return msg


class NetBabelClient30Message(_AutoRepr):
    pass


def parse_netbabel_client30(f, header):
    # sent by client when "net: writ" ... but what is the expected response?
    # one of the message types that doesn't use payload length in the header...
    _check_matches("payload_length", header.payload_length, 0)
    _check_matches("request_id", header.request_id, 0)
    _check_matches("unknown1", header.unknown1, 0)
    _check_matches("unknown2", header.unknown2, 1)
    _check_matches("unknown3", header.unknown3, 0)
    msg = NetBabelClient30Message()
    msg.recipient_id = read_u32le(f)
    msg.recipient_hid = read_u16le(f)
    msg.unknown1 = read_u16le(f)
    msg.unknown2 = read_u32le(f)
    _check_matches("unknown1", msg.unknown1, 0)
    _check_matches("unknown2", msg.unknown2, 2)
    return msg


class NetBabelClient37NetLineRequest(_AutoRepr):
    pass


def parse_netbabel_client37_net_line_request(f, header):
    # one of the message types that doesn't use payload length in the header...
    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelClient37NetLineRequest()
    msg.unknown1 = read_u32le(f)
    msg.unknown2 = read_u32le(f)
    msg.unknown3 = read_u32le(f)
    _check_matches("NetLineRequest.unknown1", msg.unknown1, (0, 1))
    _check_matches("NetLineRequest.unknown2", msg.unknown2, (0, 2))
    _check_matches("NetLineRequest.unknown3", msg.unknown3, 0)
    username_length = read_u32le(f)
    password_length = read_u32le(f)
    msg.username = decode_creatures_string(read_exact(f, username_length))
    msg.password = decode_creatures_string(read_exact(f, password_length))
    _check_matches("username nul ending", msg.username[-1], "\x00")
    _check_matches("password nul ending", msg.password[-1], "\x00")
    msg.username = msg.username[:-1]
    msg.password = msg.password[:-1]

    return msg


def parse_netbabel_client545_net_ruso_request(f, header):
    class NetBabelClient545RusoRequest(_AutoRepr):
        pass

    _check_matches("payload_length", header.payload_length, 0)
    msg = NetBabelClient545RusoRequest()
    return msg


def parse_netbabel_client801_creature_history(r, header):
    class NetBabelClient801CreatureHistory(_AutoRepr):
        pass

    r = io.BytesIO(read_exact(r, header.payload_length))

    msg = NetBabelClient801CreatureHistory()

    def timestamp_or_zero(s):
        if s == 0:
            return 0
        else:
            return datetime.datetime.fromtimestamp(s)

    msg.moniker = read_u32le_prefixed_string(r)
    istherehistory = read_u8(r)
    _check_matches("istherehistory", istherehistory, (0, 1))
    istherehistory = bool(istherehistory)

    class CreatureHistory(_AutoRepr):
        pass

    if istherehistory:
        msg.history = CreatureHistory()
        msg.history.gender = read_u32le(r)
        msg.history.genus = read_u32le(r)
        msg.history.variant = read_u32le(r)
        msg.history.crossovermutation = read_u32le(r)
        msg.history.crossoverpoints = read_u32le(r)
        _check_matches("gender", msg.history.gender, (1, 2))
        _check_matches("genus", msg.history.genus, 0)
        _check_matches("variant", msg.history.variant, tuple(range(0, 26)))
    else:
        msg.history = None

    class NetEvent(_AutoRepr):
        pass

    number_of_events = read_u32le(r)
    msg.events = []
    for _ in range(number_of_events):
        event = NetEvent()
        msg.events.append(event)

        # like GLST, without user text or photo block name or warp information

        event.type = read_u32le(r)
        event.world_time_in_ticks = read_u32le(r)
        event.creature_age_in_ticks = read_s32le(r)
        event.timestamp = timestamp_or_zero(read_u32le(r))
        event.creature_lifestage = read_s32le(r)
        event.parent1 = read_u32le_prefixed_string(r)
        event.parent2 = read_u32le_prefixed_string(r)
        # GLST: user text
        # GLST: PHOT block name
        event.world_name = read_u32le_prefixed_string(r)
        event.world_uid = read_u32le_prefixed_string(r)
        event.user_id = read_u32le_prefixed_string(r)
        # GLST: needs uploading
        # GLST: uploaded user text

        event.index = read_u32le(r)

    msg.creature_name = read_u32le_prefixed_string(r)

    msg.num_notes = read_u32le(r)
    msg.notes = []
    for i in range(msg.num_notes):
        msg.notes.append(read_u32le_prefixed_string(r))
        index = read_u32le(r)
        _check_matches("note index", index, i)

    _check_matches("rest of payload", r.read(), b"")

    return msg


def parse_netbabel_server_message(r):
    header = parse_netbabel_header(r)
    _check_matches("NetBabelHeader.unknown1", header.unknown1, (0, 10))
    _check_matches("NetBabelHeader.unknown2", header.unknown2, (0, 1, 10))
    _check_matches("NetBabelHeader.unknown3", header.unknown3, 0)

    if header.package_type == 9:
        # server message 9: PRAY message
        msg = parse_netbabel_server9_pray(r, header)
    elif header.package_type == 10:
        # server message 10: net: line response
        msg = parse_netbabel_server10_net_line_response(r, header)
    elif header.package_type == 13:
        # server message 13
        msg = parse_netbabel_server13(r, header)
    elif header.package_type == 14:
        # server message 14
        msg = parse_netbabel_server14(r, header)
    elif header.package_type == 15:
        # server message 15: net: unik response
        msg = parse_netbabel_server15_net_unik_response(r, header)
    elif header.package_type == 19:
        # server message 19: net: ulin response
        msg = parse_netbabel_server19_net_ulin_response(r, header)
    elif header.package_type == 24:
        # server message 24: net: stat response
        msg = parse_netbabel_server24_net_stat_response(r, header)
    elif header.package_type == 545:
        # server message 545: net: ruso response
        msg = parse_netbabel_server545_net_ruso_response(r, header)
    elif header.package_type == 801:
        # server message 801: creature history response
        msg = parse_netbabel_server801_creature_history_response(r, header)
    else:
        # server message 20: if you echo a client20 message back to the client, you get a client31 message in response
        # server message 30: if you echo a client30 message back to the client, you get a client20 message in response
        raise Exception(
            "Unknown message type {} (0x{:02x}), got {}".format(
                header.package_type, header.package_type, header
            )
        )

    msg.header = header
    return msg


def parse_netbabel_client_message(r):
    header = parse_netbabel_header(r)

    _check_matches("NetBabelHeader.unknown1", header.unknown1, (0, 10))
    _check_matches("NetBabelHeader.unknown2", header.unknown2, (0, 1, 2, 3))
    _check_matches("NetBabelHeader.unknown3", header.unknown3, (0, 10))

    if header.package_type == 9:
        # client message 9: PRAY
        msg = parse_netbabel_client9_pray(r, header)
    elif header.package_type == 15:
        # client message 15: net: unik request
        msg = parse_netbabel_client15_net_unik_request(r, header)
    elif header.package_type == 16:
        # client message 16
        msg = parse_netbabel_client16(r, header)
    elif header.package_type == 17:
        # client message 17
        msg = parse_netbabel_client17(r, header)
    elif header.package_type == 19:
        msg = parse_netbabel_client19_net_ulin_request(r, header)
    elif header.package_type == 20:
        msg = parse_netbabel_client20(r, header)
    elif header.package_type == 24:
        msg = parse_netbabel_client24_net_stat_request(r, header)
    elif header.package_type == 30:
        msg = parse_netbabel_client30(r, header)
    elif header.package_type == 37:
        # client message 37: net: line request
        msg = parse_netbabel_client37_net_line_request(r, header)
    elif header.package_type == 545:
        # client message 545: net: ruso request
        msg = parse_netbabel_client545_net_ruso_request(r, header)
    elif header.package_type == 801:
        # client message 801: creature history
        msg = parse_netbabel_client801_creature_history(r, header)
    else:
        # client message 20: in response to a server30 which is actually just an echoed client30
        # client message 30: something to do with net: writ
        # client message 31: in response to a server20 which is actually just an echoed client20
        raise Exception(
            "Unknown message type {} (0x{:02x}), got {}".format(
                header.package_type, header.package_type, header
            )
        )
    msg.header = header
    return msg
