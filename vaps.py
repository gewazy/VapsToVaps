from tkinter import Tk
from tkinter.filedialog import askopenfilename
from time import sleep

'''
12.01.2023
autor: DJurkowski
mail: djurkowski@geofizyka.pl


Skrypt obrabia plik *.vaps. 
- usuwa nagłówek
- usuwa voidy
- usuwa rekordy bez współrzędnych
- usuwa rekordy z błędami
- wyciąga wysokość na elipsoidzie wgs84 z ciągu #GPGGA i redukuję ją o wysokość wibratora
- czyści descriptory i w to miejsce wstawia informację o jakości pomiaru (4 oznacza, wibrator miał GPS RTK phase)
-> zapisuje plik *_OK.vaps który wgrywa się bezpośrednio do GPSeismica

Dodatkowo dla Seismologa przygotowuje plik *.force, który zawiera:
- numer linii
- numer punktu
- indeks punktu (z aparatury)
- średnią z average force z wszystkich sweepów dla punktu
- średnią z peak force z wszystkich sweepów dla punktu
- numery ID vibratorów, które wibrowały

'''


CZAS = 5  # podaj jak długo ma się wyświetlać raport po przygotowaniu plików
MINIVIB = ('8')  # po przecinku podaj ID wszystkich univibów. Jeśli nie ma żadnego, podaj jakiś ID niewystępujący wśród wibratorów
RED_MINI = 2.15  # redukcja wysokości dla univiba (wysokość zamontowania anteny)
RED_H50 = 2.75  # redukcja wysokości dla dużego wibratora (wysokość zamontowania anteny)
SPS_PATTERN = '_daily.sps' # 'końcówka pliku sps, który skrypt ma wyszukać w katalogu z dniówką


Tk().withdraw()
open_filename = askopenfilename()
print("Otworz plik: " + open_filename)
file = open(open_filename, 'r')

sps = []  # przechowuje punkty zaliczone (z pliku *.sps)
with open(f'{open_filename[:-5]}{SPS_PATTERN}', 'r') as file2:
    for row in file2:
        sps.append(row[4:10] + row[12:20] + row[23])
print(f'\nW pliku sps jest {len(sps)} puntów.\n')
sleep(2)

save_filename = open_filename[:-5] + '_OK.vaps'
print("Zapisz plik: " + save_filename)
out_file = open(save_filename, 'w')

nosps = []  # przechowuje VOIDy (do wywalenia z *.vaps)
count = 0

# wypełnianie pliku *_OK.vaps danymi;
for line in file:
    count += 1
    if count > 72:  # usuwa nagłówek
        if '0   0   0 0 0 0  0  0  0      0.0       0.0   0.0' not in line:  # usuwa punkty bez pozycji GPS
            if '$ERROR' not in line:  # usuwa punkty z błędami
                point = line[11:26]
                if point in sps:  # usuwa voidy (punkty których nie ma w sps - ie); do poprawy (bug przy PDOP>99)
                    out_file.write(line[:75] +
                                   str(round((float(line[209:216]) + float(line[219:225]) if line[208] == ',' else (float(line[210:217]) + float(line[220:226]))) -
                                             (RED_MINI if line[28] in MINIVIB else RED_H50), 1)) + line[80:92] + 14 * ' ' + line[200] + 4 * ' ' + line[111:])
                else:
                    nosps.append(point)

file.close()
out_file.close()

print('\nVAPS przerobiony')

# przygotowanie pliku z 'mocami wibratorów'
with open(save_filename, 'r') as file:
    with open(save_filename[:-8] + '.force', 'w') as force:
        force.write('Line\tPoint\tIndex\tFleetID\tno.sweeps\tavg_avg_force\tavg_peak_force\tvib_IDs\n')

        line = file.readline()
        punkt = line[11:27]
        avg_force = int(line[44:46])
        avg_peak = int(line[46:49])
        vibs = [line[28]]
        count = 1

        for line in file:
            if line[11:27] == punkt:
                count += 1
                avg_force += int(line[44:46])
                avg_peak += int(line[46:49])
                vibs.append(line[28])

            else:
                force.write(f'{punkt[:4]}\t{punkt[8:12]}\t{punkt[-2]}\t'
                            f'{punkt[-1]}\t{count}\t{"{:.2f}".format(round(avg_force / count, 2))}\t'
                            f'{"{:.2f}".format(round(avg_peak / count, 2))}\t{vibs}\n')
                punkt = line[11:27]
                count = 1
                avg_force = int(line[44:46])
                avg_peak = int(line[46:49])
                vibs = [line[28]]

        force.write(f'{punkt[:4]}\t{punkt[8:12]}\t{punkt[-2]}\t'
                    f'{punkt[-1]}\t{count}\t{"{:.2f}".format(round(avg_force / count, 2))}\t'
                    f'{"{:.2f}".format(round(avg_peak / count, 2))}\t{vibs}\n')


# raporty
print('\nUWAGA!')
sleep(0.5)

if len(nosps) > 0:
    print('\n  - usunąłem punkty których nie ma w pliku SPS, są to')
    print('    Linia   Punkt Indeks')
    for i in nosps:
        print(f'    {i}')

print('\n  - wysokość w jest na elipsoidzie WGS84'
      f'\n  - wysokości zostały zredukowane o:'
      f'\n     *  {RED_MINI}m dla UniViba'
      f'\n     *  {RED_H50}m dla H50.'
      f'\n  "Height offset" w GPSeismic ustaw 0\n')


for i in range(CZAS + 1):
    print(f"\rOkno zamknie się za {CZAS - i} sekund", end="")
    sleep(1)
