#set environmental variables for config.py
pip install -r requirements.txt
yarn --cwd src/frontend install
yarn --cwd src/frontend build
python -m flask run
