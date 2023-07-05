import json
import math


def uc3_3wrapper():
    nchannel = 132
    channelfrac = 0.125
    mwch4 = 16.04
    mwh2o = 18.02
    mwo2 = 32.0
    mwn2 = 28.01
    Rgas = 8.314
    Tref = 273.15

    uinput = json.loads(open("userinputsmodel3.json", "r").read())
    journal = open("journaltemplate.txt", "r").read()
    header = open("headertemplate.txt", "r").read()
    fileout1 = open("Pythongenerated.jou", "w")
    fileout2 = open("catalyst_monolith_channel.h", "w")

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
        * (uinput["gfr"] / 60.0 / 1000.0)
        / Rgas
        / Tref
        / nchannel
        * channelfrac
    )
    inlet_methane_mole_fraction = uinput["ch4mf"]
    inlet_water_mole_fraction = uinput["h2omf"]
    inlet_oxygen_mole_fraction = 0.21 * (
        1.0 - inlet_methane_mole_fraction - inlet_water_mole_fraction
    )
    A_ = uinput["surfa"]
    X_ = uinput["amf"]
    washcoat = 1 - uinput['macropor']
    out1 = journal.format(
        inlet_mass_flow_rate=inlet_mass_flow_rate,
        inlet_methane_mole_fraction=inlet_methane_mole_fraction,
        inlet_water_mole_fraction=inlet_water_mole_fraction,
        inlet_oxygen_mole_fraction=inlet_oxygen_mole_fraction,
        A_=A_,
        X_=X_,
        washcoat=washcoat
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
        tort=tort,
        logk01=logk01,
        Ea1=Ea1,
        logk02=logk02,
        Ea2=Ea2,
        logK0eq=logK0eq,
        dH=dH
    )
    fileout1.write(out1)
    fileout1.close()
    fileout2.write(out2)
    fileout2.close()


uc3_3wrapper()
