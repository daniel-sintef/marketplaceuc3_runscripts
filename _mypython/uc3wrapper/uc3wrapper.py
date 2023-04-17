#!/usr/bin/env python

from ontopy import get_ontology
import owlready2
import json
import math
from properties import *
import pandas as pd

class Quantity:
    def __init__(self, name, iri):
        self.name = name
        self.value = None
        self.unit = None
        self.iri = iri

    def set(self, value, unit):
        self.value = value
        self.unit = unit


INSTALL_PATH="/home/danielma/_mypython/uc3wrapper/"

class Model:
    """
    Parameters
    ----------
    name : string
        Name of the model.
    inputs : sequence
        Sequence of input quantity instances
    outputs : sequence
        Sequence of output quantity instances
    iri : str
        IRI to the corresponding entity in the ontology.
    """
    def __init__(self, name, inputs, outputs, iri):
        self.name = name
        self.input = {input.name: input for input in inputs}
        self.output = {output.name: output for output in outputs}
        self.iri = iri
        self.wrapper = None

    def set_input(self, name, value, unit):
        self.input[name].set(value, unit)

    def set_input_from_quantity(self, quantity):
        self.input[quantity.name] = quantity # this is maybe not smart? Should we copy the values?

    def get_output(self, name):
        """Returns the output quantity."""
        return self.output[name]

    def set_wrapper(self, wrapper):
        self.wrapper = wrapper

    def run(self):
        """run will pass inputs to, and store outputs from wrapper, if wrapper is set."""
        if (self.wrapper == None):
            raise Exception("Wrapper not set for Model %s" % (self.name))

        self.wrapper(self.input, self.output)



def checkModel(inputs, required_inputs):
    """Check that the required inputs are all in the input, and that all values are set"""
    expected_input_names = set(inputs.keys())
    missing_input = required_inputs.difference(expected_input_names)
    if any(missing_input):
        raise RuntimeError('Missing input: %s' % missing_input)
    for input in required_inputs:
        if (inputs[input].value == None):
            raise RuntimeError('%s not set', input)
def get_model_instance(name, onto, wrapper=None):
    """Returns an instance of Model populated with inputs and outputs
    (inferred from the ontology).

    Parameters
    ----------
    name : string
        Name of the model in the ontology.
    onto : emmo.Ontology instance
        The user case ontology.
    """
    inputs = []
    outputs = []
    ontomodel = onto[name]
    for r in ontomodel.is_a:
        if isinstance(r, owlready2.Restriction):
            if r.property == onto.hasInputSpatialPart:
                inputs.append(Quantity(r.value.prefLabel.first(),
                                       r.value.iri))
            elif r.property == onto.hasOutputSpatialPart:
                outputs.append(Quantity(r.value.prefLabel.first(),
                                       r.value.iri))
    model = Model(name, inputs, outputs, ontomodel.iri)
    return model

"""
We need to map the inputs in the model to the concepts in the ontology
The units are for now hard coded. They should probably come from the input
"""
def map_uc3model1(instance):
    uinput= json.loads(open("userinputsmodel1.json", "r").read())
    instance.set_input('PilotMethaneVolumeFlowRate', uinput['Pilotch4fr'], 'l/min')
    instance.set_input('PilotOxygenVolumeFlowRate',  uinput['Piloto2fr'], 'l/min')
    instance.set_input('DispersionVolumeFlowRate', uinput['Dispfr'], 'l/min')
    instance.set_input('FanExtractionVolumeFlowRate', uinput['Fanrate'], 'm3/h')
    instance.set_input('PreCursorVolumeFlowRate', uinput['Precurfr'], 'ml/min')
    instance.set_input('ATSBConcentration', uinput['ATSBcons'], 'mol/l')
    return


"""
We need to map the inputs in the model to the concepts in the ontology
The units are for now hard coded. They should probably come from the input
"""
def map_uc3model3(instance):
    uinput= json.loads(open(INSTALL_PATH+"userinputsmodel3.json", "r").read())
    instance.set_input('ActiveSurfaceArea', uinput['A0'], 'm2/g')
    instance.set_input('PalladiumMassFraction', uinput['X_pd'], '')
    instance.set_input('ActivationEnergy', uinput['Ea'], 'J/mol')
    instance.set_input('CatalystSupportMacroPorosity', uinput['por_cat'], '')
    instance.set_input('MacroporeTortuosity', uinput['tort'], '')
    instance.set_input('MacroPoreAverageRadius', uinput['rp'], 'nm')
    return


