import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';
import sse from 'k6/x/sse';

let TTFT = new Trend('TTFT');  //ms
let TPoT = new Trend('TPoT');  //ms
let WaitingTime = new Trend('WaitingTime');  //ms
let Throughput = new Trend('Throughput');  //tokens/sec
let TotalTokens = new Counter('TotalTokens');

export let options = {
    stages: [
        { duration: '1m', target: 1 },
        { duration: '1m', target: 2 },
        { duration: '1m', target: 0 },
    ],
};

export default function () {
    let requestStart = Date.now();

    const url = 'http://chat-app-cpu-service:8000/generate/';
    // const url = 'http://k6-datadog:8000/generate/';

    const params = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
            query: "日本で最も高い山は何ですか？",
        }),
    };

    let tokenCount = 0;
    const response = sse.open(url, params, function (client) {
        let ttftCaptured = false;
        let tokenTimes = [];
        let firstTokenTime = 0;

        client.on('event', function (event) {
            console.log(`event id=${event.id}, name=${event.name}, data=${event.data}`);
            if (parseInt(event.id) === 2) {
                client.close()
            }
            let chunkTime = Date.now();
            let data = event.data.trim();

            if (data === '') {
                return;
            }
            if (data === '[DONE]') {
                client.close();
                return;
            }

            if (!ttftCaptured) {
                firstTokenTime = chunkTime;
                let ttft = firstTokenTime - requestStart;
                TTFT.add(ttft);
                ttftCaptured = true;
            } else {
                let lastTokenTime = tokenTimes[tokenTimes.length - 1] || firstTokenTime;
                let tpot = chunkTime - lastTokenTime;
                TPoT.add(tpot);
            }
            tokenTimes.push(chunkTime);
            tokenCount += 1;
            TotalTokens.add(1);
        });

        client.on('error', function (e) {
            console.error('An unexpected error occurred: ', e.error());
            client.close();
        });
    });

    let responseEnd = Date.now();
    let waitingTime = responseEnd - requestStart;
    WaitingTime.add(waitingTime);

    if (waitingTime > 0 && tokenCount > 0) {
        let throughput = (tokenCount * 1000) / waitingTime;
        Throughput.add(throughput);
    }

    check(response, {
        'Status is 200': (r) => r && r.status === 200,
        'Received tokens': () => tokenCount > 0,
    });

    sleep(1);
}
