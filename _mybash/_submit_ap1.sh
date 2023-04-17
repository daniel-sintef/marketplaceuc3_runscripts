#!/bin/bash
#SBATCH --no-requeue
#SBATCH --job-name="aiida-177"
#SBATCH --get-user-env
#SBATCH --output=_scheduler-stdout.txt
#SBATCH --error=_scheduler-stderr.txt
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=20

module purge

module load eb
module load GCCcore/.10.3.0
module load Python/3.9.5

module load fluent/2020R1

source /home/$USER/virtualenvs/mpuc3_ontology/bin/activate
PATH=$PATH:/home/$USER/uc3run_scripts/_mypython/uc3wrapper

UUID=$(basename $PWD)

# copy over the inputs 
sftp droplet:/home/aiidawork/$UUID/inputs.json ./userinputsmodel1.json

# prep the input files
uc3wrapper.py
cp -r /home/$USER/Final_A1flame/* ./

# run FLUENT
export FLUENT_GUI=off
'/share/apps/modulessoftware/ansys_inc/v201/fluent/bin/fluent' '2ddp' '-g' '-slurm' '-pinfiniband' '-t20' '-i' 'Pythongenerated.jou'   

# cleanup 
rm ./core*

# parse the results
uc3_parser.py $PWD


# copy over the results
sftp droplet:/home/aiidawork/$UUID <<< $'put results.json'
 

 

 
