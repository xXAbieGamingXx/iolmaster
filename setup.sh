#!bin/bash
sudo apt -y install python3 python3-venv python3-pip neovim
sudo mv iol.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable iol.service
python -m venv venv
source venv/bin/activate
pip install selenium pillow mss pyserial

sudo reboot
