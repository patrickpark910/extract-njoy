import numpy as numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
import pandas as pd

def main():
    """ Import and configure xs data
    """
    datapath = "./Data/u238_fis.csv"
    data = pd.read_csv(datapath, header=None, skiprows=1, names=['E','xs']) # skips first line
    data_E, data_xs = data['E'].tolist(), data['xs'].tolist()
    plt.rcParams["font.family"] = "Arial"

    plot(data_E, data_xs, 'full',  filename='./Figures/U238_XSfis_E0full.pdf',  show=True)
    plot(data_E, data_xs, 'therm', filename='./Figures/U238_XSfis_E1therm.pdf', show=True)
    plot(data_E, data_xs, 'inter', filename='./Figures/U238_XSfis_E2inter.pdf', show=True)
    plot(data_E, data_xs, 'fast',  filename='./Figures/U238_XSfis_E3fast.pdf',  show=True)


def plot(x, y, er, filename=None, show=False):
    E_0, E_therm, E_inter, E_fast = 1e-4, 1, 100e3, 10e6

    fig, ax = plt.subplots()

    """ Naive linear interpolation (connect-the-dots)
    """
    ax.plot(x, y, linewidth=1, label='linear')


    """ Naive linear interpolation (connect-the-dots)
    """
    # ax.plot(x, y, linewidth=1, label='linear')


    """ OpenMC (5 interpolation schemes)
    """
    # ax.plot(x, y, linewidth=1, label='linear')


    """ Plot settings
    """
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Incident neutron energy [eV]')
    ax.set_ylabel(r'Cross section, $\sigma$ [b]')
    ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0,), numticks=20))
    ax.minorticks_on()



    ax.set_xlim(E_0,E_fast)
    ax.set_ylim(1e-10,1e0)
    fig.set_size_inches(6, 3)

    if er == 'therm': 
        ax.set_xlim(E_0,E_therm)
        ax.set_ylim(1e-6,1e-3)

    elif er == 'inter': 
        ax.set_xlim(E_therm,E_inter)

    elif er == 'fast': 
        ax.set_xlim(E_inter,E_fast)
        ax.set_ylim(1e-5,1e0)

    # if filename: fig.savefig(filename, format="pdf", bbox_inches='tight')
    if show: plt.show()

if __name__ == '__main__':
    main()



