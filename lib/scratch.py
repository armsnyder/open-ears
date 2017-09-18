import trigger
from scipy.io.wavfile import read
w = read('../test_resources/bad_02.wav')
trigger.calculate_phon(w[0], w[1])
