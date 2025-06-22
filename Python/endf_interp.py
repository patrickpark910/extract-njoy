# endf_interp.py

import numpy as np

def test():
    """
    Quick functionality test if you run this file directly.

    Usage:
      E_pts, Y_pts = lists of energies and cross sections
      bpts  = breakpoint index of interpolation scheme
      codes = interpolation code
        ex. bpt = [3, 5], code = [1, 2] means 
        (E1, Y1), (E2, Y2), (E3, Y3) are interpolated by scheme 1
        (E3, Y3), (E4, Y4), (E5, Y5) are interpolated by scheme 2
    """
    E_pts = [1e0, 1e1, 1e2, 1e3]
    Y_pts = [1.0, 2.0, 4.0, 8.0]
    bpts  = [2, 4]  
    codes = [1, 4]

    interp = ENDFInterpolator(E_pts, Y_pts, bpts, codes)

    for E in [1.0, 5.0, 10.0, 100.0, 500.0, 1000.0]:
        print(f"E={E:8.2f},  σ={interp(E):.5f}")

class ENDFInterpolator:
    """
    Implements ENDF‐6 MF3‐style interpolation:
      energy regions split by 'bpts' / 'codes' arrays, 
      where points within each region are interpolated by
      code = 1: linear–linear
             2: linear–log
             3: log–linear
             4: log–log

    Usage:
      First set up the class as an object
        ex. interp = ENDFInterpolator(E_pts, Y_pts, bpts, codes)
      Then you can call it like a function to return the sigma for a given energy
        ex. sigma = interp(1e6)           
      You can also input a list of energies and get out a list of xs's
        ex. sig_array = interp([1e3,1e4]) 
    """
    def __init__(self, E_pts, Y_pts, bpts, codes):
        self.E = np.asarray(E_pts, dtype=float)
        self.Y = np.asarray(Y_pts, dtype=float)
        if self.E.ndim != 1 or self.Y.ndim != 1:
            raise ValueError("E_pts and Y_pts must be 1D arrays")
        if self.E.shape != self.Y.shape:
            raise ValueError("E_pts and Y_pts length mismatch")

        # convert 1-based ENDF breakpoints to 0-based indices
        self.bpts = [int(b)-1 for b in bpts]
        if len(self.bpts) != len(codes):
            raise ValueError("len(bpts) must equal len(codes)")
        self.codes = list(codes)


    def __call__(self, E_input):
        xq = np.atleast_1d(E_input).astype(float)
        out = np.empty_like(xq)

        for i, x in enumerate(xq):
            # check domain
            if x < self.E[0] or x > self.E[-1]:
                raise ValueError(f"Energy {x} outside [{self.E[0]}, {self.E[-1]}]")

            # find segment index j so that E[j] <= x <= E[j+1]
            j = np.searchsorted(self.E, x, side='left') - 1
            if j < 0:
                j = 0
            if j >= len(self.E)-1:
                j = len(self.E)-2

            # pick region k: first breakpoint beyond j
            k = next(idx for idx, bp in enumerate(self.bpts) if j < bp)
            code = self.codes[k]

            x1, x2 = self.E[j], self.E[j+1]
            y1, y2 = self.Y[j], self.Y[j+1]

            # perform the proper interpolation
            if code == 1:           # linear–linear
                y = y1 + (y2-y1)*( (x-x1)/(x2-x1) )
            elif code == 2:         # linear–log
                y = np.exp(
                    np.log(y1) +
                    (np.log(y2)-np.log(y1))*( (x-x1)/(x2-x1) )
                    )
            elif code == 3:         # log–linear
                y = y1 + (y2-y1)*( (np.log(x)-np.log(x1)) / (np.log(x2)-np.log(x1)) )
            elif code == 4:         # log–log
                y = np.exp(
                    np.log(y1) +
                    (np.log(y2)-np.log(y1))*
                    ( (np.log(x)-np.log(x1)) / (np.log(x2)-np.log(x1)) )
                    )
            else:
                raise ValueError(f"Unknown interp code {code} in region {k}")

            out[i] = y

        return out.item() if np.isscalar(E_input) else out


if __name__ == "__main__":
    test()
