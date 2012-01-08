import unittest
import mock
import collections

from gant.ant_serial_dialect import *
from gant.ant_api import *

class TestSerialDialect(unittest.TestCase):

    def setUp(self):
        self.hardware = mock.Mock()
        self.dispatcher = mock.Mock()
        self.dialect = SerialDialect(self.hardware, self.dispatcher)

    def test_pack(self):
        self.dialect._exec(0x42, "BBB", (1, 0x20, 3))
        self.hardware.write.assert_called_with("\xa4\x03\x42\x01\x20\x03\xc7")
        self.dialect._exec(0x43, "BH", (1, 0x71ce))
        self.hardware.write.assert_called_with("\xa4\x03\x43\x01\xce\x71\x5a")

    def test_generate_checkum(self):
        self.assertEquals(0xff, self.dialect.generate_checksum("\xa5\x5a"))
        self.assertEquals(0x00, self.dialect.generate_checksum("\xa5\x5a\xff"))

    def test_validate_checksum(self):
        self.assertTrue(self.dialect.validate_checksum("\xa5\x5a\xff"))
        self.assertTrue(self.dialect.validate_checksum("\xa5\x5a\xff\x00"))
        self.assertFalse(self.dialect.validate_checksum("\xa5\x5a\xff\x01"))        

    def test_enhanced_method(self):
        self.dialect.reset_system()
        self.hardware.write.assert_called_with("\xa4\x01\x4a\x00\xef")
        
    def test_unpack(self):
        (msg_id, msg_args) = self.dialect.unpack("\xa4\x06\x54\x08\x03\xff\xaa\xbb\x00\x13")
        self.assertEquals(0x54, msg_id)
        self.assertEquals(3, msg_args.max_networks)
        self.assertEquals(8, msg_args.max_channels)
        (msg_id, msg_args) = self.dialect.unpack("\xa4\x05\x51\x01\x02\x03\x04\x05\xf1")
        self.assertEquals(0x51, msg_id)
        self.assertEquals(0x0302, msg_args.device_number)


class TestMessageMatcher(unittest.TestCase):
    
    def test_match(self):
        msg1 = (0x40, collections.namedtuple("Message", "message_code")(0x21))
        msg2 = (0x40, collections.namedtuple("Message", "message_code")(0x20))
        self.assertFalse(MessageMatcher(0x41).match(msg1))
        self.assertTrue(MessageMatcher(0x40).match(msg1))
        self.assertFalse(MessageMatcher(0x40, message_code=0x20).match(msg1))
        self.assertTrue(MessageMatcher(0x40, message_code=0x20).match(msg2))


class TestMatchingListener(unittest.TestCase):

    def test_event(self):
        future = Future()
        dialect = mock.Mock()
        matcher = mock.Mock()
        validator = mock.Mock()
        dispatcher = mock.Mock()
        dialect.unpack.return_value = (0x00, ())
        matcher.match.return_value = False
        validator.return_value = True
        matching_listener = MatchingListener(dialect, future, matcher, validator)
        matching_listener.on_message(dispatcher, None)
        self.assertFalse(future._event.is_set())
        self.assertTrue(future._result is None)
        self.assertFalse(future._exception)
        self.assertFalse(dispatcher.remove_listener.called)
        matcher.match.return_value = True
        matching_listener.on_message(dispatcher, None)
        self.assertTrue(future._event.is_set())
        self.assertTrue(future._result is not None)
        self.assertFalse(future._exception)
        self.assertTrue(dispatcher.remove_listener.called)
        dispatcher.reset_mock()
        future = Future()
        matching_listener = MatchingListener(dialect, future, matcher, validator)
        validator.match.return_value = False
        matching_listener.on_message(dispatcher, None)
        self.assertTrue(future._event.is_set())
        self.assertTrue(future._result is None)
        self.assertTrue(future._exception)
        self.assertTrue(dispatcher.remove_listener.called)


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.hardware = mock.Mock()
        self.dispatcher = Dispatcher(self.hardware)

    def test_stop_at_first_match(self):
        l1 = mock.Mock()
        l2 = mock.Mock()
        l1.on_message.return_value = True
        l2.on_message.return_value = False
        self.dispatcher.add_listener(l1)
        self.dispatcher.add_listener(l2)
        self.hardware.read.return_value = "TEST"
        self.dispatcher.start()
        self.dispatcher.stop().join()
        l1.on_message.assert_called_with(self.dispatcher, "TEST")
        self.assertFalse(l2.on_message.called)

    def test_add_listeners(self):
        l1 = mock.Mock()
        l2 = mock.Mock()
        l1.on_message.return_value = False
        l2.on_message.return_value = False
        self.dispatcher.add_listener(l1)
        self.dispatcher.add_listener(l2)
        self.hardware.read.return_value = "TEST"
        self.dispatcher.start()
        self.dispatcher.stop().join()
        l1.on_message.assert_called_with(self.dispatcher, "TEST")
        l2.on_message.assert_called_with(self.dispatcher, "TEST")

    def test_remove_listener(self):
        l = mock.Mock()
        self.dispatcher.add_listener(l)
        self.dispatcher.remove_listener(l)
        self.dispatcher.start()
        self.dispatcher.stop().join()
        self.assertFalse(l.on_message.called)


## vim: et ts=4 sts=4
