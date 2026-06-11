from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from itertools import chain
from PIL import Image
import io
import time
import serial
import subprocess
import csv
import os
# test for being equal to the boundries
# KER is corneal radius
# OD = right OS = left
# name, flat k, flat axis, steep k, steep axis, axial length, optical acd, wtw
right_constants = []
left_constants = []
right_incision = [0,180] # sia, location
left_incision = [0,0]
left_refraction = 1
right_refraction = 1
results = "level1 static" 
calculate = "MainContent_Button1"
right_eye = "MainContent_Rad1" 
left_eye = "MainContent_Rad2"
doctor_name = "MainContent_DoctorName"
patient_name = "MainContent_PatientName" 
flat_k = "MainContent_MeasuredK"
flat_axis = "MainContent_MeasuredAxis"
steep_k = "MainContent_MeasuredK0"
steep_axis = "MainContent_MeasuredAxis0"
axial_length = "MainContent_AxLength"
optical_acd = "MainContent_OpticalACD"
wtw = "MainContent_WTW"
refraction = "MainContent_Refraction"
incision_sia = "MainContent_InducedCyl"
incision_location = "MainContent_IncisionAxis"
lens_factor = "MainContent_LensFactor"
a_constant = "MainContent_Aconstant"
iol_constant = 119.1
left_examined = True
right_examined = True
name_of_doctor = "Angela Nahl, MD"
url = "https://calc.apacrs.org/toric_calculator20/Toric%20Calculator.aspx"
screenshot_coords = (215, 265, 1080, 820) # x, y, x, y
UART_PORT = "/dev/ttyAMA0"
BAUDRATE = 115200
sleep_interval = .05
def main(left):
	options = Options()
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	service = Service("/usr/bin/chromedriver")
	driver = webdriver.Chrome(service=service, options=options)
	driver.get(url)
	driver.set_window_size(1300, 1000)
	driver.set_window_position(0,0)
	time.sleep(10)
	paste_data(driver, left)
	time.sleep(3)
	driver.quit()

def paste_data(driver, left):
	constants = []
	if(left):
		left = driver.find_element(By.ID, left_eye)
		left.click()
		refraction_box = driver.find_element(By.ID, refraction)
		refraction_box.send_keys(str(left_refraction))
		sia = driver.find_element(By.ID, incision_sia)
		sia.send_keys(str(left_incision[0]))
		location = driver.find_element(By.ID, incision_location)
		location.send_keys(str(left_incision[1]))
		constants = left_constants
	else:
		right = driver.find_element(By.ID, right_eye)
		right.click()
		refraction_box = driver.find_element(By.ID, refraction)
		refraction_box.send_keys(str(right_refraction))
		sia = driver.find_element(By.ID, incision_sia)
		sia.send_keys(str(right_incision[0]))
		location = driver.find_element(By.ID, incision_location)
		location.send_keys(str(right_incision[1]))
		constants = right_constants
	constant = driver.find_element(By.ID, a_constant)
	constant.send_keys(str(iol_constant))
	doctor = driver.find_element(By.ID, doctor_name)
	doctor.send_keys(name_of_doctor)
	patient = driver.find_element(By.ID, patient_name)
	patient.send_keys(constants[0])
	k1 = driver.find_element(By.ID, flat_k)
	k1.send_keys(str(constants[1]))
	ax1 = driver.find_element(By.ID, flat_axis)
	ax1.send_keys(str(constants[2]))
	k2 = driver.find_element(By.ID, steep_k)
	k2.send_keys(str(constants[3]))
	ax2 = driver.find_element(By.ID, steep_axis)
	ax2.send_keys(str(constants[4]))
	al = driver.find_element(By.ID, axial_length)
	al.send_keys(str(constants[5]))
	acd = driver.find_element(By.ID, optical_acd)
	acd.send_keys(str(constants[6]))
	wtw_box = driver.find_element(By.ID, wtw)
	wtw_box.send_keys(str(constants[7]))
	time.sleep(3)
	calculate_box = driver.find_element(By.ID, calculate)
	calculate_box.click()
	time.sleep(3)
	results_box = driver.find_element(By.XPATH, "(//a[contains(@class, 'level1') and contains(@class, 'static')])[3]")
	results_box.click()
	time.sleep(8)
	if(left):
		output = "left.png"
	else:
		output = "right.png"
	png = driver.get_screenshot_as_png()
	image = Image.open(io.BytesIO(png))
	chrome_top = driver.execute_script("return window.outerHeight - window.innerHeight;")
	dpr = driver.execute_script("return window.devicePixelRatio || 1;")
	x1, y1, x2, y2 = screenshot_coords
	box = tuple(int(v * dpr) for v in (x1, y1 - chrome_top, x2, y2 - chrome_top))
	image.crop(box).save(output)

