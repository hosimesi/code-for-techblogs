async function fetchUsers() {
    const response = await fetch('/api/users/');
    let users = await response.json();
    // sort users by name
    users = users.sort((a, b) => a.name.localeCompare(b.name));
    const createdBySelect = document.getElementById('createdBy');
    const participantsDiv = document.getElementById('participants');
    users.forEach(user => {
        const createdByOption = document.createElement('option');
        createdByOption.value = user.user_id;
        createdByOption.text = user.name;
        createdBySelect.appendChild(createdByOption);
        const participantCheckbox = document.createElement('input');
        participantCheckbox.type = 'checkbox';
        participantCheckbox.id = `participant${user.user_id}`;
        participantCheckbox.value = user.user_id;
        const participantLabel = document.createElement('label');
        participantLabel.htmlFor = participantCheckbox.id;
        participantLabel.appendChild(document.createTextNode(user.name));
        participantsDiv.appendChild(participantCheckbox);
        participantsDiv.appendChild(participantLabel);
        participantsDiv.appendChild(document.createElement('br'));
    });
}

document.getElementById('createMeetingForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const meetingName = document.getElementById('meetingName').value;
    const createdBy = document.getElementById('createdBy').value;
    const participants = Array.from(document.getElementById('participants').getElementsByTagName('input'))
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);
    const meetingData = JSON.stringify({
        title: meetingName,
        created_by: createdBy,
        participants: participants
    });
    await fetch('/api/meetings/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: meetingData,
    });
});


async function joinMeeting(meetingId, userId) {
    const meetingUrl = new URL('/meeting/', window.location.href);
    meetingUrl.searchParams.set('meetingId', meetingId);
    meetingUrl.searchParams.set('userId', userId);
    window.open(meetingUrl.toString(), '_blank');
}

async function deleteMeeting(meetingId) {
    await fetch(`/api/meetings/${meetingId}/delete/`, {
        method: 'DELETE',
    });
}

function fetchMeetingsAndUpdateList() {
    fetch('/api/meetings/')
        .then(response => response.json())
        .then(meetings => {
            const table = document.querySelector('#meetingTable table');
            // Remove all rows except the header row
            while (table.rows.length > 1) {
                table.deleteRow(1);
            }
            // Add a new row for each meeting
            for (const meeting of meetings) {
                const row = table.insertRow(-1);
                row.insertCell(0).innerText = meeting.meeting_id;
                row.insertCell(1).innerText = meeting.title;
                row.insertCell(2).innerText = meeting.created_by_name;
                row.insertCell(3).innerText = meeting.created_at;
                const selectCell = row.insertCell(4);
                // Add a select element for the attendees
                const select = document.createElement('select');
                for (const attendee of meeting.attendees) {
                    const option = document.createElement('option');
                    option.value = attendee.user_id;
                    option.text = attendee.name;
                    select.appendChild(option);
                }
                selectCell.appendChild(select);

                // Join Action
                const joinCell = row.insertCell(5);
                const joinButton = document.createElement('button');
                joinButton.innerText = 'Join';
                joinButton.addEventListener('click', () => {
                    const selectedOption = select.options[select.selectedIndex];
                    joinMeeting(meeting.meeting_id, selectedOption.value);
                });
                joinCell.appendChild(joinButton);
                // Deelete Action
                const deleteCell = row.insertCell(6);
                const deleteButton = document.createElement('button');
                deleteButton.innerText = 'Delete';
                deleteButton.addEventListener('click', () => {
                    deleteMeeting(meeting.meeting_id);
                });
                deleteCell.appendChild(deleteButton);
            }
        }
    );
}

setInterval(fetchMeetingsAndUpdateList, 5000);
fetchMeetingsAndUpdateList();
fetchUsers();


