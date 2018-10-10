import * as express from "express"
import * as request from "request-promise-native"
import * as fs from "fs"
import * as bodyParser from "body-parser"

import { KaldiDeRequest, BingSpeechRequest, RasaNluRequest, MaryTTSRequest } from "./Requests"


export function startServer() {
    const app = express();

    app.use(express.static('public'));

    // app.use(bodyParser.json());
    // app.use(bodyParser.urlencoded({ extended: true, limit: "1mb" }));
    // app.use(bodyParser.text());
    app.use(bodyParser.raw({ type: "*/*", limit: "10mb" }));
    app.use((req, res, next) => {
        // console.log(req.headers);
        // console.log('I saw ' + req.body.length + ' bytes in the body');

        next();
    });

    // Resolve: GET /
    app.get("/", async (req, res) => {

        res.json({
            "/api/v1": {
                desc: "Base",
                parameters: [

                ],
                children: [
                    {
                        "/speech": {
                            desc: "Speech to text",
                            parameters: [
                            ],
                            children: [

                            ]
                        }
                    }
                ]
            }
        });
    });

    app.get("/test/", async (req, res) => {
        res.writeHead(200, {
            "Content-Type": "text/plain"
        });
        res.end("Test");
    })

    app.get("/api/tts/", async (req, res) => {
        const q = req.query["text"];

        // var mp3_file = fs.createWriteStream("public/tts.mp3");

        // request 
        //     .get("https://translate.google.com/translate_tts?ie=UTF-8&q=" + q + "&tl=de-DE&client=tw-ob")
        //     .on('error', function (err) {
        //         console.log(err);
        //     })
        //     .on('data', function (data) {
        //         mp3_file.write(data);
        //     })
        //     .on('end', function(){
        //         mp3_file.end();
        //     });


        const maryResponse = await MaryTTSRequest(q);

        var file = fs.createWriteStream("public/tts.wav");
        file.end(maryResponse);

        res.writeHead(200, {
            "Content-Type": "audio/wav"
            // "Content-Type": "text/plain"
        });
        res.end(maryResponse);
    })

    app.post("/api/speech/", async (req, res) => {
        const lang = req.query["lang"];

        const bingResponse = await BingSpeechRequest(req.body);
        // console.log(bingResponse);

        // let response = await KaldiDeRequest(req.body);
        
        if (bingResponse) {
            res.writeHead(200, {
                "Content-Type": "text/plain",
                "Connection": "close"
            });
            res.end(bingResponse.DisplayText);
        }
        else {
            res.writeHead(500, "Internal server error.");
            res.end();
        }
    });

    app.get("/api/intent", async (req, res) => {
        const lang = req.query["lang"] as string;
        const query = req.query["q"] as string;

        const response = await RasaNluRequest(query);

        if (response) {
            res.writeHead(200, {
                "Content-Type": "application/json",
                // "Content-Type": "text/plain",
                "Connection": "close"
            });
            res.end(response);
        }
        else {
            res.writeHead(500, "Internal server error.");
            res.end();
        }
    });

    app.listen(3000, "0.0.0.0", () => {
        console.log("Example app listening on port 3000!");
    });
}
