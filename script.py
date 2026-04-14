import usb.core
import usb.util

# Replace with your actual VID:PID from lsusb (e.g., VID=0x0738, PID=0x1708)
VID = 0x12cf  # Mad Catz vendor ID
PID = 0x0c05  # Replace with your PID, e.g., 0x1708 for RAT 8 variants

# Find the device
dev = usb.core.find(idVendor=VID, idProduct=PID)

if dev is None:
    raise ValueError("Mouse not found. Check VID:PID or connection.")

# If kernel driver is active, detach it (for HID control)
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

# Claim the interface
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]  # Assuming interface 0
usb.util.claim_interface(dev, intf)

# Example: Send a basic HID control request (this is a placeholder; real RGB commands go here)
# Format: dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data_or_wLength)
# bmRequestType: 0x21 for HID set, 0xa1 for get (class-specific)
# From captures, RGB might be something like: set_report(0x21, 0x09, 0x0200, 0, [r, g, b, effect_byte])
try:
    # Placeholder: Set RGB to red (adjust based on captures)
    rgb_data = [0x07, 0x0a, 0x01, 0x00, 0xff, 0x00, 0x00, 0x00]  # Example from similar mice; test/change
    dev.ctrl_transfer(0x21, 0x09, 0x0200, 0, rgb_data)  # HID set report (report ID 2)
    print("RGB command sent (placeholder for red).")

    # Example read: Get current status (adjust)
    response = dev.ctrl_transfer(0xa1, 0x01, 0x0200, 0, 8)  # HID get report
    print("Response:", response)

except usb.core.USBError as e:
    print("USB error:", e)

# Release the interface and reattach kernel driver
usb.util.release_interface(dev, intf)
dev.attach_kernel_driver(0)
