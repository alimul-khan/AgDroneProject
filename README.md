# Raspberry Pi Setup and Autostart Configuration

## 1. Flash OS with Preconfiguration

Use Raspberry Pi Imager:
- Set hostname (e.g., `aircam`)
- Enable SSH
- Configure username and password
- Set Wi-Fi SSID, password, and country
- Save and flash to microSD card

---

## 2. Update & Upgrade System

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y
sudo apt clean
```

---

## 3. Install Git and Store Credentials

```bash
sudo apt install git -y

git config --global user.name "Alimul Khan"
git config --global user.email "alimul.khan@usask.com"
git config --global credential.helper store

git config --list
```

---

## 4. Clone the GitHub Repository

```bash
git clone https://github.com/alimul-khan/AgDroneProject.git
cd AgDroneProject
```

---

## 5. Install Required Python Libraries

```bash
sudo apt install -y python3-flask
sudo apt install -y python3-picamera2
sudo apt install -y python3-opencv
sudo apt install -y python3-imageio
```

---

## 6. Test the Application

```bash
python3 AgCamApp.py
```

---

## 7. Set Up Autostart with systemd

```bash
chmod +x /home/alim/AgDroneProject/AgCamApp.py
sudo nano /etc/systemd/system/AgCamApp.service
```

Paste the following:

```
[Unit]
Description=Real Time Image Processing
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/alim/AgDroneProject/AgCamApp.py
Restart=always
User=alim

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable AgCamApp.service
sudo systemctl start AgCamApp.service
sudo systemctl status AgCamApp.service   # To check status
sudo systemctl stop AgCamApp.service     # To stop manually
```

---

## ✅ All Done

The script will now automatically run at boot.
