# VapsToVaps
## Czyszczenie pliku VAPS, przygotowanie do wgrania fo GPSeismic

### Skrypt obrabia plik *.vaps. 
- usuwa nagłówek
- usuwa voidy
- usuwa rekordy bez współrzędnych
- usuwa rekordy z błędami
- wyciąga wysokość na elipsoidzie wgs84 z ciągu #GPGGA i redukuję ją o wysokość wibratora
- czyści descriptory i w to miejsce wstawia informację o jakości pomiaru (4 oznacza, wibrator miał GPS RTK phase)
-> zapisuje plik *_OK.vaps który wgrywa się bezpośrednio do GPSeismica

### Dodatkowo dla Seismologa przygotowuje plik *.force, który zawiera:
- numer linii
- numer punktu
- indeks punktu (z aparatury)
- średnią z average force z wszystkich sweepów dla punktu
- średnią z peak force z wszystkich sweepów dla punktu
- numery ID vibratorów, które wibrowały

### stałe
`CZAS = 5`  # podaj jak długo ma się wyświetlać raport po przygotowaniu plików
`MINIVIB = ('8')`  # po przecinku podaj ID wszystkich univibów. Jeśli nie ma żadnego, podaj jakiś ID niewystępujący wśród wibratorów
`RED_MINI = 2.15`  # redukcja wysokości dla univiba (wysokość zamontowania anteny)
`RED_H50 = 2.75`  # redukcja wysokości dla dużego wibratora (wysokość zamontowania anteny)
