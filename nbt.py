import struct

# The Named Binary Tag (NBT) format encodes primative and composite data
# structures into a binary stream.


class NBT:
    def __init__(self, data):
        self.data = data
        self.root = self.get_tag()

    def get_tag(self, tag_type=None):
        # This grabs the next tag (which might contains other tags so this is
        # called recursively) and returns a tuple of tag name and content.
        if tag_type is None:
            tag_type = self.get_byte()
            if tag_type != 0:
                tag_name = self.get_string()
            else:
                tag_name = ""
        else:
            tag_name = "*"

        if tag_type == 0:  # End
            return None
        elif tag_type == 1:  # Byte
            return (tag_name, self.get_byte())
        elif tag_type == 2:  # Short
            return (tag_name, self.get_short())
        elif tag_type == 3:  # Int
            return (tag_name, self.get_int())
        elif tag_type == 4:  # Long
            return (tag_name, self.get_long())
        elif tag_type == 5:  # Float
            return (tag_name, self.get_float())
        elif tag_type == 6:  # Double
            return (tag_name, self.get_double())
        elif tag_type == 7:  # ByteArray
            return (tag_name, self.get_array(self.get_byte))
        elif tag_type == 8:  # String
            return (tag_name, self.get_string())
        elif tag_type == 9:  # List (homogenous)
            list_type = self.get_byte()
            return (tag_name, self.get_array(lambda: self.get_tag(list_type)))
        elif tag_type == 10:  # Compound
            # This is effectively a dictionary because each child is a tag with
            # a unique name. We end when we get an END (type 0) tag.
            tag = {}
            while self.data:
                entry = self.get_tag()
                if entry is None:
                    break
                tag[entry[0]] = entry[1]
            return (tag_name, tag)
        elif tag_type == 11:  # IntArray
            return (tag_name, self.get_array(self.get_int))
        elif tag_type == 12:  # LongArray
            return (tag_name, self.get_array(self.get_long))
        else:
            raise Exception()

    def get(self, length):
        # gets next datum of the given length and updates self.data to point
        # to what's left
        datum, self.data = self.data[:length], self.data[length:]
        return datum

    def get_byte(self):
        return struct.unpack("b", self.get(1))[0]

    def get_short(self):
        return struct.unpack(">h", self.get(2))[0]

    def get_int(self):
        return struct.unpack(">i", self.get(4))[0]

    def get_long(self):
        return struct.unpack(">q", self.get(8))[0]

    def get_float(self):
        return struct.unpack(">f", self.get(4))[0]

    def get_double(self):
        return struct.unpack(">d", self.get(8))[0]

    def get_string(self):
        length = struct.unpack(">h", self.get(2))[0]
        if length:
            return self.get(length).decode("utf-8")
        else:
            return ""

    def get_array(self, getter):
        # We already know the type of the items in the array and so get passed
        # the appropriate getter (one of the self.get_ methods). But first we
        # need to get the size, which is the next Int in the data.
        size = self.get_int()
        return [getter() for i in range(size)]
