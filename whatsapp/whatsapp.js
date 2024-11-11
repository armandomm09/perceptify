const express = require('express');
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { group } = require('console');

const app = express();
app.use(express.json()); // Para parsear JSON en las peticiones

let clientReady = false;
const client = new Client({
    authStrategy: new LocalAuth()
});

// Cuando el cliente esté listo
client.once('ready', async () => {
    console.log('El cliente de WhatsApp está listo.');
    clientReady = true;
    // const chats = await client.getChats();
    // // console.log("Checking chats")
    // // for(let chat of chats){
    // //     if(chat.isGroup && chat.name === "IoT"){
    // //         console.log(chat.id)
    // //     }
    // // }
    // // console.log("no iot")

});

// Generar el código QR
client.on('qr', (qr) => {
    console.log('Escanea este código QR con tu aplicación de WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Iniciar el cliente de WhatsApp
client.initialize();


// Función para enviar mensajes
function sendMessage(number, message, group, img_id) {
    return new Promise(async (resolve, reject) => {
        if (clientReady) {
            const chatId = `${number}@${group ? "g" : "c"}.us`;
            const media_msg = await MessageMedia.fromUrl(`http://localhost:8000/image/${img_id}`, {unsafeMime: true})
            media_msg.mimetype = "image/jpg"
            client.sendMessage(chatId, media_msg, {caption: message})
                .then(response => {
                    console.log(`Mensaje enviado a ${number}: ${message}`);
                    resolve(true);
                })
                .catch(error => {
                    console.error('Error al enviar el mensaje:', error);
                    reject(error);
                });
        } else {
            console.log('El cliente aún no está listo. Intentando nuevamente en 5 segundos...');
            setTimeout(() => {
                sendMessage(number, message).then(resolve).catch(reject);
            }, 5000);
        }
    });
}

// Endpoint para recibir peticiones POST y enviar mensajes
app.post('/send-message', async (req, res) => {
    const { number, message, group, img_id } = req.body;

    if (!number || !message) {
        return res.status(400).send('Faltan parámetros: número y mensaje son requeridos.');
    }

    try {
        await sendMessage(number, message, group, img_id);
        res.send(`Mensaje enviado a ${number}: ${message}`);
    } catch (error) {
        res.status(500).send('Error al enviar el mensaje.');
    }
});

// Iniciar el servidor Express en el puerto 3000
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor Express escuchando en el puerto ${PORT}`);
});
