import datetime
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request

import serial

# --- Config ---------------------------------------------------------------
REPO = "xXAbieGamingXx/iolmaster"
BRANCH = "master"
COMMIT_API = "https://api.github.com/repos/{}/commits/{}".format(REPO, BRANCH)
RAW_BASE = "https://raw.githubusercontent.com/{}/{}".format(REPO, BRANCH)
UPDATE_FILES = ["main.py", "startup.py"]

SERIAL_PORT = "/dev/serial0"
BAUDRATE = 115200

HERE = os.path.dirname(os.path.abspath(__file__))
HASH_FILE = os.path.join(HERE, ".commit_hash")
REBOOT_DELAY = 5  # seconds after main.py finishes

# RP2350 (e.g. Pico 2 in BOOTSEL mode) mounts as a USB mass-storage volume.
RP_DRIVE_LABEL = "RP2350"
UF2_FILE = "update.uf2"
RP_MOUNT_TIMEOUT = 120  # seconds to wait for the drive to appear
RP_POLL_INTERVAL = 1  # seconds between mount checks


def get_remote_hash():
	"""Return the latest commit SHA on the remote branch, or None on failure."""
	req = urllib.request.Request(
		COMMIT_API, headers={"User-Agent": "iolmaster-updater"}
	)
	with urllib.request.urlopen(req, timeout=15) as resp:
		data = json.load(resp)
	return data["sha"]


def get_local_hash():
	"""Return the last-seen commit SHA, or None if we have never recorded one."""
	if os.path.exists(HASH_FILE):
		with open(HASH_FILE, "r") as f:
			return f.read().strip() or None
	return None


def save_local_hash(sha):
	with open(HASH_FILE, "w") as f:
		f.write(sha)


def download_file(name):
	"""Download a single file from the raw repo into the script directory."""
	url = "{}/{}".format(RAW_BASE, name)
	req = urllib.request.Request(url, headers={"User-Agent": "iolmaster-updater"})
	with urllib.request.urlopen(req, timeout=30) as resp:
		content = resp.read()
	# Write to a temp file first, then atomically replace.
	dest = os.path.join(HERE, name)
	tmp = dest + ".new"
	with open(tmp, "wb") as f:
		f.write(content)
	os.replace(tmp, dest)


def send_serial(message):
	"""Send a message over the UART. Failures are non-fatal."""
	try:
		ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
		try:
			ser.write(message.encode("utf-8"))
			ser.flush()
		finally:
			ser.close()
	except Exception as exc:
		print("serial send failed: {}".format(exc))


def find_drive_mountpoint(label):
	"""Return the mountpoint of a mounted volume with the given label, or None."""
	try:
		out = subprocess.run(
			["lsblk", "-o", "LABEL,MOUNTPOINT", "-nr"],
			capture_output=True,
			text=True,
		).stdout
	except Exception as exc:
		print("lsblk failed: {}".format(exc))
		return None
	for line in out.splitlines():
		parts = line.split(None, 1)
		if len(parts) == 2 and parts[0] == label and parts[1]:
			return parts[1]
	return None


def wait_for_drive_and_copy_uf2():
	"""Wait for the RP2350 drive to mount, then move the UF2 file onto it."""
	print("waiting for {} drive to mount...".format(RP_DRIVE_LABEL))
	deadline = time.time() + RP_MOUNT_TIMEOUT
	mountpoint = None
	while time.time() < deadline:
		mountpoint = find_drive_mountpoint(RP_DRIVE_LABEL)
		if mountpoint:
			break
		time.sleep(RP_POLL_INTERVAL)

	if not mountpoint:
		print("{} drive did not mount within {}s".format(RP_DRIVE_LABEL, RP_MOUNT_TIMEOUT))
		return

	src = os.path.join(HERE, UF2_FILE)
	if not os.path.exists(src):
		print("{} not found, nothing to flash".format(src))
		return

	dest = os.path.join(mountpoint, UF2_FILE)
	try:
		shutil.move(src, dest)
		print("moved {} to {}".format(UF2_FILE, mountpoint))
	except Exception as exc:
		print("failed to move {}: {}".format(UF2_FILE, exc))


def check_and_update():
	"""Compare remote vs local commit hash; update files if they differ."""
	try:
		remote = get_remote_hash()
	except Exception as exc:
		print("could not fetch remote commit hash: {}".format(exc))
		return

	local = get_local_hash()

	# First run: record the current hash without forcing an update.
	if local is None:
		print("no local hash recorded; saving {}".format(remote))
		save_local_hash(remote)
		return

	if remote == local:
		print("already up to date ({})".format(remote))
		return

	print("update available: {} -> {}".format(local, remote))
	try:
		for name in UPDATE_FILES:
			download_file(name)
			print("updated {}".format(name))
	except Exception as exc:
		print("update download failed, keeping existing files: {}".format(exc))
		return

	save_local_hash(remote)
	send_serial("UPDATE")
	wait_for_drive_and_copy_uf2()
	print("update complete")


def run_main():
	"""Run main.py with the same interpreter and wait for it to finish."""
	main_path = os.path.join(HERE, "main.py")
	try:
<<<<<<< HEAD
		result = subprocess.run([sys.executable, main_path], capture_output=True, text=True)
        print(result.stdout)
=======
		result = subprocess.run([sys.executable, main_path], capture_output = True, text = True)
		print(result.stdout)
>>>>>>> de966abb887f68673100b770febd6bf538d153d3
	except Exception as exc:
		print("running main.py failed: {}".format(exc))

def reboot():
	time.sleep(REBOOT_DELAY)
	subprocess.run(["sudo", "reboot"])


def seconds_until_midnight():
	"""Seconds from now until the next local midnight."""
	now = datetime.datetime.now()
	next_midnight = datetime.datetime.combine(
		now.date() + datetime.timedelta(days=1), datetime.time.min
	)
	return (next_midnight - now).total_seconds()


def schedule_midnight_reboot():
	"""Reboot at every local midnight, from a background daemon thread."""

	def _wait_and_reboot():
		while True:
			time.sleep(seconds_until_midnight())
			print("midnight reached, rebooting")
			subprocess.run(["sudo", "reboot"])

	threading.Thread(target=_wait_and_reboot, daemon=True).start()


if __name__ == "__main__":
<<<<<<< HEAD
    check_and_update()
    schedule_midnight_reboot()
    run_main()
    reboot()
=======
	check_and_update()
	run_main()
	# reboot()
>>>>>>> de966abb887f68673100b770febd6bf538d153d3
