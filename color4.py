import hid
import time

VID = 0x12cf
PID = 0x0c05

try:
    # Open by VID/PID (preferred)
    dev = hid.device()
    dev.open(VID, PID)
    print("Opened HID device:", dev.manufacturer_string, dev.product_string)
except Exception:
    print("VID/PID open failed; trying hidraw path...")
    # Fallback: open raw path (e.g. '/dev/hidraw0')
    dev = hid.device()
    dev.open_path(b'/dev/hidraw0')  # CHANGE TO YOUR hidrawX
    print("Opened via hidraw")

# Raw write: first byte often = report ID (try 0x00 for default/output)
# Common pattern: report_id + command + zone + r g b + effect + padding
data_red_static = [0x00, 0x07, 0x00, 0xff, 0x00, 0x00, 0x00, 0x00] + [0x00] * 56  # Pad to 64
try:
    dev.write(data_red_static)
    print("Sent raw data (red attempt):", [hex(b) for b in data_red_static[:10]])
except Exception as e:
    print("Write error:", e)

time.sleep(1)  # Wait for effect

# Try another: breathing green, different prefix
data_green_breath = [0x00, 0x0a, 0x01, 0x00, 0xff, 0x00, 0x01] + [0x00] * 57
dev.write(data_green_breath)
print("Sent green breath attempt")

dev.close()
