virtualenv -p 'where python3.10' venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate