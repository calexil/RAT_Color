import usb.core
import usb.util
import time

VID = 0x12cf  # Mad Catz
PID = 0x0C05  # Example for RAT 8+ variant; CHANGE TO YOURS FROM lsusb!

dev = usb.core.find(idVendor=VID, idProduct=PID)
if dev is None:
    raise ValueError("Mouse not found!")

if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

usb.util.claim_interface(dev, 0)

def send_rgb(report_id, data):
    try:
        dev.ctrl_transfer(0x21, 0x09, report_id << 8, 0, data)
        print(f"Sent to report {hex(report_id)}: {data}")
        time.sleep(0.1)  # Give mouse time to process
        response = dev.ctrl_transfer(0xA1, 0x01, report_id << 8, 0, 64)  # Try larger read
        print("Read back:", list(response))
    except usb.core.USBError as e:
        print("Error:", e)

# Experiment 1: Try common RAT-style LED set (adjust bytes)
send_rgb(0x03, [0x07, 0x0a, 0x01, 0xff, 0x00, 0x00, 0x00, 0x00])  # Red attempt

# Experiment 2: Another variant
send_rgb(0x02, [0x07, 0x04, 0x00, 0x00, 0xff, 0x00, 0x00])  # Green?

# Experiment 3: Longer buffer, possible commit
send_rgb(0x07, [0x07] + [0xff, 0x00, 0x00] * 5 + [0x00] * 20)  # Pad

usb.util.release_interface(dev, 0)
dev.attach_kernel_driver(0)
