#!/usr/bin/env python

import json
import math


def uc3_2wrapper():
    bedl = 0.01
    beddi = 0.004
    powdermass = 0.1 / 1000.0
    rhocorderite = 1600.0
    rhoalumina = 850.0
    mwch4 = 16.04
    mwh2o = 18.02
    mwo2 = 32.0
    mwn2 = 28.01
    Rgas = 8.314
    Tref = 273.15

    uinput = json.loads(open("userinputsmodel2.json", "r").read())
    journal = open("journaltemplate.txt", "r").read()
    header = open("headertemplate.txt", "r").read()
    fileout1 = open("Pythongenerated.jou", "w")
    fileout2 = open("Pythongenerated.h", "w")

    bedvol = math.pi / 4.0 * beddi**2 * bedl

    corderite = uinput["dmf"] * powdermass / rhocorderite / bedvol
    alumina = (1.0 - uinput["dmf"]) * powdermass / rhoalumina / bedvol

    ch4mf = uinput["ch4mf"]
    h2omf = uinput["h2omf"]
    mwavg = (
        ch4mf * mwch4
        + h2omf * mwh2o
        + 0.21 * (1.0 - ch4mf - h2omf) * mwo2
        + 0.79 * (1.0 - ch4mf - h2omf) * mwn2
    )

    inlet_mass_flow_rate = (
        (mwavg / 1000.0)
        * 101325.0
        * (uinput["gfr"] / 60.0 / 1000.0 / 1000.0)
        / Rgas
        / Tref
    )
    inlet_methane_mole_fraction = uinput["ch4mf"]
    inlet_water_mole_fraction = uinput["h2omf"]
    inlet_oxygen_mole_fraction = 0.21 * (
        1.0 - inlet_methane_mole_fraction - inlet_water_mole_fraction
    )
    A_ = uinput["surfa"]
    X_ = uinput["amf"]
    out1 = journal.format(
        corderite=corderite,
        alumina=alumina,
        inlet_mass_flow_rate=inlet_mass_flow_rate,
        inlet_methane_mole_fraction=inlet_methane_mole_fraction,
        inlet_water_mole_fraction=inlet_water_mole_fraction,
        inlet_oxygen_mole_fraction=inlet_oxygen_mole_fraction,
        A_=A_,
        X_=X_,
    )
    por_cat = uinput["macropor"]
    tort = uinput["macrotor"]
    logk01 = math.log10(uinput["k1"])
    Ea1 = uinput["ea1"]
    logk02 = math.log10(uinput["k2"])
    Ea2 = uinput["ea2"]
    logK0eq = math.log10(uinput["koeq"])
    dH = uinput["dhh20"]
    out2 = header.format(
        por_cat=por_cat,
        tort=tort,
        logk01=logk01,
        Ea1=Ea1,
        logk02=logk02,
        Ea2=Ea2,
        logK0eq=logK0eq,
        dH=dH,
    )
    fileout1.write(out1)
    fileout1.close()
    fileout2.write(out2)
    fileout2.close()


uc3_2wrapper()
