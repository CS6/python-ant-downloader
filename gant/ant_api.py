# Copyright (c) 2012, Braiden Kindt.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS ''AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import logging

import gant.ant_command as command
import gant.ant_core as core
import gant.ant_workflow as workflow

_log = logging.getLogger("ant.ant_api");


class Device(object):
    """
    Provides access to Channel and Network's of ANT radio.
    """

    channels = []
    networks = []

    def __init__(self, dispatcher):
        """
        Create a new ANT device. The given dispatcher is delagated
        to for all now level operations. Typically you should
        use one fo the pre-configured device defined in this package.
        e.g. GarminAntDevice() to get an instance of Device.
        """
        self.dispatcher = dispatcher
        self.reset_system()

    def reset_system(self):
        """
        Reset the ANT radio to default configuration and 
        initialize this instance network and channel properties.
        """
        result = workflow.execute(self.dispatcher,
                workflow.chain(
                        command.ResetSystem(),
                        command.GetDeviceCapabilities()))
        _log.debug("Device Capabilities: max_channels=%d, max_networks=%d, std_opts=0x%x, adv_opts=0x%x%x"
                % (result.max_channels, result.max_networks, result.standard_options, 
                   result.advanced_options_1, result.advanced_options_2))
        self.channels = [Channel(n, self.dispatcher) for n in range(0, result.max_channels)]
        self.networks = [Network(n) for n in range(0, result.max_networks)]

    def close(self):
        workflow.execute(self._dispatcher, command.ResetSystem())
        self.dispatcher.close()


class Channel(object):
    """
    An ANT communications channel.
    Provides methods for configuration and openning
    a channel, to send / recieve data you should 
    register a ChannelListener before openning.
    """

    network = None
    channel_type = 0
    device_number = 0
    device_type = 0
    trans_type = 0
    period = 0x2000
    search_timeout = 0xFF 
    rf_freq = 66
    search_waveform = None
    open_scan_mode = False

    def __init__(self, channel_id, dispatcher):
        self.channel_id = channel_id
        self.dispatcher = dispatcher

    def execute(self, state):
        """
        Exceute the given state (or workflow.
        Channel will automatically be configured
        based on properites of channel an network.
        """
        if not self.network:
            raise AntError("Network must be defined before openning channel", AntError.ERR_API_USAGE)
        if self.open_scan_mode and self.channel_id != 0:
            raise AntError("Open RX scan can only be enabled on channel 0.", AntError.ERR_API_USAGE)
        states = [
                command.SetNetworkKey(self.network.network_id, self.network.network_key),
                command.AssignChannel(self.channel_id, self.channel_type, self.network.network_id),
                command.SetChannelId(self.channel_id, self.device_number, self.device_type, self.trans_type),
                command.SetChannelPeriod(self.channel_id, self.period),
                command.SetChannelSearchTimeout(self.channel_id, self.search_timeout),
                command.SetChannelRfFreq(self.channel_id, self.rf_freq),
        ]
        if self.search_waveform is not None:
            states.append(command.SetChannelSearchWaveform(self.channel_id, self.search_waveform))
        if self.open_scan_mode:
            states.append(command.OpenRxScanMode())
        else:
            states.append(command.OpenChannel(self.channel_id))
        states.append(state)
        states.append(command.CloseChannel(self.channel_id))
        workflow.execute(self.dispatcher, workflow.chain(*states))


class Network(object):

    network_key = "\x00" * 8

    def __init__(self, network_id):
        self.network_id = network_id


class AntError(BaseException):

    ERR_TIMEOUT = 1
    ERR_MSG_FAILED = 2
    ERR_API_USAGE = 3
    ERR_UNSUPPORTED_MESSAGE = 4

    def __init__(self, error_str, error_type):
        super(AntError, self).__init__(error_str, error_type)


# vim: et ts=4 sts=4
