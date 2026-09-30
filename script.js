function sendMessage() {

    let message = document.getElementById("message").value;

    if (message === "") {
        alert("Please type a message");
        return;
    }

    let chatBox = document.getElementById("chat-box");

    let newMessage = document.createElement("p");

    newMessage.innerText = "You: " + message;

    chatBox.appendChild(newMessage);

    document.getElementById("message").value = "";
}