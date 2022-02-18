# SteganoEDU: Educational Prototype of a LSB-AES Hybrid Encryption Algorithm

Standalone application to securely exchange information between two peers. It uses a hybrid encryption scheme to exchange images with secret content, applying the AES CBC algorithm, the LSB Steganography algoritm, RSA key-pair exchange algorithm and md5 hash algorithm.

## Installation

You need to have virtualenv installed:
```sh
python -m pip install virtualenv
```

```sh
git clone https://github.com/tdavilab/hybrid-encryption-lsb-aes.git
cd hybrid-encryption-lsb-aes
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
source env/bin/activate
python gui.py
```



![s1](https://user-images.githubusercontent.com/25911836/154664569-60dea46b-de36-4edc-a23f-e348de711c4d.png)
![s2](https://user-images.githubusercontent.com/25911836/154664579-78fcc8c9-dc2d-4967-a46c-7973a0949dc9.png)
