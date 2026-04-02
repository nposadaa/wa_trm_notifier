import os
import requests
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

class WhatsAppClient:
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("PHONE_NUMBER_ID")
        self.api_version = "v22.0"  # Latest version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def send_template_message(self, recipient_number, template_name="hello_world", language_code="en_US", params=None):
        """
        Sends a template message with optional parameters.
        params: List of strings to fill in {{1}}, {{2}}, etc.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        # Build components for parameters if provided
        components = []
        if params:
            parameter_list = [{"type": "text", "text": str(p)} for p in params]
            components.append({
                "type": "body",
                "parameters": parameter_list
            })

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": components
            }
        }
        
        print(f"Sending '{template_name}' template to {recipient_number} with params: {params}...")
        response = requests.post(self.base_url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print("Successfully sent message!")
            print(f"Server Response: {response.json()}")
            return True
        else:
            print(f"Failed to send message. Status: {response.status_code}")
            print(f"Error details: {response.text}")
            return False

if __name__ == "__main__":
    client = WhatsAppClient()
    recipient = os.getenv("RECIPIENT_PHONE_NUMBER")
    
    if not all([client.access_token, client.phone_number_id, recipient]):
        print("Error: Missing credentials or recipient in .env file.")
    else:
        client.send_template_message(recipient)
