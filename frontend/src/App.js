import { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([
    { text: 'Здравствуйте! Чем я могу вам помочь?', sender: 'bot' },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isFaqVisible, setIsFaqVisible] = useState(false);
  const [activeFaqIndex, setActiveFaqIndex] = useState(null);
  const messagesEndRef = useRef(null);

  const [faqData, setFaqData] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    const initializeChat = async () => {
      try {
        const sessionResponse = await fetch(`${API_BASE_URL}/addChat`, {
          method: 'POST',
        });
        if (!sessionResponse.ok) throw new Error('Ошибка создания сессии');
        const sessionData = await sessionResponse.json();
        setSessionId(sessionData.id);

        const faqResponse = await fetch(`${API_BASE_URL}/getFAQ`);
        if (!faqResponse.ok) throw new Error('Ошибка загрузки FAQ');
        const faqItems = await faqResponse.json();
        setFaqData(faqItems);

      } catch (error) {
        console.error("Ошибка инициализации:", error);
        setMessages(prev => [...prev, { text: 'Не удалось подключиться к серверу. Попробуйте обновить страницу.', sender: 'bot' }]);
      }
    };

    initializeChat();
  }, []); 

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || !sessionId) return;

    const userMessage = { text: inputValue, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    const currentInput = inputValue; 
    setInputValue('');

    try {
      const response = await fetch(`${API_BASE_URL}/sendQuery`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: currentInput,
          sessionId: sessionId
        }),
      });

      if (!response.ok) throw new Error('Ошибка ответа сервера');

      const data = await response.json();

      setMessages((prevMessages) => [
        ...prevMessages,
        { text: data.answer, sender: 'bot' },
      ]);

    } catch (error) {
      console.error("Ошибка отправки сообщения:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: 'Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте еще раз.', sender: 'bot' },
      ]);
    }
  };

  const handleFaqClick = () => {
    setIsFaqVisible(!isFaqVisible);
    setActiveFaqIndex(null);
  };

  const handleFaqItemClick = (index) => {
    setActiveFaqIndex(activeFaqIndex === index ? null : index);
  };

  return (
    <div className="App">
      <div className="chat-content-wrapper">
        <header className="chatbot-header">
          <h1>Умный помощник</h1>
        </header>

        <main className="chatbot-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message-wrapper ${message.sender}`}>
              <div className="message">{message.text}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </main>

        <footer className="chatbot-footer">
          {isFaqVisible && (
            <div className="faq-section">
              {faqData.map((item, index) => (
                <div
                  key={item.id}
                  className={`faq-item ${activeFaqIndex === index ? 'active' : ''}`}
                  onClick={() => handleFaqItemClick(index)}
                >
                  <div className="faq-question">
                    {item.question}
                    <span>{activeFaqIndex === index ? '−' : '+'}</span>
                  </div>
                  <div className="faq-answer">{item.answer}</div>
                </div>
              ))}
            </div>
          )}
          <div className="faq-button-container">
            <button onClick={handleFaqClick} disabled={!faqData.length}>
              {isFaqVisible ? 'Скрыть ЧаВо' : 'Просмотреть ЧаВо'}
            </button>
          </div>
          <div className="chatbot-input-area">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder={sessionId ? "Спросите что-нибудь..." : "Загрузка сессии..."} 
              disabled={!sessionId} 
            />
            <button onClick={handleSendMessage} disabled={!sessionId}>➤</button>
          </div>
          <div className="disclaimer">
            Ответы генерируются ИИ и могут содержать неточности.
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;