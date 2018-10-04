import * as request from "request-promise-native"


export async function RasaNluRequest(query: string) {
    try {
        query = query.replace(".", "");

        const response: Buffer = await request({
            url: 'http://localhost:5000/parse?project=my_project&q=' + query,
            method: 'GET'
        }, (error, response, body) => {
            if (error) {
                console.log('Error sending message: ', error);
            }
        });
        return response;
    }
    catch (e) {
        return null;
    }
}

export async function KaldiDeRequest(audioBinary: Buffer) {
    try {
        const response: Buffer = await request({
            url: 'http://localhost:13001',
            method: 'POST',
            headers: {
                'Content-Type': 'audio/wav'
            },
            body: audioBinary,
            encoding: null
        }, (error, response, body) => {
            if (error) {
                console.log('Error sending message: ', error);
            }
        });

        return response;
    }
    catch (e) {
        return null;
    }
}

export async function BingSpeechRequest(audioBinary: Buffer) {
    const key = "<<<Bing-API-Key>>>";

    try {
        const token: Buffer = await request({
            url: "https://api.cognitive.microsoft.com/sts/v1.0/issueToken",
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "0",
                "Ocp-Apim-Subscription-Key": key
            },
            body: null
        }, (error, response, body) => {
            if (error) {
                console.log('Error sending message: ', error);
            }
        });

        const locale = "de-DE";
        const format = "audio/wav";

        const urlParameters = "language=" + locale + "&locale=" + locale + "&format=" + format + "&requestid=" + key;
        const response: Buffer = await request({
            url: "https://speech.platform.bing.com/speech/recognition/interactive/cognitiveservices/v1?" + urlParameters,
            method: "POST",
            headers: {
                "Transfer-Encoding": "chunked",
                "Authorization": token.toString(),
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "0",
                "Ocp-Apim-Subscription-Key": key,
                "Content-type": "audio/wav; codec='audio/pcm'; samplerate=16000"
            },
            body: audioBinary,
            encoding: null
        }, (error, response, body) => {
            if (error) {
                console.log("Error sending message: ", error);
            } else {
                // console.log('Response-Header: ', response.headers);
                // console.log('Response-Body:', body);
                // response = response.body;
            }
        });

        return JSON.parse(response.toString());
    }
    catch (e) {
        return null;
    }
}

