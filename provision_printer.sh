#!/bin/bash
# Install CUPS + drivers, discover the printer by name, add it as the default
# queue, and record the queue name in printer.conf next to this script.
#
# Safe to re-run: it only writes printer.conf on success, so a failed run (e.g.
# printer off/unreachable) leaves no config and gets retried on the next boot.
# Called by setup.sh once, and by startup.py on boot whenever printer.conf is
# missing.
#
# Usage: provision_printer.sh [QUEUE_NAME] [DISCOVERY_PATTERN]
set -u

# The ONLY thing you normally need to change is this queue name.
PRINTER_NAME="${1:-Brother_HL-L2350DW_series_Printer}"
# Discovery pattern derived from the name (treat _ as a wildcard, drop the
# trailing queue-name suffix). Pass a 2nd arg to override if auto-detect misses.
PRINTER_MATCH="${2:-$(echo "$PRINTER_NAME" | sed -E 's/_(series_)?[Pp]rinter$//; s/_/.*/g')}"
HERE="$(cd "$(dirname "$0")" && pwd)"

sudo apt -y install cups printer-driver-brlaser avahi-daemon avahi-utils
sudo usermod -aG lpadmin "$USER"
sudo systemctl enable --now avahi-daemon cups

echo "discovering printer matching '$PRINTER_MATCH'..."
URI=""
for _ in $(seq 1 30); do
	URI=$(lpinfo -v 2>/dev/null | awk '$1=="network"||$1=="direct"||$1=="usb"{print $2}' | grep -i -m1 "$PRINTER_MATCH" || true)
	[ -n "$URI" ] && break
	sleep 2
done

if [ -z "$URI" ]; then
	echo "WARNING: no printer matching '$PRINTER_MATCH' found" >&2
	exit 1
fi

echo "found printer at $URI"
if echo "$URI" | grep -qi '^usb:'; then
	# USB: needs a real driver PPD (brlaser supports the HL-L2350DW)
	PPD=$(lpinfo -m | grep -i brlaser | grep -i 'l2350' | head -n1 | awk '{print $1}')
	[ -z "$PPD" ] && PPD=$(lpinfo -m | grep -i brlaser | head -n1 | awk '{print $1}')
	sudo lpadmin -p "$PRINTER_NAME" -E -v "$URI" -m "$PPD"
else
	# Network: driverless IPP Everywhere, no vendor driver needed
	sudo lpadmin -p "$PRINTER_NAME" -E -v "$URI" -m everywhere
fi
sudo lpadmin -d "$PRINTER_NAME"        # make it the default queue
sudo cupsaccept "$PRINTER_NAME"
sudo cupsenable "$PRINTER_NAME"
echo "$PRINTER_NAME" > "$HERE/printer.conf"
echo "printer '$PRINTER_NAME' configured and set as default"
