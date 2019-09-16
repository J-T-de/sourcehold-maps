import binascii
import logging
import struct

import compression
from structure_tools import Structure, Variable


class SimpleSection(Structure):
    size = Variable("size", "I")
    data = Variable("data", "B", size)

    def pack(self):
        self.size = len(self.data)

    def unpack(self):
        assert len(self.data) == self.size


class CompressedSection(Structure):
    uncompressed_size = Variable("us", "I")
    compressed_size = Variable("cs", "I")
    hash = Variable("hash", "I")
    data = Variable("data", "B", compressed_size)

    def pack(self):
        self.data = compression.COMPRESSION.compress(self.uncompressed)
        self.hash = binascii.crc32(self.uncompressed)
        self.uncompressed_size = len(self.uncompressed)
        self.compressed_size = len(self.data)

    def unpack(self):
        self.uncompressed = compression.COMPRESSION.decompress(self.data)
        assert len(self.data) == self.compressed_size
        assert len(self.uncompressed) == self.uncompressed_size
        assert binascii.crc32(self.uncompressed) == self.hash

    def get_data(self):
        if not hasattr(self, "uncompressed"):
            self.unpack()
        return self.uncompressed


class Preview(Structure):
    uncompressed_size = Variable("us", "I")
    compressed_size = Variable("cs", "I")
    hash = Variable("hash", "I")
    data = Variable("data", "B", compressed_size)

    def pack(self):
        self.data = compression.COMPRESSION.compress(self.uncompressed)
        self.hash = binascii.crc32(self.uncompressed)
        self.uncompressed_size = len(self.uncompressed)
        self.compressed_size = len(self.data)

    def unpack(self):
        self.uncompressed = compression.COMPRESSION.decompress(self.data)
        assert len(self.data) == self.compressed_size
        assert len(self.uncompressed) == self.uncompressed_size
        assert binascii.crc32(self.uncompressed) == self.hash

    def get_data(self):
        if not hasattr(self, "uncompressed"):
            self.unpack()
        return self.uncompressed


class Description(Structure):
    unknown1 = Variable("u1", "B", 4)
    unknown2 = Variable("u2", "B", 4)
    uncompressed_size = Variable("us", "I")
    compressed_size = Variable("cs", "I")
    hash = Variable("hash", "I")
    data = Variable("data", "B", compressed_size)

    def pack(self):
        self.data = compression.COMPRESSION.compress(self.uncompressed)
        self.hash = binascii.crc32(self.uncompressed)
        self.uncompressed_size = len(self.uncompressed)
        self.compressed_size = len(self.data)

    def unpack(self):
        self.uncompressed = compression.COMPRESSION.decompress(self.data)
        assert len(self.data) == self.compressed_size
        assert len(self.uncompressed) == self.uncompressed_size
        assert binascii.crc32(self.uncompressed) == self.hash

    def get_data(self):
        if not hasattr(self, "uncompressed"):
            self.unpack()
        return self.uncompressed


class MapSection(Structure):

    def __init__(self, buf, array_index, length):
        super().__init__(buf, array_index)
        self.length = length
        self.data = buf.read(length)

    def pack(self):
        self.length = len(self.data)

    def serialize_to_buffer(self, buf):
        self.pack()

        # note: we do not serialize length!
        prop = "data"
        bef = buf.tell()
        buf.write(self.data)
        aft = buf.tell()
        l = aft - bef
        logging.debug("serialized {:16s}. length: {:10d} before: {:10d},  after: {:10d}".format(
            prop,
            l,
            bef,
            aft
        ))


class CompressedMapSection(Structure):
    uncompressed_size = Variable("us", "I")
    compressed_size = Variable("cs", "I")
    hash = Variable("hash", "I")
    data = Variable("data", "B", compressed_size)

    def pack(self):
        self.data = compression.COMPRESSION.compress(self.uncompressed)
        self.hash = binascii.crc32(self.uncompressed)
        self.uncompressed_size = len(self.uncompressed)
        self.compressed_size = len(self.data)

    def unpack(self):
        self.uncompressed = compression.COMPRESSION.decompress(self.data)
        assert len(self.data) == self.compressed_size
        assert len(self.uncompressed) == self.uncompressed_size
        assert binascii.crc32(self.uncompressed) == self.hash

    def get_data(self):
        if not hasattr(self, "uncompressed"):
            self.unpack()
        return self.uncompressed


