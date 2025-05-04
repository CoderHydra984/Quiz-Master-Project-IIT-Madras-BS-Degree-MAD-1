#! /bin/sh
echo "======================================================================"
echo "Welcome to to the setup. This will setup the local virtual env." 
echo "You can rerun this without any issues."
echo "----------------------------------------------------------------------"
if [ -d ".venv" ];
then
    echo "Enabling virtual environment venv"
else
    echo "No Virtual environment .venv Please run local_setup.sh first"
    exit N
fi

# Activate virtual .venv
. .venv/bin/activate
export ENV=development
python3 main.py
deactivate
