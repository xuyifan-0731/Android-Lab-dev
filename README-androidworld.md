conda create -n android_world python=3.11.8
conda activate android_world
git clone https://github.com/google-deepmind/android_env.git
cd android_env
python setup.py install
git clone https://github.com/google-research/android_world.git
cd ./android_world
pip install -r requirements.txt
python setup.py install