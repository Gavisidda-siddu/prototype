document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chat-messages');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');
  
  // Auto-resize textarea as user types
  userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    
    // Enable/disable send button based on input content
    sendButton.disabled = !userInput.value.trim();
  });
  
  // Handle enter key to send message (but allow shift+enter for new line)
  userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (!sendButton.disabled) {
        sendMessage();
      }
    }
  });
  
  // Send button click handler
  sendButton.addEventListener('click', sendMessage);
  
  // Function to send message to Ollama API
  async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    sendButton.disabled = true;
    
    // Add loading indicator
    const loadingEl = document.createElement('div');
    loadingEl.className = 'message assistant';
    loadingEl.innerHTML = `
      <div class="loader">
        <div></div>
        <div></div>
        <div></div>
      </div>
    `;
    chatMessages.appendChild(loadingEl);
    scrollToBottom();
    
    try {
      // Call the Ollama API
      const response = await callOllama(message);
      
      // Remove loading indicator
      chatMessages.removeChild(loadingEl);
      
      // Add assistant response
      addMessage(response, 'assistant');
    } catch (error) {
      // Remove loading indicator
      chatMessages.removeChild(loadingEl);
      
      // Show error message
      addMessage(
        "I'm having trouble connecting to the healthcare model. Please check that Ollama is running locally with the healthcare model installed.", 
        'assistant'
      );
      console.error('Error:', error);
    }
  }
  
  // Function to call Ollama API
  async function callOllama(prompt) {
    try {
      const response = await fetch('http://localhost:11434/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'skos41/llama-healthcare-llm',
          messages: [
            {
              role: 'user',
              content: prompt,
            },
          ],
          stream: true,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message?.content || "I couldn't process your question. Please try again.";
    } catch (error) {
      console.error('Error querying Ollama:', error);
      throw error;
    }
  }
  
  // Function to add a message to the chat
  function addMessage(content, role) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${role}`;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageEl.innerHTML = `
      <div class="message-content">${formatMessage(content)}</div>
      <time>${timeStr}</time>
    `;
    
    chatMessages.appendChild(messageEl);
    scrollToBottom();
  }
  
  // Function to format message content (add line breaks, links, etc.)
  function formatMessage(text) {
    return text
      .replace(/\n/g, '<br>')
      .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  }
  
  // Function to scroll chat to bottom
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});