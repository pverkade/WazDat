""" 
    fingerprint.py
"""


import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.io.wavfile import read
from scipy.ndimage.filters import gaussian_filter

import classifier


def get_tokens(signal, window_size=1024, bin_size=2):
    fingerprints = get_fingerprints(signal, window_size, bin_size)
    result = []

    leftoffset = 1
    width = 4
    height = 16
   
    ''' Create tokens using the anchor point method. '''
    
    for time, peaks in fingerprints:
        realtime = time * float(window_size) / signal.get_samplerate()
        for anchorpoint in peaks:
            minfreq = anchorpoint - height / 2
            maxfreq = anchorpoint + height / 2
            for searchtime in xrange(time + leftoffset, min(time + leftoffset + width, len(fingerprints))):
                for matchpoint in fingerprints[searchtime][1]:
                    if minfreq <= matchpoint <= maxfreq:
                        result.append(classifier.Token((anchorpoint, matchpoint, searchtime - time), realtime, signal.get_filename()))

    return result


def get_fingerprints(signal, window_size, bin_size):
    '''
    get spectrogram peaks as (time, frequency) points
    '''

    result = []
    time_samples = get_spectogram(signal, window_size, bin_size)

    width = time_samples.shape[1]
    prev_histogram = np.zeros(width)
    for time, histogram in enumerate(time_samples):
        peaks = get_peaks(histogram - prev_histogram - 25)
        result.append((time, peaks))

        prev_histogram = np.zeros(width)
        for peak in peaks:
            prev_histogram[peak-1:peak+1] = histogram[peak-1:peak+1]
        prev_histogram = gaussian_filter(prev_histogram, 2.)
        prev_histogram *= 1 # np.sum(histogram) / 50.0

    return result


def get_peaks(histogram):
    '''
    Returns the peaks for a given amplitude plot.
    '''
    location_peaks = argrelextrema(np.array(histogram), np.greater)[0]
    peaks = [(i, histogram[i]) for i in location_peaks]
    peaks = sorted(peaks, key=lambda pair: pair[1], reverse=True)

    result = []
    for peak in peaks[:5]:
        if peak[1] > 0 and peak[1] > 0.5 * peaks[0][1]:
            result.append(peak[0])
    return result


def get_spectogram(signal, window_size, bin_size):
    '''
    '''
    samples = signal.get_samples()
    width = len(samples) / window_size
    height = window_size / 2 / bin_size
    window = zero_padded_window(window_size)

    result = np.empty((width, height))
    
    #highpass_filter = np.zeros(height)
    #cutoff_frequency = 100
    #slope = 20
    #for i in xrange(cutoff_frequency):
    #    highpass_filter[i] = 1.

    for t in range(0, width):
        partial_signal = window * samples[t*window_size:(t+1)*window_size]
        spectrum = np.fft.rfft(partial_signal)

        for bin in xrange(height):
            sum = 0.0
            for offset in xrange(bin_size):
                sum += np.abs(spectrum[bin*bin_size+offset])
            result[t][height-bin-1] = sum # * highpass_filter[height-bin-1]

    return result


def zero_padded_window(size):
    return np.ones(size)


def hanning_window(length, index, size):

    return None


def hamming_window(length, index, size):
    return None


def show_spectogram(spectogram):
    plt.imshow(spectogram.T, aspect="auto", interpolation="none")
    ax = plt.gca()
    ax.set_xlabel("Time")
    ax.set_ylabel("Frequencies")
    ax.set_ylim((128, 256))
    ax.set_xlim((0, 23))
    plt.show()


if __name__ == "__main__":
    import soundfiles

    signal = soundfiles.load_wav("training/pokemon/103.wav")
    fingers = get_fingerprints(signal, 1024, 2)
    time = []
    peaks = []

    for t, ps in fingers:
        time  += [t] * len(ps)
        peaks += ps

    print len(peaks)

    plt.scatter(time, peaks, color="red")
    plt.show()

