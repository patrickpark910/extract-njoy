"""
Bunch of generic helper functions needed to process ENDF data
"""
import re, csv

with open("./Data/element_lookup.csv", newline='') as f:
    reader = csv.DictReader(f)
    ELEMENTS = { row['X']: int(row['Z']) for row in reader }

def endf_float(s):
    """Convert ENDF-style float to Python float.
    i.e. insert 'E' before the final exponent sign: '1.23456+3' → '1.23456E+3'
    """
    s = s.strip()
    s = re.sub(r'([0-9])([+-]\d+)$', r'\1E\2', s)
    return float(s)


def format_nuclide(nuclide: str) -> str:
    """
    Given something like "Li6" (any case), returns "Li006".
    Raises ValueError if it can't parse into letters+digits.
    """
    m = re.match(r'^([A-Za-z]+)(\d+)$', nuclide.strip())
    if not m:
        raise ValueError(f"Cannot parse nuclide {nuclide!r}")
    letters, digits = m.groups()
    symbol = letters.capitalize()          # e.g. "li" -> "Li", "LI" -> "Li"
    mass    = digits.zfill(3)             # e.g. "6" -> "006", "238" -> "238"
    return f"{symbol}{mass}"
    

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