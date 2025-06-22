"""
Bunch of generic helper functions needed to process ENDF data
"""
import re
import periodictable as pt

with open(csv_path, newline='') as f:
    reader = csv.DictReader(f)
    return {
        row['element_symbol']: int(row['atomic_number'])
        for row in reader
    }

def endf_float(s):
    """Convert ENDF-style float to Python float.
    i.e. insert 'E' before the final exponent sign: '1.23456+3' → '1.23456E+3'
    """
    s = s.strip()
    s = re.sub(r'([0-9])([+-]\d+)$', r'\1E\2', s)
    return float(s)

def split_zaid(N):
    
    m = re.match(r'^([A-Za-z]+)(\d+)$', N)
    if not m:
        raise ValueError(f" Fatal. Nuclide string {N!r} is not in <letters><digits> form")
        sys.exit()

    X, A = m.groups()
    A = str(A).zfill(3)
    Z = str(ELEMENTS[X]).zfill(3)

    if len(A) > 3:
        raise ValueError(f"Fatal. Mass number {A} exceeds 3 characters. Ensure input A <=3 digits ex. 'H001'")

    return Z, X, A

""" For testing
"""
if __name__ == '__main__':
    print(split_zaid("H001"))