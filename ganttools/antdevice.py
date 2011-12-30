import usb

class AntUsbDevice(object):
    
    def __init__(self, idVendor, idProduct, configuration=0, interface=0, altInterface=0, endpointOut=0x01, endpointIn=0x81):
        self.dev = self.find_usb_device(idVendor, idProduct)
        if not self.dev:
            raise IOError("No USB Device could be found with vid=0x%04x pid=0x%04x." % (idVendor, idProduct))
        self.handle = self.dev.open() 
        self.cfg = self.dev.configurations[configuration]
        self.handle.setConfiguration(self.cfg)
        self.interface = self.cfg.interfaces[interface][altInterface]
        self.handle.setAltInterface(self.interface)
        self.handle.claimInterface(self.interface)
        self.end_out = endpointOut 
        self.end_in = endpointIn

    def find_usb_device(self, idVendor, idProduct):
        for bus in usb.busses():
            for dev in bus.devices:
                if dev.idProduct == idProduct and dev.idVendor == idVendor:
                    return dev

    def read(self, n=1, timeout=100):
        return self.handle.bulkRead(self.end_in, n, timeout)

    def write(self, buffer, timeout=100):
        self.handle.bulkWrite(self.end_out, buffer, timeout)


class AntFileDevice(object):

    def __init__(self, dev):
        pass

    def read(self, n=1, timeout=100):
        return []

    def write(self, buffer, timeout=100):
        pass


# vim: et ts=4 sts=4 nowrap
