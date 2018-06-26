from flask import Flask, render_template, jsonify, send_from_directory
import datetime
import time
from threading import Thread
import RPi.GPIO as gpio
import pickle
import os

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
monitora_zona1 = True
monitora_zona2 = True
monitora_zona3 = True
close = False

alarmes = []


@app.route("/")
def main():
	return render_template('main.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

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

@app.route("/atualizaAlarmes")
def atualiza_alarmes():
	return jsonify(alarmes)

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
	if (os.path.isfile('obj/' + file)):
		with open('obj/' + file, 'rb') as f:
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
	global alarmes

	while not close:
		if status_sistema:
			zona1 = monitora_zona1 and gpio.input(21)
			zona2 = monitora_zona2 and gpio.input(22)
			zona3 = monitora_zona3 and gpio.input(23)

			if zona1 == 1 and monitora_zona1:
				alarmes.append({'zona': 'zona1', 'hora': datetime.datetime.now()})
			if zona2 == 1 and monitora_zona2:
				alarmes.append({'zona': 'zona2', 'hora': datetime.datetime.now()})
			if zona3 == 1 and monitora_zona3:
				alarmes.append({'zona': 'zona3', 'hora': datetime.datetime.now()})
			
			save_to_file('alarmes', alarmes)
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

		alarmes = load_from_file('alarmes') or []

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