# Installation

## Setup

### 1. Setup your broker account

setup TOTP for your broker account.
get API key from your broker portal.
This is necessary to programatically access your broker account and do trade functions.

### 2. Install python version 3.9.13 or above till 3.12

you need to download [python 3.9.13](https://www.python.org/downloads/release/python-3913/) and install the appropriate version for
your operating system.

### 3. Install git

[Git](https://git-scm.com/) is required so you can clone any Github repository. We also need  it to
provide continuous integration and delivery. Usually you need to
download [64-bit version of Git](https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe)
The default choice of installation is fine for most cases. You may opt out from experimental features, while installing Git

### 4. Download this repository from Github

You can give any folder name or Create a New folder in any Drive of your choice.

Here, `C:\ecomsense` is the directory, where you want to install this software.

`terminal` directory is for actually project files & dependencies which will be installed.

```
mkdir C:\ecomsense\
cd C:\ecomsense
mkdir terminal
cd terminal
git clone https://github.com/ecomsense/neha-breakout.git
```

if successful, you should be able to see a new directory `neha-breakout` under the current directory

## 5. To setup project

There is a script which will automatically do everything to setup project.

### To Run the setup Script

```
# 1. change the directory to neha-breakout. 

cd neha-breakout


# 2. Now you will be in "C:\ecomsense\terminal\neha-breakout" directory.
```

# 3. install the packages

`pip install -r requirements.txt`

### 6. Run the application

Before we run the application, the credential file needs to be created. Please create a file named as `neha-breakout.yml` in `terminal` folder which you created earlier. Open it in notepad or any other text editor. Modify it suitably according to your stock broker credentials.

```
broker: finvasia
user_id: FN104038
password: <password>
pin: <totp key>
app_key: <api_key>
imei: abc1234
vendor_code: FN104038_U
```

* Fill the above  and paste it to the `breakout_neha.yml` file in `terminal` folder and replace all the placeholders with actual details.

* Note: Make sure you will be in neha-breakout directory.

* run `run_algo.bat`

### 7. Create Shortcuts

There are two bat files `run_algo.bat` and `update.bat` in this folder `neha-breakout`. create desktop shortcuts for them. This way one can run the program by clicking on the `run_algo` without having to run complicated commands from the command line. The `update` shortcut can be clicked whenever the user wants to get the latest updates.

## What do we need to do start the program

If we have successfully installed the application, clicking on the `run_algo` will start the program. It is basically an one liner which activates the virtualenv by running `terminal\venv\Scripts\activate` and then starts the python script using `python main.py` which is inside `terminal\neha-breakout\src`
