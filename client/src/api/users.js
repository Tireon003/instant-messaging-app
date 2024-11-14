import axios from "axios";

export async function fetchRecipientStatus(recipientId) {
    let status;
    await axios.get(
        `${window.CONSTS.SERVER_URL}/api/chats/user_network_status?recipient_id=${recipientId}`
    ).then(response => {
        status = response.data.status;
    }).catch(error => {
        if (error.status === 422) {
            console.error("recipientId should be a valid positive integer")
        }
    })
    return status;
}