"""
This wrapper will use the model inputs to calculate the required FLUENT inputs and store them as outputs.
"""
def uc3model1_wrapper(inputs, outputs):
    alphaATSB   = inputs['ATSBConcentration'].value*mwATSB/rhoATSB
    rhomix      = alphaATSB*rhoATSB+(1.0-alphaATSB)*rhoXylene
    ATSBmf      = alphaATSB*rhoATSB/(alphaATSB*rhoATSB + (1.0-alphaATSB)*rhoXylene)
    Xylenemf    = 1.0 - ATSBmf
    sigmaprec   = sigmaATSB*ATSBmf + (1.0-ATSBmf)*sigmaXylene
    Precmfr     = inputs['PreCursorVolumeFlowRate'].value/1000.0/1000.0/60.0*rhomix
    Precvel     = inputs['PreCursorVolumeFlowRate'].value/1000.0/1000.0/60.0/(math.pi/4.0*dnozzle**2)
    Dispmfr     = mwO2*atm*(inputs['DispersionVolumeFlowRate'].value/1000.0/60.)/rgas/Tref/1000.0
    myprec      = math.exp(ATSBmf*math.log(myATSB)+Xylenemf*math.log(myXylene)-11.24*ATSBmf*Xylenemf)
    Dispgapa    = math.pi/4.0*(gap_outer_diameter**2-gap_inner_diameter**2)
    Dispgavel   = inputs['DispersionVolumeFlowRate'].value/1000.0/60.0/Dispgapa
    Re          = rhomix*(Dispgavel - Precvel)*dnozzle/myprec
    We          = rhomix*(Dispgavel-Precvel)**2*dnozzle/sigmaprec
    Pilotch4mfr = mwMethane*atm*(inputs['PilotMethaneVolumeFlowRate'].value/1000.0/60.0)/rgas/Tref/1000.0
    PilotO2mfr  = mwO2*atm*(inputs['PilotOxygenVolumeFlowRate'].value/1000.0/60.0)/rgas/Tref/1000.0
    Dropsmd     = 51.0*dnozzle*Re**(-0.39)*We**(-0.18)*(Precmfr/Dispmfr)**0.29
    Pilotmfr    = Pilotch4mfr + PilotO2mfr
    Pilotch4mf  = Pilotch4mfr/Pilotmfr
    Piloto2mf   = 1.0 - Pilotch4mf
    Fanextrate  = inputs['FanExtractionVolumeFlowRate'].value*(atm*mwAir/rgas/Tref/1000.0)/3600.0

    """
    Now connect the local variables to the correct outputs
    """
    outputs['ATSBMassFraction'].set(ATSBmf,'')
    outputs['XyleneMassFraction'].set(Xylenemf,'')
    outputs['PreCursorMassFlowRate'].set(Precmfr,'kg/s')
    outputs['PreCursorVelocity'].set(Precvel,'m/s')
    outputs['DispersionMassFlowRate'].set(Dispmfr,'kg/s')
    outputs['DropletSauterMeanDiameter'].set(Dropsmd,'m')
    outputs['PilotMassFlowRate'].set(Pilotmfr,'kg/s')
    outputs['PilotMethaneMassFlowRate'].set(Pilotch4mf,'')
    outputs['PilotOxygenMassFlowRate'].set(Piloto2mf,'')
    outputs['FanExtractionMassFlowRate'].set(Fanextrate,'kg/s')
    return

def uc3model2_wrapper(inputs,outputs):
    journal = open(INSTALL_PATH+"journaltemplate.txt", "r").read()
    fileout = open("Pythongenerated.jou", "w")
    """
    replace the calculated values in the template by mapping the variables in
    the journal template to concepts in the ontology
    """
    out = journal.format(ATSBmf=inputs['ATSBMassFraction'].value, 
                         Xylenemf=inputs['XyleneMassFraction'].value, 
                         Precmfr=inputs['PreCursorMassFlowRate'].value, 
                         Precvel=inputs['PreCursorVelocity'].value, 
                         Dispmfr=inputs['DispersionMassFlowRate'].value, 
                         Dropsmd=inputs['DropletSauterMeanDiameter'].value, 
                         Pilotmfr=inputs['PilotMassFlowRate'].value, 
                         Pilotch4mf=inputs['PilotMethaneMassFlowRate'].value, 
                         Piloto2mf=inputs['PilotOxygenMassFlowRate'].value, 
                         Fanextrate=inputs['FanExtractionMassFlowRate'].value)
    """
    Write the new journal file to disk
    """
    fileout.write(out)
    fileout.close()
    return

