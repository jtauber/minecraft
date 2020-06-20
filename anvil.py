import datetime
import struct
import zlib

from nbt import NBT

# Each region file (`r.X.Z.mca`) is in the Anvil format and consists of chunks
# each of which is the NBT format.
#
# reader = RegionReader(DIRECTORY)
# reader.get_chunk(cx, cz)


class RegionReader:
    def __init__(self, directory):

        self.directory = directory
        self.region_cache = {}
        self.chunk_cache = {}

    def get_chunk(self, cx, cz):

        if (cx, cz) not in self.chunk_cache:

            rx = cx // 32
            rz = cz // 32

            if (rx, rz) not in self.region_cache:
                filename = f"{self.directory}/r.{rx}.{rz}.mca"
                self.region_cache[(rx, rz)] = Region(filename)
            region = self.region_cache[(rx, rz)]

            location, sectors, timestamp = region.chunk_metadata(cx, cz)
            if sectors:
                self.chunk_cache[(cx, cz)] = NBT(
                    region.chunk_data(location, sectors)
                ).root[1]
            else:
                return {}

        chunk = self.chunk_cache[(cx, cz)]

        assert chunk["Level"]["xPos"] == cx
        assert chunk["Level"]["zPos"] == cz

        return chunk


class Region:
    def __init__(self, filename):

        try:
            self.file = open(filename, "rb")
        except FileNotFoundError:
            self.file = None

    def chunk_metadata(self, cx, cz):

        if self.file:

            offset = 4 * ((cx % 32) + (cz % 32) * 32)
            self.file.seek(offset)
            loc1, loc2, length = struct.unpack(">BHB", self.file.read(4))
            self.file.seek(offset + 4096)
            timestamp = datetime.datetime.fromtimestamp(
                struct.unpack(">L", self.file.read(4))[0]
            )

            return 65526 * loc1 + loc2, length, timestamp

        else:
            return 0, 0, 0

    def chunk_data(self, location, sectors):

        self.file.seek(4096 * location)
        raw_data = self.file.read(4096 * sectors)
        length, compression_type = struct.unpack(">LB", raw_data[:5])
        assert compression_type == 2
        data = zlib.decompress(raw_data[5 : length + 4])

        return data
