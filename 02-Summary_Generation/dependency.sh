#openai-dependency creation script

apt install python3.9-venv
python3.9 -m venv ./openai-dependency  # Create a virtual environment
source ./openai-dependency/bin/activate  # Activate the virtual environment
python3.9 -m pip install --upgrade pip  # Upgrade pip
python3.9 -m pip install openai  # Install boto3
deactivate  # Deactivate the virtual environment

zip -r openai-dependency.zip ./openai-dependency/lib/python3.9/site-packages/

