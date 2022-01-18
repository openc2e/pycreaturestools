import itertools
import re

from creaturestools._io_utils import *


def _descramble(buf):
    buf = bytearray(buf)
    key = 0x5
    for i in range(len(buf)):
        buf[i] ^= key
        key = (key + 0xC1) % 256
    return buf.decode("cp1252")


def _scramble(script):
    buf = bytearray(script.encode("cp1252"))
    key = 0x5
    for i in range(len(buf)):
        buf[i] ^= key
        key = (key + 0xC1) % 256
    return bytes(buf)


def mngscript_get_wave_names(script):
    nocomments = re.sub(r"//.*", "", script)
    wavenames = re.findall("[^\w]Wave\(\s*([^\)]+)\s*\)", nocomments)
    uniquewavenames = []
    for name in wavenames:
        if name in uniquewavenames:
            continue
        uniquewavenames.append(name)
    return uniquewavenames


def read_mng_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as f:
        num_samples = read_u32le(f)

        script_position = read_u32le(f)
        expected_position = 12 + 8 * num_samples
        if script_position != expected_position:
            raise Expected(
                "Expected script to be at position {}, but got {}".format(
                    expected_position, script_position
                )
            )

        script_length = read_u32le(f)
        expected_position += script_length

        sample_lengths = []
        for _ in range(num_samples):
            position = read_u32le(f)
            if position != expected_position:
                raise Exception(
                    "Expected sample to be at position {}, but got {}".format(
                        expected_position, position
                    )
                )
            length = read_u32le(f)
            sample_lengths.append(length)
            expected_position += length

        script = _descramble(read_exact(f, script_length))
        samples = []
        for length in sample_lengths:
            wav_header = b"RIFF" + struct.pack("<I", length + 4) + b"WAVEfmt "
            samples.append(wav_header + read_exact(f, length))

        namedsamples = {}
        wavenames = mngscript_get_wave_names(script)
        for i, (name, sample) in enumerate(itertools.zip_longest(wavenames, samples)):
            if name:
                namedsamples[name] = sample
            else:
                namedsamples["__unknown{}".format(i)] = sample

        return (script, namedsamples)


def write_mng_file(fname_or_stream, script, fileloaderfunc):
    with open_if_not_stream(fname_or_stream, "wb") as f:
        sample_names = mngscript_get_wave_names(script)
        samples = []
        for name in sample_names:
            data = fileloaderfunc(name + ".wav")
            if data[:4] != b"RIFF" or data[8:16] != b"WAVEfmt ":
                raise Exception(
                    "Expected sample data to start with b'RIFF'...b'WAVEfmt ', but got {}".format(
                        data[:16]
                    )
                )
            samples.append(data[16:])

        script = _scramble(script)

        write_u32le(f, len(samples))
        script_position = 12 + len(samples) * 8
        write_u32le(f, script_position)
        write_u32le(f, len(script))

        sample_position = script_position + len(script)
        for sample in samples:
            write_u32le(f, sample_position)
            write_u32le(f, len(sample))
            sample_position += len(sample)

        write_all(f, script)
        for sample in samples:
            write_all(f, sample)
