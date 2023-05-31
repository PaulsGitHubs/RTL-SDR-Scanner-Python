import sys
import time
import argparse
import numpy as np
import os
import json
import zmq
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from rtlsdr import RtlSdr
from scipy import signal as sig
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout

#*** THIS IS MORE COMPLICATED THAN IT SOUNDS
#Need to get the harmonics to work to spot frequencies that are interfering it seems like PSD does not do it justice. We need to scan it for: Frequency of wave (to get the harmonics), the strength of the signal, and the band of the signal *** THIS IS MORE COMPLICATED THAN IT SOUNDS

# Guidelines for choosing the number of samples to read from the RTL-SDR device

# 1. Choose a power of 2:
# This is important for efficient processing, especially when using Fast Fourier Transform (FFT) algorithms.
# Common choices include 131072 (2^17), 262144 (2^18), 524288 (2^19), and 1048576 (2^20).
#
# Example:
# num_samples = 131072

# 2. Consider the time resolution:
# The time duration of the captured signal is determined by the number of samples and the sample rate.
# For example, if you choose 131072 samples and have a sample rate of 2.4 MS/s (2,400,000 samples per second),
# the time duration of the captured data would be 131072 / 2,400,000 = 0.0547 seconds.
# This means that the data you're processing represents a signal captured over 54.7 milliseconds.
#
# Equation:
# time_duration = num_samples / sample_rate

# Example:
num_samples = 131072
sample_rate = 2.4e6  # 2.4 MS/s
time_duration = num_samples / sample_rate  # 0.0547 seconds, or 54.7 milliseconds


#this is good at finding FM radio stations... but AM radio stations are going to be a challange because bad antenna... but in theory if connection is good and no interference
#it should work well for AM signals... I wonder if I can create an app that will be able to tell what devices are interfering based on the frequency of the signal

def detect_harmonics(radio_stations, harmonic_threshold=3, max_harmonic=10, shape_margin=1e3, bin_width=1e3):
    harmonic_candidates = []
    for station in radio_stations:
        freq = station['freq']
        psd = station['psd']
        harmonics = [freq * (i + 1) for i in range(1, max_harmonic + 1)]
        strong_harmonics = 0
        for harmonic in harmonics:
            for candidate in radio_stations:
                if abs(candidate['freq'] - harmonic) < shape_margin:
                    if check_psd_shape(candidate, radio_stations, bin_width):
                        strong_harmonics += 1
                    break
        if strong_harmonics >= harmonic_threshold:
            harmonic_candidates.append({'freq': freq, 'harmonics': strong_harmonics})

    return harmonic_candidates

def tune_to_frequency(radio, true_frequency, lo_frequency):
    shifted_frequency = true_frequency + lo_frequency
    radio.center_freq = shifted_frequency
    print(f"Tuned to {true_frequency / 1e6} MHz (shifted to {shifted_frequency / 1e6} MHz)")


def find_highest_magnitudes(data, num_peaks=5, sample_rate=2.048e6, fft_size=1024):
    if len(data) < num_peaks:
        print("Not enough data points to find the desired number of peaks.")
        return [], []

    peak_indices = np.argpartition(data, -num_peaks)[-num_peaks:]
    peak_indices = peak_indices[np.argsort(-data[peak_indices])]
    bin_width = sample_rate / fft_size
    frequencies = peak_indices * bin_width
    return peak_indices, frequencies

class ScannerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(ScannerApp, self).__init__()

        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('RTL-SDR Scanner')
        self.resize(400, 300)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        grid = QtWidgets.QGridLayout(central_widget)

        labels = ['PPM', 'Gain', 'Threshold', 'LNB LO', 'Start', 'Stop', 'Step']
        self.inputs = {}

        default_values = {'ppm': '0', 'gain': '20', 'threshold': '0.75', 'lnb lo': '-125000000', 'start': '93000000', 'stop': '95500000', 'step': '100000'}

        for i, label_text in enumerate(labels):
            label = QtWidgets.QLabel(label_text)
            input = QtWidgets.QLineEdit()
            input.setText(default_values[label_text.lower()])
            grid.addWidget(label, i, 0)
            grid.addWidget(input, i, 1)

            self.inputs[label_text.lower()] = input

        self.scan_button = QtWidgets.QPushButton('Start Scan')
        self.scan_button.clicked.connect(self.start_scan)
        grid.addWidget(self.scan_button, len(labels), 0, 1, 2)

        self.result_list = QtWidgets.QListWidget()
        grid.addWidget(self.result_list, 0, 2, len(labels), 1)

    @pyqtSlot()
    def start_scan(self):
        args = self.get_args()
        self.scan(args)

    def get_args(self):
        return argparse.Namespace(
            ppm=int(self.inputs['ppm'].text()),
            gain=int(self.inputs['gain'].text()),
            threshold=float(self.inputs['threshold'].text()),
            lo=int(self.inputs['lnb lo'].text()),
            start=int(self.inputs['start'].text()),
            stop=int(self.inputs['stop'].text()),
            step=int(self.inputs['step'].text()),
        )
        
    def scan(self, args):
        sdr = RtlSdr()
        sdr.sample_rate = sample_rate = 2400000
        sdr.err_ppm = args.ppm
        sdr.gain = args.gain

        lo_frequency = args.lo

        freq = args.start
        radio_stations = []
        last_detected_station = None
        min_distance = 200000  # Minimum distance between stations in Hz
        radio_psd_threshold = 2e-08
        while freq <= args.stop:
            print(f"Scanning frequency: {freq / 1e6} MHz")
            try:
                tune_to_frequency(sdr, freq, lo_frequency)
                iq_samples = self.read_samples(sdr, freq)
                iq_samples = sig.decimate(iq_samples, 48)

                f, psd = sig.welch(iq_samples, fs=sample_rate / 48, nperseg=1024)
                peak_indices, frequencies = find_highest_magnitudes(psd, num_peaks=1, sample_rate=sample_rate / 48, fft_size=1024)

                if peak_indices:
                    peak_index = peak_indices[0]
                    peak_frequency = frequencies[0]
                    peak_psd = psd[peak_index]
                    print(f"Peak frequency: {peak_frequency} Hz, PSD: {peak_psd}")

                    # Group nearby frequencies as one station
                    if peak_psd >= radio_psd_threshold:  # Check if the PSD value is above the radio station threshold
                        print(f"Strong signal found at {freq / 1e6} MHz, PSD: {peak_psd}")  # Print the strong signal as it is found
                        radio_stations.append({'freq': freq, 'psd': peak_psd, 'band': (freq / 1e6)})
                        last_detected_station = radio_stations[-1]

                    if peak_psd >= args.threshold:
                        self.result_list.addItem('{:.3f} MHz - {:.2f}'.format(freq / 1e6, peak_psd * 100))

            except Exception as e:
                print(f"Error occurred while scanning frequency {freq / 1e6} MHz: {str(e)}")

            freq += args.step

        sdr.close()

        print("\nDetected radio stations:")
        for station in radio_stations:
            print(f"Band: {station['freq'] / 1e6} MHz - PSD: {station['psd']}")

        # Harmonic and shape detection
        harmonic_candidates = detect_harmonics(radio_stations)

        print("\nPotential interference sources with strong harmonics and specific PSD shape:")
        for candidate in harmonic_candidates:
            print(f"Frequency: {candidate['freq'] / 1e6} MHz - Harmonics: {candidate['harmonics']}")

    @staticmethod
    def read_samples(sdr, freq):
        f_offset = 250000
        sample_rate = 2400000
        sdr.center_freq = freq - f_offset
        time.sleep(0.01) # originally, 0.06, but too slow
        iq_samples = sdr.read_samples(1024) #originally 1221376, but too slow, the lower this is though the lower the PSD integrity is...btw must be powers of 2...
        iq_samples = iq_samples[0:600000]
        fc1 = np.exp(-1.0j * 2.0 * np.pi * f_offset / sample_rate * np.arange(len(iq_samples)))
        iq_samples = iq_samples * fc1
        return iq_samples


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ScannerApp()
    sys.exit(app.exec_())
