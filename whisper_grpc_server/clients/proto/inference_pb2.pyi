"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""

import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message
import typing

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class TranscribeRequest(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    AUDIO_BYTES_FIELD_NUMBER: builtins.int
    TARGET_FIELD_NUMBER: builtins.int
    audio_bytes: builtins.bytes
    target: builtins.str
    def __init__(
        self,
        *,
        audio_bytes: builtins.bytes = ...,
        target: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["audio_bytes", b"audio_bytes", "target", b"target"]) -> None: ...

global___TranscribeRequest = TranscribeRequest

@typing.final
class ASRResult(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    TRANSCRIPTION_FIELD_NUMBER: builtins.int
    transcription: builtins.str
    def __init__(
        self,
        *,
        transcription: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["transcription", b"transcription"]) -> None: ...

global___ASRResult = ASRResult

@typing.final
class TranscribeResponse(google.protobuf.message.Message):
    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class ResultEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        @property
        def value(self) -> global___ASRResult: ...
        def __init__(
            self,
            *,
            key: builtins.str = ...,
            value: global___ASRResult | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["value", b"value"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["key", b"key", "value", b"value"]) -> None: ...

    RESULT_FIELD_NUMBER: builtins.int
    @property
    def result(self) -> google.protobuf.internal.containers.MessageMap[builtins.str, global___ASRResult]: ...
    def __init__(
        self,
        *,
        result: collections.abc.Mapping[builtins.str, global___ASRResult] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["result", b"result"]) -> None: ...

global___TranscribeResponse = TranscribeResponse