def get_data():
	with open("export.csv", "r") as file:
		reader = csv.reader(file, delimiter=";")
		first_row = True
		for row in reader:
			print(row)
			if first_row:
				first_row = False
			else:
				if(row[30] == ""):
					global left_examined
					left_examined = False
				if(row[27] == ""):
					global right_examined
					right_examined = False
				left_constants.append(row[1] + " " + row[0])
				right_constants.append(row[1] + " " + row[0])
				for i in range(2):
					if(i == 0 and left_examined or i == 1 and right_examined):
						k1 = []
						k1.append(row[16-i*9])
						k1.append(row[19-i*9])
						k1.append(row[22-i*9])
						make_floats(k1)
						axis = []
						axis.append(row[18-1*9])
						axis.append(row[21-1*9])
						axis.append(row[24-1*9])
						make_floats(axis)
						if(i == 0):
							left_constants.append(sum(k1)/len(k1))
							left_constants.append(sum(axis)/len(axis))
						else:
							right_constants.append(sum(k1)/len(k1))
							right_constants.append(sum(axis)/len(axis))
				for i in range(2):
					if(i == 0 and left_examined or i == 1 and right_examined):
						k2 = []
						k2.append(row[17-i*9])
						k2.append(row[20-i*9])
						k2.append(row[23-i*9])
						make_floats(k2)
						if(i == 0):
							left_constants.append(sum(k2)/len(k2))
							if(left_constants[2] <= 90):
								left_constants.append(left_constants[2]+90)
							else:
								left_constants.append(left_constants[2]-90)
						else:
							right_constants.append(sum(k2)/len(k2))
							if(left_constants[2] <= 90):
								right_constants.append(right_constants[2]+90)
							else:
								right_constants.append(right_constants[2]-90)
				if(left_examined):
					left_constants.append(float(row[6]))
					left_constants.append(float(row[26]))
					wtw = []
					wtw.append(row[30])
					wtw.append(row[31])
					wtw.append(row[32])
					make_floats(wtw)
					left_constants.append(sum(wtw)/len(wtw))							
					
				if(right_examined):
					right_constants.append(float(row[5]))
					right_constants.append(float(row[25]))
					wtw = []
					wtw.append(row[27])
					wtw.append(row[28])
					wtw.append(row[29])
					make_floats(wtw)
					right_constants.append(sum(wtw)/len(wtw))							

def get_printer_name():
	"""Return the queue name written by setup.sh, or None to use the CUPS default."""
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "printer.conf")
	try:
		with open(path) as f:
			return f.read().strip() or None
	except OSError:
		return None

def print_data():
	printer = get_printer_name()
	for examined, file_name in ((left_examined, "left.png"), (right_examined, "right.png")):
		if(not examined):
			continue
		cmd = ["lp"]
		if(printer):
			cmd += ["-d", printer]
		cmd.append(file_name)
		subprocess.run(cmd)

def read_csv():
	ser = serial.Serial(UART_PORT, BAUDRATE, timeout=1, exclusive=True)
	ser.reset_input_buffer()
	print("opened serial port")
	buffer = bytearray()
	last_char_time = None
	try:
		while True:
			if(last_char_time is not None and time.time() - last_char_time > 5):
				break
			chunk = ser.read(256)
			if(chunk):
				buffer += chunk
				last_char_time = time.time()
	finally:
		ser.close()
		print("closed serial port")
	text = buffer.decode("utf-8", errors="ignore")
	with open("export.csv", "w") as file:
		file.write(text)

def reset_data():
	global left_constants
	global right_constants
	global left_examined
	global right_examined
	left_constants = []
	right_constants = []
	left_examined = False
	right_examined = False

def make_floats(strings):
	for i in range(len(strings)):
		strings[i] = float(strings[i])

if(__name__ == "__main__"):
	# while True:
	read_csv()
	get_data()
	if(left_examined):
		main(True)
	if(right_examined):
		main(False)
	# print_data()
	# subprocess.run(["rm", "-f", "left.png", "right.png"])
	time.sleep(5) # let the prints finish
