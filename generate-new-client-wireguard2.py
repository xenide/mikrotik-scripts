import routeros_api
import ipaddress
import re
from dotenv import load_dotenv
import os
import pyperclip
import qrcode
from PIL import Image
import io

# Load environment variables
load_dotenv()

# --- CONFIGURATION --- #
ROUTER_IP = "10.0.0.254"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
PORT = 8728  # default API port
INTERFACE = "wireguard2"
ALLOWED_MASK = "/32"  # adjust mask if needed

# --- CONNECT TO ROUTER --- #
connection = routeros_api.RouterOsApiPool(
    ROUTER_IP, username=USERNAME, password=PASSWORD, port=PORT, plaintext_login=True
)
api = connection.get_api()

# --- READ WIREGUARD PEERS --- #
peers_resource = api.get_resource("/interface/wireguard/peers")
peers = peers_resource.get(interface=INTERFACE)
if not peers:
    print("No peers found on interface " + INTERFACE)
    exit(1)

# --- FIND PEER WITH HIGHEST IP ADDRESS --- #
highest_peer = None
highest_ip = None
for peer in peers:
    addr = peer.get("allowed-address")
    if addr:
        # remove mask if included
        ip_str = addr.split("/")[0]
        curr_ip = ipaddress.ip_address(ip_str)
        if highest_ip is None or curr_ip > highest_ip:
            highest_ip = curr_ip
            highest_peer = peer

if highest_peer is None:
    print("Could not determine a peer with a valid allowed-address.")
    exit(1)

# --- PREPARE NEW PEER PROPERTIES --- #
new_ip = highest_ip + 1
new_addr = f"{new_ip}{ALLOWED_MASK}"

# Copy properties from the highest peer except the internal fields
new_peer_props = {k: v for k, v in highest_peer.items() if not k.startswith(".")}

new_peer_props["allowed-address"] = new_addr
new_peer_props["client-address"] = new_addr

# Increase name (if present). For example, if name is 'Client 1', increment the number.
if "name" in new_peer_props:
    name = new_peer_props["name"]
    match = re.search(r"(\d+)$", name)
    if match:
        new_number = int(match.group(1)) + 1
        new_name = re.sub(r"\d+$", str(new_number), name)
    else:
        new_name = name + " 2"
    new_peer_props["name"] = new_name
else:
    new_peer_props["name"] = "Client 1"

# Drop all things that the router doesn't need
new_peer_props.pop("id", None)
new_peer_props.pop("private-key", None)
new_peer_props.pop("current-endpoint-address", None)
new_peer_props.pop("current-endpoint-port", None)
new_peer_props.pop("tx", None)
new_peer_props.pop("rx", None)
new_peer_props.pop("dynamic", None)

# Instruct the router to generate a new pre-shared key.
# This may involve setting a flag; adjust the parameter key based on your router's configuration.
new_peer_props["preshared-key"] = "auto"
new_peer_props["private-key"] = "auto"

# --- CREATE NEW WIREGUARD PEER --- #
new_peer = peers_resource.add(**new_peer_props)
if new_peer.done:
    print("New peer successfully created!")
else:
    print("Failed to create new peer")
    exit(1)
new_peer_id = new_peer.done_message["ret"]

# --- EXPORT QR CODE --- #
# Call the router's function to export the QR code.
# This command may vary depending on your router firmware. Adjust if necessary.
qr_result = peers_resource.call("show-client-config", {".id": new_peer_id})
data = qr_result[0]["conf"]

# Generate QR code image
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(data)
qr.make(fit=True)
qr_image = qr.make_image(fill_color="black", back_color="white")

# Convert the image to bytes so we can put it on the clipboard
img_byte_arr = io.BytesIO()
qr_image.save(img_byte_arr, format="PNG")
img_byte_arr.seek(0)

# On macOS, we need to use pbcopy to copy the image to clipboard
with open("/tmp/wireguard_qr.png", "wb") as f:
    f.write(img_byte_arr.getvalue())

os.system(
    'osascript -e \'tell application "System Events" to set the clipboard to (read (POSIX file "/tmp/wireguard_qr.png") as TIFF picture)\''
)
os.remove("/tmp/wireguard_qr.png")  # Clean up the temporary file

print("WireGuard QR code has been copied to clipboard as an image!")

connection.disconnect()
