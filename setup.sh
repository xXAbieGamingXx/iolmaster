#!bin/bash
sudo apt -y install python3 python3-venv python3-pip neovim chromium-browser chromium-driver
sudo mv iol.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iol.service
sudo raspi-config nonint do_serial_hw 0 # 0 is on 1 is off
sudo raspi-config nonint do_serial_cons 1
sudo raspi-config nonint do_autologin 0
sudo raspi-config nonint do_vnc 0
python -m venv venv
source venv/bin/activate
pip install selenium pillow mss pyserial
echo "dtoverlay=disable-bt" | sudo tee -a /boot/firmware/config.txt

sudo reboot