def uc3model3_wrapper(inputs,outputs):
    template = open(INSTALL_PATH+"catalystmodeltemplate.txt", "r").read()
    fileout = open("calc.h", "w")
    """
    replace the calculated values in the template by mapping the variables in
    the journal template to concepts in the ontology
    """
    out = template.format(A0=inputs['ActiveSurfaceArea'].value, 
                         X_pd=inputs['PalladiumMassFraction'].value, 
                         Ea=inputs['ActivationEnergy'].value, 
                         por_cat=inputs['CatalystSupportMacroPorosity'].value, 
                         tort=inputs['MacroporeTortuosity'].value, 
                         rp=inputs['MacroPoreAverageRadius'].value, 
                         k0=10000.0) #Not ontologized yet
    """
    Write the new UDF header file to disk
    """
    print("Running FLUENT")
    """
    Parsing the FLUENT output
    """
    lo1 = pd.read_csv("outputmodel3/Monitor-Catalyst-LO1_7.out", delim_whitespace=True, skiprows=3, usecols=[2,4], header=None)
    lo2 = pd.read_csv("outputmodel3/Monitor-Catalyst-LO2_7.out", delim_whitespace=True, skiprows=3, usecols=[2,4], header=None)
    lo3 = pd.read_csv("outputmodel3/Monitor-Catalyst-LO3_7.out", delim_whitespace=True, skiprows=3, usecols=[2,4], header=None)
    lo1.columns=['t','ch4']
    lo2.columns=['t','ch4']
    lo3.columns=['t','ch4']
    outputs['Lightoff1Temperature'].set(lo1.t.to_numpy(),'K')
    outputs['Lightoff1MethaneMassFraction'].set(lo1.ch4.to_numpy(),'-')
    outputs['Lightoff2Temperature'].set(lo2.t.to_numpy(),'K')
    outputs['Lightoff2MethaneMassFraction'].set(lo2.ch4.to_numpy(),'-')
    outputs['Lightoff3Temperature'].set(lo3.t.to_numpy(),'K')
    outputs['Lightoff3MethaneMassFraction'].set(lo3.ch4.to_numpy(),'-')
#     print(lo1)

    fileout.write(out)
    fileout.close()
    return

uc3onto = get_ontology('/home/danielma/_mypython/uc3wrapper/uc3ttlv2.ttl')
uc3onto.load()

#Autogenerate model objects from ontology
uc3model1 = get_model_instance('UC3Model1', uc3onto)
map_uc3model1(uc3model1)
uc3model2 = get_model_instance('UC3Model2', uc3onto)
uc3model3 = get_model_instance('UC3Model3', uc3onto)
map_uc3model3(uc3model3)

#Set wrapper for model 1
uc3model1.set_wrapper(uc3model1_wrapper)
#Run model 1
uc3model1.run()

print('The inputs for model 1 are:')
for i in uc3model1.input.values():
    print(i.name, i.value)
print('The outputs for model 1 are:')
for i in uc3model1.output.values():
    print(i.name, i.value)

"""Transfer output of model 1 to input in model 2 """
for p in uc3model1.output.values():
    uc3model2.set_input_from_quantity(p)
#Set wrapper for model 2
uc3model2.set_wrapper(uc3model2_wrapper)
#Run model 2
uc3model2.run()
print('The inputs for model 2 are:')
for i in uc3model2.input.values():
    print(i.name, i.value)
print('The outputs for model 2 are:')
for i in uc3model2.output.values():
    print(i.name, i.value)

##Set wrapper for model 3
#uc3model3.set_wrapper(uc3model3_wrapper)
##Run model 1
#uc3model3.run()
#
#print('The inputs for model 3 are:')
#for i in uc3model3.input.values():
#    print(i.name, i.value)
#print('The outputs for model 3 are:')
#for i in uc3model3.output.values():
#    print(i.name, i.value)
