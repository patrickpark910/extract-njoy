#!/usr/bin/env python3
"""
parse_endf.py

Scan an ENDF-6 file and extract the interpolation schemes
from every MF=3 (pointwise cross section) section.
"""

import sys, re

def test():
    
    fname = "./n-092_U_238.endf"

    try:
        schemes = extract_mf3_interp(fname)
    except Exception as e:
        print("ERROR while parsing:", e)
        sys.exit(2)

    for mt, nreg, bpts, codes in schemes:
        print(f"MF=3, MT={mt}:")
        print(f"  Number of regions : {nreg}")
        print(f"  Breakpoint indices: {bpts}")
        print(f"  Interpolate codes : {codes}")
        print()


def endf_float_to_python(s):
    """Convert ENDF-style float to Python float.
    i.e. insert 'E' before the final exponent sign: '1.23456+3' → '1.23456E+3'
    """
    s = s.strip()
    # 
    s = re.sub(r'([0-9])([+-]\d+)$', r'\1E\2', s)
    return float(s)


def split_record(line):
    """Split an 80-char ENDF line into its six 11-character fields.
       Columns  0–10,11–21,22–32,33–43,44–54,55–65  contain the data
    """ 
    return [line[i*11:(i+1)*11] for i in range(6)]


def parse_int_fields(fields):
    """
    Given a list of six ENDF fields, parse each as an integer.
    ENDF integer fields may be written without any decimal dot,
    but floats in these positions still parse to int after conversion.
    """
    ints = []
    for f in fields:
        tok = f.strip()
        if not tok:
            continue
        try:
            v = int(tok)
        except ValueError:
            # must be something like '1.00000+0'
            v = int(endf_float_to_python(tok))
        ints.append(v)
    return ints


def extract_mf3_interp(filename):
    schemes = []
    with open(filename, 'r') as fh:
        lines = fh.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]
        mf = line[70:72].strip()
        
        if mf == '3':
            mt = int(line[72:75])

            # 1) skip the “MT=0” end-of-section record
            if mt == 0:
                i += 1
                continue

            # advance past the header record
            i += 1

            # read the NR, NP and then the 2*NR break/code ints…
            region_ints = []
            while True:
                rec = lines[i]
                if rec[70:72].strip() != '3':
                    raise RuntimeError(f"MF changed unexpectedly at line {i}")
                region_ints.extend(parse_int_fields(split_record(rec)))
                print(f"on line {i}")
                print(line)
                print(region_ints)
                if len(region_ints) >= 2:
                    NREG, NPTS = region_ints[0], region_ints[1]
                    break
                i += 1

            # grab the rest of the break/code ints
            needed = 2 * NREG - 1
            data = region_ints[2:]
            i += 1

            while len(data) < needed:
                rec = lines[i]
                # print(f"line {i} | len(data) = {len(data)} | needed = {needed}")

                if rec[70:72].strip() != '3':
                    # print(f"len(data) = {len(data)} | needed = {needed}")
                    raise RuntimeError(f"MF changed in interp data at line {i}")
                data.extend(parse_int_fields(split_record(rec)))
                i += 1

            bpts  = data[:NREG]
            codes = data[NREG:2*NREG]
            schemes.append((mt, NREG, bpts, codes))

            # 2) skip the NPTS data lines (each line holds up to 3 pairs)
            n_data_recs = (NPTS + 2) // 3
            i += n_data_recs

        else:
            i += 1

        print(f"line {i}")

    return schemes


if __name__ == "__main__":
    test()
