import struct
import unittest

from arsc_decoder import decode_arsc


def _make_string_pool(strings: list[str], utf8: bool = True) -> bytes:
    """Build a minimal valid ResStringPool chunk for unit testing."""
    flags = (1 << 8) if utf8 else 0
    encoded = []
    offsets = []
    cur = 0
    for s in strings:
        offsets.append(cur)
        if utf8:
            b = s.encode("utf-8")
            item = bytes([len(s), len(b)]) + b + b"\x00"
        else:
            b = s.encode("utf-16-le")
            item = struct.pack("<H", len(s)) + b + b"\x00\x00"
        encoded.append(item)
        cur += len(item)
    blob = b"".join(encoded)
    while len(blob) % 4 != 0:
        blob += b"\x00"
    header_size = 28
    strings_start = header_size + 4 * len(strings)
    total_size = strings_start + len(blob)
    header = struct.pack("<HHIIIIII", 0x0001, header_size, total_size, len(strings), 0, flags, strings_start, 0)
    # Wait: header is 28 bytes = 2+2+4 + 5*4 = 28 bytes (8 fields? No: type(H), hdr(H), size(I), strCnt(I), styleCnt(I), flags(I), strStart(I), styleStart(I) = 2+2+24 = 28)
    off_table = struct.pack(f"<{len(strings)}I", *offsets) if strings else b""
    return header + off_table + blob


class TestArscDecoder(unittest.TestCase):
    def test_decodes_utf8_string_and_array_resources(self) -> None:
        global_pool = _make_string_pool(["Hello\nWorld", "Line A", "Line B"], utf8=True)
        type_pool = _make_string_pool(["string", "array"], utf8=True)
        key_pool = _make_string_pool(["greeting", "litany_items"], utf8=True)

        # Build two ResTable_type chunks (type_id=1 for string, type_id=2 for array)
        # type 1: 1 entry (index 0 -> key 0, RES_VALUE string=0)
        entry1 = struct.pack("<HHIBBH", 8, 0, 0, 8, 0, 0x03)  # incomplete? Let's pack Res_value: size(H)=8, res0(B)=0, dataType(B)=3, data(I)=0
        entry1 = struct.pack("<HHI", 8, 0, 0) + struct.pack("<HBBI", 8, 0, 3, 0)
        t1_hdr_size = 84
        t1_entries_start = t1_hdr_size + 4
        t1_total = t1_entries_start + len(entry1)
        t1_hdr = struct.pack("<HHIIBBHI", 0x0201, t1_hdr_size, t1_total, 1, 0, 0, 0, 1)
        # pad config (48 bytes) + entriesStart is at offset 20 in ResTable_type!
        # Let's build exact ResTable_type header (84 bytes):
        # type(H), headerSize(H), size(I), id(B), flags(B), reserved(H), entryCount(I), entriesStart(I), config(64 bytes) -> 2+2+4+1+1+2+4+4+64 = 84
        t1_hdr = struct.pack("<HHIIBBHII", 0x0201, 84, t1_total, 1, 0, 0, 1, t1_entries_start, 0)
        # Wait: entriesStart is 1 I, config is 64 bytes -> let's use b"\x00" * 64
        t1_hdr = struct.pack("<HHIBBHII", 0x0201, 84, t1_total, 1, 0, 0, 1, t1_entries_start) + (b"\x00" * 64)
        t1_chunk = t1_hdr + struct.pack("<I", 0) + entry1

        # type 2: 1 complex map entry (index 0 -> key 1, parent=0, count=2, items -> global_pool[1], global_pool[2])
        map_hdr = struct.pack("<HHIII", 16, 1, 1, 0, 2)  # size=16, flags=1(COMPLEX), key=1, parent=0, count=2
        map_item1 = struct.pack("<IHBBI", 0x01000001, 8, 0, 3, 1)
        map_item2 = struct.pack("<IHBBI", 0x01000002, 8, 0, 3, 2)
        entry2 = map_hdr + map_item1 + map_item2
        t2_entries_start = 84 + 4
        t2_total = t2_entries_start + len(entry2)
        t2_hdr = struct.pack("<HHIBBHII", 0x0201, 84, t2_total, 2, 0, 0, 1, t2_entries_start) + (b"\x00" * 64)
        t2_chunk = t2_hdr + struct.pack("<I", 0) + entry2

        # Package chunk (ResTable_package header = 288 bytes)
        pkg_hdr_size = 288
        name_utf16 = "com.example".encode("utf-16-le").ljust(256, b"\x00")
        pkg_body = type_pool + key_pool + t1_chunk + t2_chunk
        pkg_total = pkg_hdr_size + len(pkg_body)
        # ResTable_package: type(H=0x0200), hdrSize(H=288), size(I), id(I=0x7f), name(256B), typeStrings(I), lastPublicType(I), keyStrings(I), lastPublicKey(I), typeIdOffset(I)
        type_strings_off = pkg_hdr_size
        key_strings_off = pkg_hdr_size + len(type_pool)
        pkg_hdr = struct.pack("<HHII", 0x0200, pkg_hdr_size, pkg_total, 0x7F) + name_utf16 + struct.pack(
            "<IIIII", type_strings_off, 2, key_strings_off, 2, 0
        )
        pkg_chunk = pkg_hdr + pkg_body

        # ResTable header (12 bytes)
        table_total = 12 + len(global_pool) + len(pkg_chunk)
        table_hdr = struct.pack("<HHII", 0x0002, 12, table_total, 1)
        arsc_bytes = table_hdr + global_pool + pkg_chunk

        result = decode_arsc(arsc_bytes)
        self.assertEqual(result["strings"]["greeting"]["value"], "Hello\nWorld")
        self.assertEqual(result["strings"]["greeting"]["id"], "0x7f010000")
        self.assertEqual(result["arrays"]["litany_items"]["items"], ["Line A", "Line B"])
        self.assertEqual(result["arrays"]["litany_items"]["id"], "0x7f020000")


if __name__ == "__main__":
    unittest.main()
