import periodictable as pt
import csv

with open('elements.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['element_symbol', 'atomic_number'])
    for elem in pt.elements:
        if elem.number > 0:           # skip the placeholder “0” entry
            writer.writerow([elem.symbol, elem.number])
