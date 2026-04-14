import usb.core
import usb.util
import time

VID = 0x12cf
PID = 0x0c05

dev = usb.core.find(idVendor=VID, idProduct=PID)
if dev is None:
    raise ValueError("R.A.T. 8+ not found!")

print("Device:", dev.manufacturer, dev.product)

# Detach kernel driver if active
for cfg in dev:
    for intf in cfg:
        if dev.is_kernel_driver_active(intf.bInterfaceNumber):
            try:
                dev.detach_kernel_driver(intf.bInterfaceNumber)
            except usb.core.USBError as e:
                print(f"Detach failed for intf {intf.bInterfaceNumber}: {e}")

# Claim first HID interface (usually 0)
usb.util.claim_interface(dev, 0)

# Find the OUT endpoint (for writing reports)
endpoint_out = None
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]  # interface 0, altsetting 0
for ep in intf:
    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
        endpoint_out = ep
        break

if endpoint_out is None:
    raise ValueError("No OUT endpoint found!")

print(f"Using OUT endpoint: {hex(endpoint_out.bEndpointAddress)}")

def send_raw(data):
    try:
        bytes_written = dev.write(endpoint_out.bEndpointAddress, data, timeout=5000)
        print(f"Raw write success: {bytes_written} bytes sent -> { [hex(b) for b in data[:8]] }...")
        time.sleep(0.5)
    except usb.core.USBError as e:
        print(f"Write error: {e}")

# Test payloads (first byte often report ID or command; pad to typical 64 bytes)
# Red static attempt
send_raw([0x07, 0x00, 0xff, 0x00, 0x00] + [0x00]*59)

# Green breathing attempt
send_raw([0x0a, 0x01, 0x00, 0xff, 0x00, 0x01] + [0x00]*58)

# Another common prefix
send_raw([0x00, 0xff, 0x00, 0x00] + [0x00]*60)  # Off or reset?

# Cleanup
usb.util.release_interface(dev, 0)
for cfg in dev:
    for intf in cfg:
        try:
            dev.attach_kernel_driver(intf.bInterfaceNumber)
        except:
            pass  # Ignore re-attach fails; unplug/replug fixes
