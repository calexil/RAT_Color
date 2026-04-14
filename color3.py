import usb.core
import usb.util
import time

VID = 0x12cf
PID = 0x0c05

dev = usb.core.find(idVendor=VID, idProduct=PID)
if dev is None:
    raise ValueError("Mad Catz R.A.T. 8+ not found!")

print("Device found:", dev.manufacturer, dev.product)

if dev.is_kernel_driver_active(0):
    try:
        dev.detach_kernel_driver(0)
    except usb.core.USBError as e:
        print("Detach failed (maybe already detached?):", e)

usb.util.claim_interface(dev, 0)

def send_command(report_id, data, request_type=0x21, request=0x09, value_suffix=0x02):
    try:
        w_value = (report_id << 8) | value_suffix
        bytes_written = dev.ctrl_transfer(request_type, request, w_value, 0, data, timeout=5000)  # 5s timeout
        print(f"Sent {bytes_written} bytes to report {hex(report_id)} (wValue={hex(w_value)}): {[hex(b) for b in data]}")
        time.sleep(0.3)
        
        # Try read (feature report get)
        try:
            response = dev.ctrl_transfer(0xa1, 0x01, w_value, 0, 64, timeout=2000)
            print(f"Read back: {[hex(b) for b in response]}")
        except usb.core.USBError as re:
            print(f"Read timed out/failed (often normal): {re}")
    except usb.core.USBError as e:
        print(f"Send error on report {hex(report_id)}: {e}")

# Experiments with variations (common for vendor HID RGB)
# Try feature report suffix (0x03) instead of output (0x02)
send_command(0x07, [0x07, 0x01, 0xff, 0x00, 0x00, 0x00], value_suffix=0x03)  # Red attempt, feature

send_command(0x08, [0x07, 0x00, 0x00, 0xff, 0x00, 0x00], value_suffix=0x03)

send_command(0x0b, [0x0b, 0x01, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00], value_suffix=0x03)

# Classic output try again with longer timeout
send_command(0x03, [0x07, 0x0a, 0x00, 0xff, 0x00, 0x00] + [0x00]*26)

# Possible init or commit
send_command(0x01, [0x01, 0x00, 0x00, 0x00, 0x00], value_suffix=0x03)  # Init-like

# Cleanup with safety
usb.util.release_interface(dev, 0)
try:
    if not dev.is_kernel_driver_active(0):
        dev.attach_kernel_driver(0)
except usb.core.USBError as e:
    print("Re-attach failed (harmless, unplug/replug mouse to fix):", e)        
