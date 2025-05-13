import os
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import sqlite3
from io import BytesIO  
from scipy.signal import find_peaks

folder_paths = ['Data/AcousticGuitar', 'Data/WesternGuitar']

db_path = './database.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS FrequencyData (
    file_name TEXT PRIMARY KEY,
    note TEXT,
    fundamental_frequency REAL,
    theoretical_frequency REAL,
    harmonics TEXT,
    fft_plot BLOB,
    comparison_plot BLOB,
    mean_deviation_percent REAL
)
''')

Fs = 50000
tolerance = 0.05  

theoretical_frequencies = {

    'A_001.mat': 110, 'A_002.mat': 110,
    'A_003.mat': 116.54, 'A_004.mat': 116.54,
    'A_005.mat': 220, 'A_006.mat': 220,
    'A_007.mat': 233.08, 'A_008.mat': 233.08,
    'A_009.mat': 440, 'A_010.mat': 440,
    'A_011.mat': 466.16, 'A_012.mat': 466.16,
    'A_013.mat': 880, 'A_014.mat': 880,
    'A_015.mat': 880, 'A_016.mat': 932.33,
    'A_017.mat': 932.33, 'A_018.mat': 123.47,
    'A_019.mat': 123.47, 'A_020.mat': 123.47,
    'A_021.mat': 130.81, 'A_022.mat': 130.81, 
    'A_023.mat': 246.94, 'A_024.mat': 246.94,
    'A_025.mat': 261.63, 'A_026.mat': 261.63, 
    'A_027.mat': 493.88, 'A_028.mat': 493.88,
    'A_029.mat': 130.81, 'A_030.mat': 130.81,
    'A_031.mat': 138.59, 'A_032.mat': 138.59,
    'A_033.mat': 261.63, 'A_034.mat': 261.63,
    'A_035.mat': 277.18, 'A_036.mat': 277.18,
    'A_037.mat': 523.25, 'A_038.mat': 523.25,
    'A_039.mat': 554.37, 'A_040.mat': 554.37,
    'A_041.mat': 146.83, 'A_042.mat': 146.83,
    'A_043.mat': 155.56, 'A_044.mat': 155.56,
    'A_045.mat': 293.66, 'A_046.mat': 293.66,
    'A_047.mat': 311.13, 'A_048.mat': 311.13,
    'A_049.mat': 587.33, 'A_050.mat': 587.33,
    'A_051.mat': 622.25, 'A_052.mat': 622.25,
    'A_053.mat': 164.81, 'A_054.mat': 164.81,  
    'A_055.mat': 164.81, 'A_056.mat': 164.81,
    'A_057.mat': 329.63, 'A_058.mat': 329.63,
    'A_059.mat': 659.26, 'A_060.mat': 659.26,
    'A_061.mat': 174.61, 'A_062.mat': 174.61, 
    'A_063.mat': 185.00, 'A_064.mat': 185.00,
    'A_065.mat': 174.61, 'A_066.mat': 174.61,
    'A_067.mat': 185.00, 'A_068.mat': 185.00,
    'A_069.mat': 349.23, 'A_070.mat': 349.23,
    'A_071.mat': 369.99, 'A_072.mat': 369.99,
    'A_073.mat': 698.46, 'A_074.mat': 698.46,
    'A_075.mat': 739.99, 'A_076.mat': 739.99,
    'A_077.mat': 98.00, 'A_078.mat': 98.00,
    'A_079.mat': 103.83, 'A_080.mat': 103.83,
    'A_081.mat': 196.00, 'A_082.mat': 196.00,
    'A_083.mat': 207.65, 'A_084.mat': 207.65,
    'A_085.mat': 392.00, 'A_086.mat': 392.00,
    'A_087.mat': 415.30, 'A_088.mat': 415.30,
    'A_089.mat': 784.00, 'A_090.mat': 784.00,
    'A_091.mat': 830.61, 'A_092.mat': 830.61,

    'W_001.mat': 110, 'W_002.mat': 110,
    'W_003.mat': 116.54, 'W_004.mat': 116.54,
    'W_005.mat': 220, 'W_006.mat': 220,
    'W_007.mat': 233.08, 'W_008.mat': 233.08,
    'W_009.mat': 440, 'W_010.mat': 440,
    'W_011.mat': 466.16, 'W_012.mat': 466.16,
    'W_013.mat': 880, 'W_014.mat': 880,
    'W_015.mat': 932.33, 'W_016.mat': 932.33,
    'W_017.mat': 123.47, 'W_018.mat': 123.47,
    'W_019.mat': 130.81, 'W_020.mat': 130.81,
    'W_021.mat': 246.94, 'W_022.mat': 246.94,
    'W_023.mat': 261.63, 'W_024.mat': 261.63,
    'W_025.mat': 493.88, 'W_026.mat': 493.88,
    'W_027.mat': 130.81, 'W_028.mat': 130.81,
    'W_029.mat': 138.59, 'W_030.mat': 138.59,
    'W_031.mat': 138.59, 'W_032.mat': 261.63,
    'W_033.mat': 261.63, 'W_034.mat': 277.18,
    'W_035.mat': 277.18, 'W_036.mat': 523.25,
    'W_037.mat': 523.25, 'W_038.mat': 554.37,
    'W_039.mat': 554.37, 'W_040.mat': 146.83,
    'W_041.mat': 146.83, 'W_042.mat': 146.83,
    'W_043.mat': 155.56, 'W_044.mat': 155.56,
    'W_045.mat': 293.66, 'W_046.mat': 293.66,
    'W_047.mat': 311.13, 'W_048.mat': 311.13,
    'W_049.mat': 587.33, 'W_050.mat': 587.33,
    'W_051.mat': 622.25, 'W_052.mat': 622.25,
    'W_053.mat': 164.81, 'W_054.mat': 164.81,
    'W_055.mat': 164.81, 'W_056.mat': 164.81,
    'W_057.mat': 329.63, 'W_058.mat': 329.63,
    'W_059.mat': 659.26, 'W_060.mat': 659.26,
    'W_061.mat': 87.31, 'W_062.mat': 87.31,
    'W_063.mat': 92.50, 'W_064.mat': 92.50,
    'W_065.mat': 174.61, 'W_066.mat': 174.61,
    'W_067.mat': 185.00, 'W_068.mat': 185.00,
    'W_069.mat': 349.23, 'W_070.mat': 349.23,
    'W_071.mat': 369.99, 'W_072.mat': 369.99,
    'W_073.mat': 698.46, 'W_074.mat': 698.46,
    'W_075.mat': 739.99, 'W_076.mat': 739.99,
    'W_077.mat': 98.00, 'W_078.mat': 98.00,
    'W_079.mat': 103.83, 'W_080.mat': 103.83,
    'W_081.mat': 196.00, 'W_082.mat': 196.00,
    'W_083.mat': 207.65, 'W_084.mat': 207.65,
    'W_085.mat': 784.00, 'W_086.mat': 784.00,
    'W_087.mat': 415.30, 'W_088.mat': 415.30,
    'W_089.mat': 784.00, 'W_090.mat': 784.00,
    'W_091.mat': 830.61, 'W_092.mat': 830.61 
}

note_names = {
    110.00: 'A', 110.00: 'A',
    116.54: 'Ais', 116.54: 'Ais',
    220.00: 'a', 220.00: 'a',
    233.08: 'ais', 233.08: 'ais',
    440.00: 'a¹', 440.00: 'a¹',
    466.16: 'ais¹', 466.16: 'ais¹',
    880.00: 'a²', 880.00: 'a²',
    932.33: 'ais²', 932.33: 'ais²',
    123.47: 'H', 123.47: 'H',
    130.81: 'B#2', 130.81: 'B#2',
    246.94: 'h', 246.94: 'h',
    261.63: 'B#3', 261.63: 'B#3',
    493.88: 'h¹', 493.88: 'h¹',
    130.81: 'c', 130.81: 'c',
    138.59: 'cis', 138.59: 'cis',
    261.63: 'c¹', 261.63: 'c¹',
    277.18: 'cis¹', 277.18: 'cis¹',
    523.25: 'c²', 523.25: 'c²',
    554.37: 'cis²', 554.37: 'cis²',
    146.83: 'd', 146.83: 'd',
    155.56: 'dis', 155.56: 'dis',
    293.66: 'd¹', 293.66: 'd¹',
    311.13: 'dis¹', 311.13: 'dis¹',
    587.33: 'd²', 587.33: 'd²',
    622.25: 'dis²', 622.25: 'dis²',
    82.407: 'E', 82.407: 'E',
    164.81: 'e', 164.81: 'e',
    329.63: 'e¹', 329.63: 'e¹',
    659.26: 'e²', 659.26: 'e²',
    87.31: 'F', 87.31: 'F',
    92.50: 'Fis', 92.50: 'Fis',
    174.61: 'f', 174.61: 'f',
    185.00: 'fis', 185.00: 'fis',
    349.23: 'f¹', 349.23: 'f¹',
    369.99: 'fis¹', 369.99: 'fis¹',
    698.46: 'f²', 698.46: 'f²',
    739.99: 'fis²', 739.99: 'fis²',
    98.00: 'G', 98.00: 'G',
    103.83: 'Gis', 103.83: 'Gis',
    196.00: 'g', 196.00: 'g',
    207.65: 'gis', 207.65: 'gis',
    392.00: 'g¹', 392.00: 'g¹',
    415.30: 'gis¹', 415.30: 'gis¹',
    784.00: 'g²', 784.00: 'g²',
    830.61: 'gis²', 830.61: 'gis²',

    110.00: 'A', 110.00: 'A',
    116.54: 'Ais', 116.54: 'Ais',
    220.00: 'a', 220.00: 'a',
    233.08: 'ais', 233.08: 'ais',
    440.00: 'a¹', 440.00: 'a¹',
    466.16: 'ais¹', 466.16: 'ais¹',
    880.00: 'a²', 880.00: 'a²',
    932.33: 'ais²', 932.33: 'ais²',
    123.47: 'H', 123.47: 'H',
    130.81: 'B#2', 130.81: 'B#2',
    246.94: 'h', 246.94: 'h',
    261.63: 'B#3', 261.63: 'B#3',
    493.88: 'h¹', 493.88: 'h¹',
    130.81: 'c', 130.81: 'c',
    138.59: 'cis', 138.59: 'cis',
    138.59: 'cis', 138.59: 'cis',
    261.63: 'c¹', 261.63: 'c¹',
    277.18: 'cis¹', 277.18: 'cis¹',
    523.25: 'c²', 523.25: 'c²',
    554.37: 'cis²', 554.37: 'cis²',
    146.83: 'd', 146.83: 'd',
    155.56: 'dis', 155.56: 'dis',
    293.66: 'd¹', 293.66: 'd¹',
    311.13: 'dis¹', 311.13: 'dis¹',
    587.33: 'd²', 587.33: 'd²',
    622.25: 'dis²', 622.25: 'dis²',
    164.81: 'e', 164.81: 'e',
    164.81: 'e', 164.81: 'e',
    329.63: 'e¹', 329.63: 'e¹',
    659.26: 'e²', 659.26: 'e²',
    87.31: 'F', 87.31: 'F',
    92.50: 'Fis', 92.50: 'Fis',
    174.61: 'f', 174.61: 'f',
    185.00: 'fis', 185.00: 'fis',
    349.23: 'f¹', 349.23: 'f¹',
    369.99: 'fis¹', 369.99: 'fis¹',
    698.46: 'f²', 698.46: 'f²',
    739.99: 'fis²', 739.99: 'fis²',
    98.00: 'G', 98.00: 'G',
    103.83: 'Gis', 103.83: 'Gis',
    196.00: 'g', 196.00: 'g',
    207.65: 'gis', 207.65: 'gis',
    392.00: 'g¹', 392.00: 'g¹',
    415.30: 'gis¹', 415.30: 'gis¹',
    784.00: 'g²', 784.00: 'g²',
    830.61: 'gis²', 830.61: 'gis²',
}

# files to skip
files_to_skip = ['A_013.mat', 'A_014.mat', 'A_032.mat', 'A_059.mat', 'A_060.mat', 'A_079.mat', 'A_089.mat', 'A_092.mat', 'W_029.mat', 'W_061.mat', 'W_075.mat']

# delete if found in database
for file_to_skip in files_to_skip:
    cursor.execute("DELETE FROM FrequencyData WHERE file_name = ?", (file_to_skip,))
    print(f"Deleted {file_to_skip} from database if it existed.")

for folder_path in folder_paths:
    for file_name in sorted(os.listdir(folder_path)): # Sort file names alphabetically
        # skip files that are in files_to_skip
        if file_name in files_to_skip:
            print(f"Skipping {file_name}")
            continue

        if file_name.endswith('.mat'):
            full_path = os.path.join(folder_path, file_name)
            
            mat_data = scipy.io.loadmat(full_path)
            amplitudes = mat_data['Y19'].flatten()
            frequencies = mat_data['Y19_X'].flatten()
            
            N = len(amplitudes)
            Y = np.fft.fft(amplitudes)
            Y_magnitude = np.abs(Y) / N
            f = np.fft.fftfreq(N, d=1/Fs)

            mask = f > 0
            f = f[mask]
            Y_magnitude = Y_magnitude[mask]

            peak_idx = np.argmax(Y_magnitude)       # argmax finds the highest peak in "Y_magnitude"
            fundamental_frequency = round(f[peak_idx], 2)     # f contains the frequencies of the FFT and "f[peak_idx]" gives back the actual frequency, rounds the number too to 2 decimals
            print(f"Fundamental Frequency ({file_name}): {fundamental_frequency:.2f} Hz")   # simple print function to Print the frequency with two decimal places aswell as the name of the file

            num_harmonics = 30      # Increased from 10 to 30 harmonics for the synthesizer sliders
            harmonics = [fundamental_frequency * (i + 1) for i in range(num_harmonics)]  # creates a list of harmonic frequencies, it multiplies the fundamental frequency with the range of harmonic numbers
            valid_peaks = []    # empty list to be able to store the peaks later

            for i, harmonic in enumerate(harmonics):    # loops through each harmonic number
                f_min = harmonic * (1 - tolerance)      # is used for the frequency range, to detect a harmonic, it defines the lower bound
                f_max = harmonic * (1 + tolerance)      # is used for the frequency range, to detect a harmonic, it defines the upper bound

                idx_in_range = np.where((f >= f_min) & (f <= f_max))[0]     # finds the indices of frequency values that lie between the ranges

                if len(idx_in_range) > 0:       # checking if there are any frequencies in the allowed range
                    idx_peak = idx_in_range[np.argmax(Y_magnitude[idx_in_range])]   # selects the strongest peak in the given range
                    valid_peaks.append((f[idx_peak], Y_magnitude[idx_peak]))        # stores the detected frequency and the coresponding amplitude
                else:
                    valid_peaks.append((None, None))    # if no valid peaks are found "(None, None)" is stored

            harmonic_frequencies = [freq for freq, amp in valid_peaks if freq is not None]  # list of all detected harmonic frequencies 
            harmonic_amplitudes = [amp for freq, amp in valid_peaks if amp is not None]     # list of all the amplitudes


            theoretical_frequency = theoretical_frequencies.get(file_name, 0)   # retrieves the theoretical frequency from the dictionary
            note = note_names.get(theoretical_frequency, "Unknown")             # retrieves the note corresponding to the theoretical frequency

            # Only use the first 10 harmonics for plotting and mean deviation calculation
            display_harmonics = 10  # Limit display to first 10 harmonics
            
            # Calculate mean deviation in percent (limited to first 10 harmonics)
            deviations = []
            # Limit the calculation to the first 10 harmonics
            first_10_harmonic_frequencies = harmonic_frequencies[:display_harmonics] if len(harmonic_frequencies) >= display_harmonics else harmonic_frequencies
            for i, (measured_freq, theoretical_freq) in enumerate(zip(first_10_harmonic_frequencies, [theoretical_frequency * (i + 1) for i in range(len(first_10_harmonic_frequencies))])):
                if measured_freq is not None and theoretical_freq != 0:
                    deviation = abs(measured_freq - theoretical_freq) / theoretical_freq * 100
                    deviations.append(deviation)

            mean_deviation_percent = np.mean(deviations) if deviations else 0   # calculate mean deviation in percent
            mean_deviation_percent = round(mean_deviation_percent, 3)
            display_harmonic_frequencies = harmonic_frequencies[:display_harmonics] if len(harmonic_frequencies) >= display_harmonics else harmonic_frequencies
            display_harmonic_amplitudes = harmonic_amplitudes[:display_harmonics] if len(harmonic_amplitudes) >= display_harmonics else harmonic_amplitudes
            
            plt.figure(figsize=(10, 6))
            markerline, stemlines, baseline = plt.stem(
                display_harmonic_frequencies, display_harmonic_amplitudes, linefmt='#704422', basefmt="k-"
            )
            plt.setp(stemlines, linewidth=1)

            plt.title(f'Frequency spectrum: {file_name}')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Amplitude')
            plt.yscale('log')

            fft_img_buffer = BytesIO()
            plt.savefig(fft_img_buffer, format='png')
            fft_img_buffer.seek(0)
            fft_plot_blob = fft_img_buffer.read()
            plt.close()

            plt.figure(figsize=(10, 6))
            # Limit comparison plot to first 10 harmonics
            display_valid_peaks = valid_peaks[:display_harmonics] if len(valid_peaks) >= display_harmonics else valid_peaks
            harmonics_numbers = list(range(1, len(display_valid_peaks) + 1))
            theoretical_harmonics = [theoretical_frequency * n for n in harmonics_numbers]
            measured_harmonics = [freq if freq is not None else 0 for freq, _ in display_valid_peaks]

            plt.bar(harmonics_numbers, measured_harmonics, width=0.4, label='Measured', color='#C19A6B', alpha=0.6, align='center')
            plt.bar(harmonics_numbers, theoretical_harmonics, width=0.4, label='Theoretical', color='#704422', alpha=0.6, align='edge')

            for i, (measured, theoretical) in enumerate(zip(measured_harmonics, theoretical_harmonics)):
                diff = measured - theoretical if measured != 0 else 0
                percentage_diff = (diff / theoretical) * 100 if theoretical != 0 else 0
                plt.text(i + 1, max(measured, theoretical) + 5, f"{diff:.1f} Hz\n({percentage_diff:.1f}%)", ha='center', fontsize=9)

            plt.title(f'Measured vs Theoretical Frequencies: {file_name}')
            plt.xlabel('Harmonic Number')
            plt.ylabel('Frequency (Hz)')
            plt.legend()
            plt.grid()

            comparison_img_buffer = BytesIO()
            plt.savefig(comparison_img_buffer, format='png')
            comparison_img_buffer.seek(0)
            comparison_plot_blob = comparison_img_buffer.read()
            plt.close()

            cursor.execute('''
            INSERT OR REPLACE INTO FrequencyData (file_name, note, fundamental_frequency, theoretical_frequency, harmonics, fft_plot, comparison_plot, mean_deviation_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_name, note, fundamental_frequency, theoretical_frequency, ','.join(map(str, harmonics)), fft_plot_blob, comparison_plot_blob, mean_deviation_percent))

connection.commit()
connection.close()

print("Upload Finished.")

