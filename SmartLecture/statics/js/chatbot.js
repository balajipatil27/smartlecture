// chatbot.js
document.addEventListener('DOMContentLoaded', function() {
  const chatbotBtn = document.getElementById('chatbotBtn');
  const chatbotBox = document.getElementById('chatbotBox');
  const sendBtn = document.getElementById('sendBtn');
  const chatbotMessages = document.getElementById('chatbotMessages');
  const inputField = document.getElementById('userMessage');

  // Toggle chatbot visibility
  chatbotBtn.addEventListener('click', () => {
    if (chatbotBox.style.display === 'flex') {
      chatbotBox.style.display = 'none';
    } else {
      chatbotBox.style.display = 'flex';
    }
  });

  // Handle sending a message
  sendBtn.addEventListener('click', sendMessage);

  async function sendMessage() {
    const message = inputField.value.trim();
    if (!message) return;

    appendMessage('You', message);
    inputField.value = '';

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_message: message })
      });
      const data = await response.json();
      appendMessage('SmartLecture Bot', data.reply);
    } catch (error) {
      appendMessage('SmartLecture Bot', "⚠️ Sorry, something went wrong.");
    }
  }

  function appendMessage(sender, text) {
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
    messageElement.classList.add('mb-2');
    chatbotMessages.appendChild(messageElement);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }
});
