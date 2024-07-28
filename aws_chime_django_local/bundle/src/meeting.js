import * as ChimeSDK from 'amazon-chime-sdk-js';

window.addEventListener('DOMContentLoaded', async () => {
    // wait for the meeting and attendee to be set
    while (!window.meeting || !window.attendee) {
        await new Promise(resolve => setTimeout(resolve, 100));
    }

    const meeting = window.meeting;
    const attendee = window.attendee;

    const logger = new ChimeSDK.ConsoleLogger('ChimeMeetingLogs', ChimeSDK.LogLevel.INFO);
    const deviceController = new ChimeSDK.DefaultDeviceController(logger);
    const configuration = new ChimeSDK.MeetingSessionConfiguration(meeting, attendee);
    const meetingSession = new ChimeSDK.DefaultMeetingSession(configuration, logger, deviceController);


    meetingSession.audioVideo.setDeviceLabelTrigger(() => Promise.resolve(new MediaStream()));
    meetingSession.audioVideo.start();

    // Invoke devices
    meetingSession.audioVideo.setDeviceLabelTrigger(async () =>
        await navigator.mediaDevices.getUserMedia({ audio: true, video: true })
    );
    const audioInputDevices = await meetingSession.audioVideo.listAudioInputDevices();
    const audioOutputDevices = await meetingSession.audioVideo.listAudioOutputDevices();
    const videoInputDevices = await meetingSession.audioVideo.listVideoInputDevices();
    await meetingSession.audioVideo.startAudioInput(audioInputDevices[0].deviceId);
    await meetingSession.audioVideo.chooseAudioOutput(audioOutputDevices[0].deviceId);
    await meetingSession.audioVideo.startVideoInput(videoInputDevices[0].deviceId);



    const audioElement = document.getElementById('audio-view');
    const videoElement = document.getElementById('video-view');
    const videoElementTile = document.getElementById('video-view-div');
    meetingSession.audioVideo.bindAudioElement(audioElement);

    const observer = {
        videoTileDidUpdate: tileState => {

            if (tileState.localTile){
                meetingSession.audioVideo.bindVideoElement(tileState.tileId, videoElement);
            }else{
                if(!document.getElementById(tileState.tileId)){
                    const node = document.createElement("video");
                    node.id = tileState.tileId;
                    videoElementTile.appendChild(node);
                }
                const videoElementNew = document.getElementById(tileState.tileId);
                meetingSession.audioVideo.bindVideoElement(tileState.tileId, videoElementNew);
            }
        },
        videoTileWasRemoved: tileId => {
            if(document.getElementById(tileId)){
                const videoElementRemoved = document.getElementById(tileId);
                videoElementRemoved.remove();
            }
        }
    };

    meetingSession.audioVideo.addObserver(observer);
    meetingSession.audioVideo.startLocalVideoTile();
    meetingSession.audioVideo.start();
});
