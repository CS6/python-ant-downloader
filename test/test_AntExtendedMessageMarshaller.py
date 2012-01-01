import unittest
from gat.ant_stream_device import AntExtendedMessageMarshaller


class Test(unittest.TestCase):

    def setUp(self):
        self.marshaller = AntExtendedMessageMarshaller()

    def test_extract_extended_data(self):
        self.assertEquals(
            self.marshaller._extract_extended_data("B", "\x00\x03\x00\xFF\xBE\xEF\xFF"),
            "\xBE\xEF")
        self.assertEquals(
            self.marshaller._extract_extended_data("B", "\x00\x01\x00\xFF\xFF"),
            "")

    def test_remove_extended_data(self):
        self.assertEquals(
            self.marshaller._remove_extended_data("B", "\x00\x03\x00\xFF\xBE\xEF\xFF"),
            "\x00\x03\x00\xFF\xFF")
        self.assertEquals(
            self.marshaller._remove_extended_data("B", "\x00\x01\x00\xFF\xFF"),
            "\x00\x01\x00\xFF\xFF")

    def test_unmarshall(self):
        (sync, msg_id, args, extended_attrs) = self.marshaller.unmarshall("B", "\x00\x03\x00\xFF\xBE\xEF\xAD")
        self.assertEquals(msg_id, 0x00)
        self.assertEquals(args[0], 0xFF)
        self.assertEquals(len(args), 1)


# vim: et ts=4 sts=4 nowrap
