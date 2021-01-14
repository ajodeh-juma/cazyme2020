#!/usr/bin/env bash

#SBATCH --partition batch
#SBATCH --nodelist compute2
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --output=output_%j.txt
#SBATCH --error=error_output_%j.txt
#SBATCH --job-name=predict_CAZymes.py
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=J.Juma@cgiar.org


# create conda environment
# conda env create -f /home/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/environment.yaml

# activate conda environment
source /home/jjuma/miniconda3/etc/profile.d/conda.sh
conda activate run_dbcan


WORK_DIR="/home/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/scripts/"
GENOMES_DIR="/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/genomes"
DB_DIR="/var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/db/"


#WORK_DIR="/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/scripts/"
#GENOMES_DIR="/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/genomes"
#DB_DIR="/Users/jjuma/Work/Stanley_Onyango/cazyme_project_05102020/db/"



#python3 ${WORK_DIR}/fetch_genomes.py

# dowload genomes
test -d ${DB_DIR} || mkdir ${DB_DIR}
cd ${DB_DIR} \
  && wget http://bcb.unl.edu/dbCAN2/download/CAZyDB.07312019.fa.nr && diamond makedb --in CAZyDB.07312019.fa.nr -d CAZy \
  && wget http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-HMMdb-V8.txt && mv dbCAN-HMMdb-V8.txt dbCAN.txt && hmmpress dbCAN.txt \
  && wget http://bcb.unl.edu/dbCAN2/download/Databases/tcdb.fa && diamond makedb --in tcdb.fa -d tcdb \
  && wget http://bcb.unl.edu/dbCAN2/download/Databases/tf-1.hmm && hmmpress tf-1.hmm \
  && wget http://bcb.unl.edu/dbCAN2/download/Databases/tf-2.hmm && hmmpress tf-2.hmm \
  && wget http://bcb.unl.edu/dbCAN2/download/Databases/stp.hmm && hmmpress stp.hmm

# annotate cazymes
cd ${WORK_DIR} || exit
python3 annotate_cazymes.py \
  --dataDir ${GENOMES_DIR} \
  --seq-type meta \
  --database-dir ${DB_DIR} \
  --tools 'hmmer hotpep diamond'

#python3 annotate_cazymes.py \
#  --dataDir /var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/genomes \
#  --seq-type meta \
#  --database-dir /var/scratch/jjuma/Stanley_Onyango/cazyme_project_05102020/db/ \
#  --tools 'hmmer hotpep diamond'

