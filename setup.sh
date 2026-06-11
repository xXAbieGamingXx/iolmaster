#!bin/bash
sudo apt -y install python3 python3-venv python3-pip neovim chromium-browser chromium-driver
sudo mv iol.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iol.service
sudo raspi-config nonint do_serial_hw 0 # 0 is on 1 is off
sudo raspi-config nonint do_serial_cons 1
<<<<<<< HEAD
sudo raspi-config nonint do_sudo_pass 1
=======
sudo raspi-config nonint do_autologin 0
>>>>>>> de966abb887f68673100b770febd6bf538d153d3
sudo raspi-config nonint do_vnc 0
python -m venv venv
source venv/bin/activate
pip install selenium pyserial pyscreenshot
echo "dtoverlay=disable-bt" | sudo tee -a /boot/firmware/config.txt

sudo reboot