class Directory(Structure):
    _AMOUNT_OF_SECTIONS = 122
    length = Variable("l", "I")
    sections_count = Variable("sc", "I")
    u1 = Variable("u1", "I", 5)
    uncompressed_lengths = Variable("ul", "I", _AMOUNT_OF_SECTIONS)
    u2 = Variable("u2", "I", 28)
    section_lengths = Variable("sl", "I", _AMOUNT_OF_SECTIONS)
    u3 = Variable("u3", "I", 28)
    section_indices = Variable("si", "I", _AMOUNT_OF_SECTIONS)
    u4 = Variable("u4", "I", 28)
    section_compressed = Variable("com", "I", _AMOUNT_OF_SECTIONS)
    u5 = Variable("u5", "I", 28)
    section_offsets = Variable("so", "I", _AMOUNT_OF_SECTIONS)
    u6 = Variable("u6", "I", 28)
    u7 = Variable("u7", "I")

    def __init__(self, buf, array_size):
        super().__init__(buf, array_size)
        self.sections = []
        for i in range(self.sections_count):
            logging.debug("processing section {}".format(i))
            compressed = self.section_compressed[i] == 1
            length = self.section_lengths[i]
            if not compressed:
                self.sections.append(MapSection(self._buf, i, length))
            else:
                self.sections.append(CompressedMapSection(self._buf, i))

    def __getitem__(self, item):
        # access directory item by index
        if not item in self.section_indices:
            raise KeyError(item)
        i = self.section_indices.index(item)
        return self.sections[i]

    def __setitem__(self, key, value):
        # access directory item by index
        if not key in self.section_indices:
            raise KeyError(key)
        i = self.section_indices.index(key)
        self.sections[i] = value

    def unpack(self):
        for section in self.sections:
            section.unpack()

    def get_data(self):
        raise NotImplementedError()

    def pack(self):
        for section in self.sections:
            section.pack()

        # Lets keep things simple for now and not change compressed and indices
        zeroes = Directory._AMOUNT_OF_SECTIONS - len(self.sections)

        accum = 0

        self.sections_count = len(self.sections)
        for i in range(self.sections_count):
            s = self.sections[i]
            if s.__class__ == MapSection:
                self.uncompressed_lengths[i] = s.length
                self.section_lengths[i] = s.length
                self.section_compressed[i] = 0
            if s.__class__ == CompressedMapSection:
                self.uncompressed_lengths[i] = s.uncompressed_size
                self.section_lengths[i] = s.compressed_size + 12  # important!
                self.section_compressed[i] = 1

            self.section_offsets[i] = accum
            accum += self.section_lengths[i]

        for i in range(self.sections_count, Directory._AMOUNT_OF_SECTIONS):
            self.section_lengths[i] = 0
            self.uncompressed_lengths[i] = 0
            self.section_compressed[i] = 0
            self.section_indices[i] = 0
            self.section_offsets[i] = 0  # TODO check this

    def serialize_to_buffer(self, buf):
        self.pack()

        super().serialize_to_buffer(buf)

        for i in range(len(self.sections)):
            section = self.sections[i]
            logging.debug("serializing section {} with size {}".format(i, self.section_lengths[i]))
            section.serialize_to_buffer(buf)

    def dump_to_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        for i in range(len(self.sections)):
            write_to_file(os.path.join(path, str(self.section_indices[i])), self.sections[i].get_data())


import os


def write_to_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def _int_array_to_bytes(array):
    return b''.join(struct.pack("B", v) for v in array)


class Map(Structure):
    magic = Variable("magic", "I")
    preview_size = Variable("preview_size", "I")
    preview = Variable("preview", Preview)
    description_size = Variable("description_size", "I")
    description = Variable("description", Description)
    u1 = Variable("u1", SimpleSection)
    u2 = Variable("u2", SimpleSection)
    u3 = Variable("u3", SimpleSection)
    u4 = Variable("u4", SimpleSection)
    ud = Variable("ud", "B", 4)
    directory_size = Variable("ds", "I")
    directory = Variable("directory", Directory)

    def unpack(self):
        self.preview.unpack()
        self.description.unpack()
        # self.directory.unpack()

    def pack(self):
        self.preview.pack()
        self.description.pack()
        # self.directory.pack()

    def dump_to_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        dirpath = os.path.join(path, "sections")

        write_to_file(os.path.join(path, "preview"), self.preview.get_data())
        write_to_file(os.path.join(path, "description"), self.description.get_data())
        write_to_file(os.path.join(path, "u1"), _int_array_to_bytes(self.u1.get_data()))
        write_to_file(os.path.join(path, "u2"), _int_array_to_bytes(self.u2.get_data()))
        write_to_file(os.path.join(path, "u3"), _int_array_to_bytes(self.u3.get_data()))
        write_to_file(os.path.join(path, "u4"), _int_array_to_bytes(self.u4.get_data()))
        write_to_file(os.path.join(path, "ud"), _int_array_to_bytes(self.ud))
        self.directory.dump_to_folder(dirpath)