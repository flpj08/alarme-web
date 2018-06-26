from flask import Flask, render_template, jsonify
import datetime
import time
from threading import Thread
import RPi.GPIO as gpio
import pickle

gpio.setwarnings(False)

gpio.setmode(gpio.BOARD)

gpio.setup(19, gpio.IN)
gpio.setup(21, gpio.IN)
gpio.setup(22, gpio.IN)
gpio.setup(23, gpio.IN)

gpio.setup(24, gpio.OUT)
gpio.setup(26, gpio.OUT)

app = Flask(__name__)

status_sistema = False
zona1 = 0
zona2 = 0
zona3 = 0
close = False


@app.route("/")
def main():
	return render_template('main.html')

@app.route("/mudaStatus")
def muda_status():
	global status_sistema
	if (status_sistema):
		status_sistema = False
	else:
		status_sistema = True
	atualiza_led_status()
	return ""

@app.route("/validaStatus")
def valida_status():
	if (status_sistema):
		return "on"
	else:
		return "off"

@app.route("/validaSensores")
def valida_sensores():
	return jsonify({"status" : [zona1, zona2, zona3]})

@app.route("/ultimosalarmes")
def ultimos_alarmes():

	return jsonify({"status" : [zona1, zona2, zona3]})
	
def save_to_file(file, dict):
	with open('obj/' + file, 'wb') as f:
		pickle.dump(dict, f, pickle.HIGHEST_PROTOCOL)

def load_from_file(file):
	with open('obj/' + file, 'wb') as f:
		return pickle.load(f)

def ativa_sirene():
	gpio.output(26,gpio.LOW)
	while (zona1 or zona2 or zona3) and status_sistema:
		gpio.output(26,gpio.HIGH)
		time.sleep(1)
		gpio.output(26,gpio.LOW)
		time.sleep(1)

def le_sensores():
	global zona1
	global zona2
	global zona3

	while not close:
		if status_sistema:
			zona1 = gpio.input(21)
			zona2 = gpio.input(22)
			zona3 = gpio.input(23)
		else:
			zona1 = 0
			zona2 = 0
			zona3 = 0
		time.sleep(0.3)

def atualiza_led_status():
	if (status_sistema):
		gpio.output(26,gpio.LOW)
		gpio.output(24,gpio.HIGH)
	else:
		gpio.output(26,gpio.HIGH)
		gpio.output(24,gpio.LOW)

def le_status():
	global status_sistema
	while not close:
		status = gpio.input(19)
		if (status):
			status_sistema = not status_sistema
			atualiza_led_status()
			time.sleep(0.3)
		

try:
	if __name__ == "__main__":
		t1 = Thread(target=ativa_sirene)
		t2 = Thread(target=le_sensores)
		t3 = Thread(target=le_status)

		t1.daemon = True
		t2.daemon = True
		t3.daemon = True

		t1.start()
		t2.start()
		t3.start()

		app.run(host='0.0.0.0', port=8080, debug=False)

		while True:
			time.sleep(1)

except KeyboardInterrupt:
	print("Fechando")
	close = True