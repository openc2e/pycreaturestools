import struct


class MFCReader:
    def __init__(self, f):
        self._f = f
        self._classmap = {}
        self._objects = [None]

    def register_class(self, name, klass):
        assert name not in self._classmap
        self._classmap[name] = klass

    def peek(self):
        return self._f.peek()

    def read(self, n):
        result = self._f.read(n)
        assert len(result) == n
        return result

    def read_s8(self):
        return struct.unpack("<b", self.read(1))[0]

    def read_u8(self):
        return struct.unpack("<B", self.read(1))[0]

    def read_u16le(self):
        return struct.unpack("<H", self.read(2))[0]

    def read_s32le(self):
        return struct.unpack("<i", self.read(4))[0]

    def read_u32le(self):
        return struct.unpack("<I", self.read(4))[0]

    def read_string(self):
        length = self.read_u8()
        if length == 0xFF:
            length = self.read_u16le()
            if length == 0xFFFF:
                length = self.read_u32le()
        return self.read(length)

    def read_object(self, class_requested=None):
        tag = self.read_u16le()
        if tag == 0x7FFF:
            # 32-bit tag
            raise NotImplementedError('32-bit "big" tag')
        if tag == 0:
            return None
        elif tag == 0xFFFF:
            # new class description
            schema_number = self.read_u16le()
            classname_length = self.read_u16le()
            classname = self.read(classname_length).decode("ascii")
            # print(f"{schema_number=} {classname_length=} {classname=}")

            if classname not in self._classmap:
                raise NotImplementedError(
                    'Found new class "{}", but don\'t know how to deserialize it'.format(
                        classname
                    )
                )

            # print('Found new class "{}"'.format(classname))
            self._objects.append(self._classmap[classname])
            # print("Giving it PID {}".format(len(self._objects) - 1))

            val = self._classmap[classname]()
            # print('Found object of type "{}"'.format(classname))
            self._objects.append(val)
            # print("Giving it PID {}".format(len(self._objects) - 1))
            val.read(self)
            return val
        elif tag & 0x8000:
            # existing class
            tag = tag & ~0x8000
            # print("Found object of existing class {}".format(tag))
            assert len(self._objects) >= tag
            val = self._objects[tag]()
            self._objects.append(val)
            # print("Giving it PID {}".format(len(self._objects) - 1))
            val.read(self)
            return val
        else:
            # existing object
            # print("Reference to existing object with PID {}".format(tag))
            assert len(self._objects) >= tag
            return self._objects[tag]
