import requests

def notify_fall_detection(phone_number: str, message: str, group:bool, img_id: int):
    try:
        url = 'http://localhost:3000/send-message'  
        payload = {
            'number': phone_number,
            'message': message,
            'group': group,
            'img_id': img_id
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print('Notificación de caída enviada exitosamente.')
            print('Respuesta del servidor:', response.text)
        else:
            print('Error al enviar la notificación de caída.')
            print('Código de estado:', response.status_code)
            print('Respuesta del servidor:', response.text)
    except Exception as e:
        print(f"Error al realizar la solicitud HTTP: {e}")

