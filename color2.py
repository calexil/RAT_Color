import usb.core
import usb.util
import time

VID = 0x12cf
PID = 0x0c05

dev = usb.core.find(idVendor=VID, idProduct=PID)
if dev is None:
    raise ValueError("Mad Catz R.A.T. 8+ not found! Double-check lsusb and connection.")

print("Device found:", dev.manufacturer, dev.product)

if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

usb.util.claim_interface(dev, 0)

def send_command(report_id, data):
    try:
        # SET_REPORT (class-specific, OUT)
        bytes_written = dev.ctrl_transfer(0x21, 0x09, report_id << 8 | 0x02, 0, data)  # wValue often report_id << 8 + report_type (02=output)
        print(f"Sent {bytes_written} bytes to report {hex(report_id)}: {[hex(b) for b in data]}")
        time.sleep(0.2)  # Let the mouse process it

        # Optional GET_REPORT to see if it responds
        try:
            response = dev.ctrl_transfer(0xa1, 0x01, report_id << 8 | 0x02, 0, 64)
            print(f"Read back from report {hex(report_id)}: {[hex(b) for b in response]}")
        except:
            print("No read response (common if not supported)")
    except usb.core.USBError as e:
        print(f"USB error on report {hex(report_id)}: {e}")

# Some new experiments based on common HID RGB patterns for OEM gaming mice (DEXIN/Saitek lineage)
# Many use report IDs 0x07-0x0b for LEDs, prefixes like 0x07/0x0a, zones 0x00-0x02

# Try report 0x07, possible LED command prefix
send_command(0x07, [0x07, 0x01, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00])  # Zone? Red attempt

# Report 0x08, another common one
send_command(0x08, [0x07, 0x00, 0x00, 0xff, 0x00, 0x00])  # Green?

# Report 0x0b (seen in some DEXIN mice)
send_command(0x0b, [0x0b, 0x01, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00])  # Blue attempt

# Longer buffer example (pad to 32/64 bytes if needed; some mice require full packets)
long_data = [0x07, 0x0a, 0x00] + [0xff, 0x00, 0x00] + [0x00]*25  # Pad
send_command(0x03, long_data[:32])  # Try shorter first

# Possible "commit/save" or init sequence (try after color sets)
send_command(0x09, [0x09, 0x01, 0x00, 0x00, 0x00, 0x00])  # Commit attempt?

# Cleanup
usb.util.release_interface(dev, 0)
if not dev.is_kernel_driver_active(0):
    dev.attach_kernel_driver(0)
