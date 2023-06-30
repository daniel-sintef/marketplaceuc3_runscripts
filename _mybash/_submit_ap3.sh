#!/bin/bash
#SBATCH --no-requeue
#SBATCH --job-name="aiida-177"
#SBATCH --get-user-env
#SBATCH --output=_scheduler-stdout.txt
#SBATCH --error=_scheduler-stderr.txt
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=18

module purge

module load eb
module load GCCcore/.10.3.0
module load Python/3.9.5

module load fluent/2021R2

source /home/$USER/virtualenvs/mpuc3/bin/activate
#PATH=$PATH:/home/$USER/_mypython/uc3_3wrapper

UUID=$(basename $PWD)

# copy over the inputs 
sftp droplet:/home/aiidawork/$UUID/inputs.json ./userinputsmodel3.json

# prep the input files
cp /home/$USER/_mypython/uc3_3wrapper/*.py .
cp /home/$USER/_mypython/uc3_3wrapper/*.txt .
python3 uc3_3wrapper.py
cp -r /home/$USER/Final_A3/* ./



# run FLUENT
export FLUENT_GUI=off
'fluent' '3ddp' '-g' '-t36' '-i' 'Pythongenerated.jou'   

# cleanup 
rm ./core*

# parse the results
python3 ap3_results2json.py $PWD


# copy over the results
sftp droplet:/home/aiidawork/$UUID <<< $'put results.json'
 

 

 
