#!/bin/bash
#SBATCH --no-requeue
#SBATCH --job-name="aiida-177"
#SBATCH --get-user-env
#SBATCH --output=_scheduler-stdout.txt
#SBATCH --error=_scheduler-stderr.txt
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH -p norma2
#SBATCH -t 0-01:0:0     # upper time limit of 1 hour for the job

module purge

module load eb
module load GCCcore/.10.3.0
module load Python/3.9.5

module load fluent/2021R2

source /home/$USER/virtualenvs/mpuc3/bin/activate
PATH=$PATH:/home/$USER/_mypython/uc3wrapper

UUID=$(basename $PWD)

# copy over the inputs 
sftp droplet:/home/aiidawork/$UUID/inputs.json ./userinputsmodel2.json

# prep the input files
cp /home/$USER/_mypython/uc3_2wrapper/*.py .
cp /home/$USER/_mypython/uc3_2wrapper/*.txt .
python3 uc3_2wrapper.py
cp -r /home/$USER/Final_A2/* ./

# run FLUENT
export FLUENT_GUI=off
'fluent' '2ddp' '-g' '-t4' '-i' 'Pythongenerated.jou'   

# cleanup 
rm ./core*

# parse the results
python3 ap2_results2json.py $PWD


# copy over the results
sftp droplet:/home/aiidawork/$UUID <<< $'put results.json'
 

 

 
