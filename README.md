# STEGANO-AES Application

Standalone application to securely exchange information between two peers. It uses a hybrid encryption scheme to exchange images with secret content, applying the AES CBC algorithm, the LSB Steganography algoritm, RSA key-pair exchange algorithm and md5 hash algorithm.

## Installation

You need to have virtualenv installed:
```sh
python -m pip install virtualenv
```

```sh
git clone https://github.com/tdavilab/Cifrado-Hibrido-Esteganografia.git
cd Cifrado-Hibrido-Esteganografia
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
source env/bin/activate
python gui.py
```



