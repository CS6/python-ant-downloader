from gant.ant_api import Channel, Network, Device

__all__ = [ "GarminUsbAntDevice", "Device", "Channel", "Network" ]

def GarminUsbAntDevice():
    """
    Create a new ANT Device configured for
    use with a Garmin USB ANT Stick (nRF24AP2-USB).
    http://search.digikey.com/us/en/products/ANTUSB2-ANT/1094-1002-ND/2748492
    """
    import atexit
    from gant.ant_usb_hardware import UsbHardware
    from gant.ant_serial_dialect import SerialDialect, Dispatcher
    hardware = UsbHardware(idVendor=0x0fcf, idProduct=0x1008)
    dispatcher = Dispatcher(hardware)
    dialect = SerialDialect(hardware, dispatcher)
    dispatcher.start()
    class GarminUSbAntDevice(Device):
        def __init__(self):
            super(GarminUSbAntDevice, self).__init__(dialect)
        def close(self):
            hardware.close()
            dispatcher.stop()
    dev = GarminUsbAntDevice()
    atexit.register(lambda : dev.close)


# vim: et ts=4 sts=4
