import { useState, useRef, useEffect, ChangeEvent, KeyboardEvent } from "react";
import "./chatbot.css";

interface Message {
  text: string;
  sender: "user" | "bot";
}

function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isVisible, setIsVisible] = useState(false); // État pour gérer la visibilité
  const chatboxRef = useRef<HTMLDivElement>(null);
  const [isThinking, setIsThinking] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomMessageRef = useRef<HTMLDivElement>(null); // Référence pour le dernier message

  useEffect(() => {
    if (isVisible && messages.length === 0) {
      const timer = setTimeout(() => {
        addMessage(
          "Bonjour ! Vous avez des questions  ?",
          "bot"
        );
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  // Fonction pour ajouter un message
  const addMessage = (message: string, sender: "user" | "bot") => {
    setMessages((prevMessages) => [...prevMessages, { text: message, sender }]);
  };

  // Fonction pour envoyer le message à l'API
  const sendMessage = async () => {
    if (!input.trim() || isThinking) return; // Bloquer si déjà en train de traiter

    setIsThinking(true); // Active le verrou
    const userMessage = input.trim();
    setInput("");
    addMessage(userMessage, "user");
    addMessage("typing-indicator", "bot");

    try {
     const response = await fetch("http://localhost:9000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
      });

       

      if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);

      const data = await response.json();
      setMessages((prev) => [
        ...prev.filter((msg) => msg.text !== "typing-indicator"),
        { text: data.response, sender: "bot" },
      ]);

      // Récupérer l'IP et logger l'interaction
    } catch (error) {
      console.error("Erreur API :", error);
      setMessages((prev) => [
        ...prev.filter((msg) => msg.text !== "typing-indicator"),
        { text: "Désolé, une erreur est survenue.", sender: "bot" },
      ]);
    } finally {
      setIsThinking(false); // Désactive le verrou quoi qu'il arrive
    }
  };

  // Gestion de l'input utilisateur
  const handleInputChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
  };

  // Gestion de l'envoi avec la touche "Enter"
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  // Effect pour scroll automatique vers le bas lorsque le dernier message change
  useEffect(() => {
    // Vérifie si bottomMessageRef est non nul avant de défiler
    if (bottomMessageRef.current) {
      const timeout = setTimeout(() => {
        bottomMessageRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100); // Un petit délai pour garantir que le DOM a été mis à jour
      return () => clearTimeout(timeout); // Nettoyage du timeout
    }
  }, [messages]); // Dépendance sur messages

  // met le curseur de l'utilisateur dans la textarea après la réponse du chat
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];

    if (
      !isThinking &&
      lastMessage &&
      lastMessage.sender === "bot" &&
      lastMessage.text !== "typing-indicator"
    ) {
      const timeout = setTimeout(() => {
        textareaRef.current?.focus();
      }, 100); // Petit délai pour laisser le textarea devenir actif
      return () => clearTimeout(timeout);
    }
  }, [isThinking, messages]);

  return (
    <>
      {/* Bouton pour afficher/masquer le chatbot */}
      <button
        className="chatbot-toggler"
        onClick={() => setIsVisible(!isVisible)}
      >
        <span className="material-symbols-outlined">mode_comment</span>
        <span className="material-symbols-outlined">close</span>
      </button>

      {/* Contenu du chatbot */}
      <div className={`chatbot ${isVisible ? "show-chatbot" : ""}`}>
        <header>
          <h2>JuridiBot</h2>
          <span
            className="material-symbols-outlined"
            onClick={() => setIsVisible(false)}
          >
            close
          </span>
        </header>
        <div className="chatbox" ref={chatboxRef}>
          {messages.map((msg, index) => (
            <div key={index} className={`chat ${msg.sender}`}>
              {msg.sender === "bot" && msg.text === "typing-indicator" ? (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              ) : (
                <>
                  <p>{msg.text}</p>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Écris un message..."
            disabled={isThinking}
          />
          <span
            className={`material-symbols-outlined ${
              isThinking ? "disabled" : ""
            }`}
            onClick={!isThinking ? sendMessage : undefined} // N'appelle sendMessage que si !isThinking
          >
            send
          </span>
        </div>
      </div>
    </>
  );
}

export default Chatbot;
