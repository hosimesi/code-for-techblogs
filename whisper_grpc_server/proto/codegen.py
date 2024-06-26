from grpc.tools import protoc

protoc.main(
    (
        "",
        "-I.",
        "--python_out=./src/",
        "--grpc_python_out=./src/",
        "--mypy_out=./src/",
        "./proto/inference.proto",
    )
)
