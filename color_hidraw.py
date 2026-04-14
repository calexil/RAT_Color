import hid
import time

VID = 0x12cf
PID = 0x0c05
HIDRAW_PATH = b'/dev/hidraw3'

try:
    dev = hid.Device(VID, PID)
    print("Opened via VID/PID:", dev.manufacturer or "Unknown", dev.product or "Unknown")
except Exception as e:
    print("VID/PID open failed:", e)
    print("Falling back to hidraw path...")
    dev = hid.Device(path=HIDRAW_PATH)
    print("Opened via /dev/hidraw3")

# Payloads as lists → convert to bytes before write
payload_lists = [

    # More variations around the working payload 1
    [0x00, 0x07, 0x01, 0x00, 0xff, 0x00] + [0x00] * 58,  # Green attempt, zone 1?
    [0x00, 0x07, 0x02, 0x00, 0x00, 0xff] + [0x00] * 58,  # Blue, zone 2?
    [0x00, 0x0a, 0x00, 0xff, 0x00, 0x00, 0x00] + [0x00] * 57,  # Alt command prefix
    [0x00] * 64,  # All zero (possible off/reset)
    # Red static attempts
    [0x00, 0x07, 0x00, 0xff, 0x00, 0x00] + [0x00] * 58,
    [0x07, 0xff, 0x00, 0x00] + [0x00] * 60,
    [0x07, 0x00, 0xff, 0x00, 0x00] + [0x00] * 59,
    [0x07, 0x01, 0xff, 0x00, 0x00] + [0x00] * 59,
    [0x07, 0x02, 0xff, 0x00, 0x00] + [0x00] * 59,
    # Breathing green
    [0x0a, 0x00, 0x00, 0xff, 0x00, 0x01] + [0x00] * 58,
    # Off/reset
    [0x00] * 64,
]

for idx, payload_list in enumerate(payload_lists):
    data = bytes(payload_list)  # Convert list[int] → bytes
    try:
        written = dev.write(data)
        print(f"Payload {idx+1} sent: {written} bytes | Preview: {[hex(b) for b in payload_list[:10]]}")
        time.sleep(2)
    except Exception as e:
        print(f"Write failed on payload {idx+1}: {e}")

try:
    # Read without timeout_ms (older API often blocks or takes only length)
    resp = dev.read(64)  # Or dev.read(64, 3000) if it accepts timeout as int
    print("Any response:", [hex(b) for b in resp] if resp else "None")
except Exception as e:
    print("Read failed (common):", e)

dev.close()
print("Done. Unplug/replug mouse if needed.")
