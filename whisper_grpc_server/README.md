# Overview
gRPC ASR inference server in local.\
blog link: https://zenn.dev/hosimesi/articles/23132daca3e9ff

# Pre-requirements
1. Install Python and poetry.
    ```bash
    $ pip list | grep poetry
    poetry                      1.7.1
    poetry-core                 1.8.1
    poetry-plugin-export        1.6.0
    ```

2. Download models from Hugging Face
   - [faster-whisper-large-v2](https://huggingface.co/Systran/faster-whisper-large-v2)
   - [faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3)
   - [faster-distil-whisper-large-v2](https://huggingface.co/Systran/faster-distil-whisper-large-v2)
   - [faster-distil-whisper-large-v3](https://huggingface.co/Systran/faster-distil-whisper-large-v3)

3. Prepareing audio files and set to samples/.

# How to use in local
1. Change directory.
    ```bash
    cd path/to/whisper_grpc_server
    ```
2. Run up.
    ```bash
    $ docker compose up --build
    ```
3. Request.
    ```bash
    $ rye run python clients/request.py
    ```
