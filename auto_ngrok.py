import os
import time
import requests
import subprocess
import json


# Configuration
try:
    config=json.load(open("config.json"))
except Exception as e:
    print(f"Error loading config.json: {e}")
    with open("config.json", "w") as f:
        json.dump({"port":22,
"type":"tcp",
"token":"",
"website":"https://www.google.com",
"interval":60,
"ngrok_binary":"/usr/local/bin/ngrok"}, f, indent=4)
    print("a config file has been created, please edit the file and try again")
    exit(1)

NGROK_AUTH_TOKEN = config["token"]  # Replace with your ngrok auth token
TUNNEL_TYPE=config["type"]
PORT=config["port"]
WEBSITE_TO_CHECK = config["website"]  # Website to check for internet connectivity
CHECK_INTERVAL = config["interval"]  # Time interval between checks in seconds
NGROK_BINARY=config["ngrok_binary"]
#check ngrok binary
if not os.path.exists(NGROK_BINARY):
    print(f"Error: {NGROK_BINARY} does not exist.")
    print("ngrok can be downloaded from https://www.ngrok.com")
    exit(1)
    
# Function to check internet connectivity
def check_internet():
    try:
        response = requests.get(WEBSITE_TO_CHECK, timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

# Function to start ngrok SSH tunnel
def start_ngrok():
    print("Starting ngrok  tunnel...")
    os.system(f'ngrok authtoken {NGROK_AUTH_TOKEN}')
    process = subprocess.Popen([NGROK_BINARY, TUNNEL_TYPE, PORT], stdout=subprocess.PIPE)

    time.sleep(5)  # Give ngrok time to establish the tunnel
    ngrok_tunnel_url = None
    try:
        ngrok_tunnel_url = requests.get("http://127.0.0.1:4040/api/tunnels").json()["tunnels"][0]["public_url"]
    except (requests.RequestException, IndexError, KeyError) as e:
        print(f"Error getting ngrok tunnel URL: {e}")
    finally:
        return ngrok_tunnel_url, process

# Function to kill the ngrok process
def kill_ngrok(process):
    if process is not None:
        process.terminate()
        process.wait()
        print("Ngrok process terminated.")

if __name__ == "__main__":
    ngrok_process = None
    while True:
        if check_internet():
            print("Internet connection detected.")
            if not ngrok_process or ngrok_process.poll() is not None or ngrok_process is not  None:
                ngrok_tunnel_url, ngrok_process = start_ngrok()
                if ngrok_tunnel_url:
                    #TODO agregar opciones para tuneles no SSH 
                    print(f"Ngrok tunnel established: {ngrok_tunnel_url}")
                    print("To connect, use: ssh -p <port> <your_username>@<your_ngrok_url>")
                    #urlt=f"https://api.telegram.org/bot6311720356:AAF-09bAksBjwq-FMM9QttHKQ9BPs23Ebv8/sendMessage?chat_id=-1001965096659&text=BLUEMDEICAL ssh {ngrok_tunnel_url}"
                    #try:
                    #    tele=requests.get(urlt)
                    #except:
                    #    pass    
                else:
                    print("Failed to establish ngrok tunnel.")
            else:
                print("Ngrok tunnel is already running.")
        else:
            print("No internet connection. Retrying in 60 seconds...")
            kill_ngrok(ngrok_process)
            ngrok_process = None

        time.sleep(CHECK_INTERVAL)
