import threading
import logging

_log = logging.getLogger("ant.ant_api");

class Device(object):
    """
    Provides access to Channel and Network's of ANT radio.
    """

    channels = []
    networks = []

    def __init__(self, dialect):
        """
        Create a new ANT device. The given dialect is delagated
        to for all now level operations. Typically you should
        use one fo the pre-configured device defined in this package.
        e.g. GarminAntDevice() to get an instance of Device.
        """
        self._dialect = dialect 
        self.reset_system()

    def close(self):
        """
        Close this device, releasign and resouce it may have
        allocated and reseting the state of ANT radio to device.
        """
        self._dialect.close()

    def reset_system(self):
        """
        Reset the ANT radio to default configuration and 
        initialize this instance network and channel properties.
        """
        self._dialect.reset_system().wait()
        capabilities = self._dialect.get_capabilities().result
        self.channels = [Channel(n, self._dialect) for n in range(0, capabilities.max_channels)]
        self.networks = [Network(n, self._dialect) for n in range(0, capabilities.max_networks)]

    def __del__(self):
        """
        Make sure the device is closed (reset) on deletion.
        """
        self.close();


class Channel(object):
    """
    An ANT communications channel.
    """

    network = None
    channel_type = 0
    device_number = 0
    device_type = 0
    trans_type = 0
    period = 0x2000
    search_timeout = 0xFF 
    rf_freq = 66

    def __init__(self, channel_id, dialect):
        self.channel_id = channel_id
        self._dialect = dialect

    def apply_settings(self):
        """
        For those property that can changed on an already
        open channel, calling this method will apply changes.
        network, device#, device_type, trans_type, and open_rf_scan
        cannot be changed on an open channel. To apply changes to
        those values, close() and open().
        """
        self._dialect.set_channel_period(self.channel_id, self.period).wait()
        self._dialect.set_channel_search_timeout(self.channel_id, self.search_timeout).wait()
        self._dialect.set_channel_rf_freq(self.channel_id, self.rf_freq).wait()

    def open(self):
        """
        Apply all setting to this channel and open.
        Attempts to open an already open channel will fail
        (depending on reply from hardware)
        """
        assert self.network
        self._dialect.assign_channel(self.channel_id, self.channel_type, self.network.network_id).wait()
        self._dialect.set_channel_id(self.channel_id, self.device_number, self.device_type, self.trans_type).wait()
        self.apply_settings()
        self._dialect.open_channel(self.channel_id).wait()

    def close(self):
        """
        close the channel and unassign the change.
        Attempting to close already closed channel may fail,
        depending on hardware.
        """
        self._dialect.close_channel(self.channel_id).wait()
        self._dialect.unassign_channel(self.channel_id).wait()

    def get_channel_id(self):
        """
        Get a tuple representing the id of this channel.
        """
        return self._dialect.get_channel_id(self.channel_id).result

    def get_channel_status(self):
        """
        Get a tuple representing the state of this channel.
        """
        return self._dialect.get_channel_status(self.channel_id).result
            

class Network(object):

    _network_key = "\x00" * 8

    def __init__(self, network_id, dialect):
        self.network_id = network_id
        self._dialect = dialect

    @property
    def network_key(self):
        return self._network_key

    @network_key.setter
    def network_key(self, network_key):
        self._network_key = network_key
        self._dialect.set_network_key(self.network_id, self._network_key).wait()


class Future(object):
    """
    Returned by async API calls to an ANT device. e.g. send_broadcast.
    result will block until the operation completes, and return the
    message recived by device. result may also raise an exception if
    the message returned from device is a failure. A timeout, provided
    you waited at least message_period time, is unrecoverable, and
    an error will be raised.
    """
    
    timeout = 2

    def __init__(self):
        self._event = threading.Event()
        self._result = None
        self._exception = None

    @property
    def result(self):
        """
        Get the result of the asynchronous operation.
        Block until the result completes or timesout.
        """
        self.wait()
        return self._result
        
    @result.setter
    def result(self, result):
        """
        Set the result of the async transaction.
        """
        self._result = result
        self._event.set()

    def set_exception(self, e):
        """
        Set an exception, if set exception will be raised
        on access of result property.
        """
        self._exception = e
        self._event.set()

    def wait(self):
        """
        Wait for device to acknowledge command,
        discard result, expcetion can still be raised.
        """
        self._event.wait(self.timeout)
        assert self._event.is_set()
        if self._exception: raise self._exception

    def retry():
        """
        Invoke the original action that created this
        "Future" and return a new one.
        """
        pass


# vim: et ts=4 sts=4
