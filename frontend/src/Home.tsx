// src/pages/Home.tsx (ou selon ton organisation)

import React from "react";
import Chatbot from "./Chatbot";
import "./chatbot.css";

const Home: React.FC = () => {
  return (
    <div className="home-page" style={styles.container}>
      <h1 style={styles.title}>Bienvenue sur JuridiBot </h1>
      <p style={styles.subtitle}>
        Posez vos questions en cliquant sur l’icône en bas à droite !
      </p>
      <Chatbot />
    </div>
  );
};

export default Home;

const styles = {
  container: {
    padding: "2rem",
    fontFamily: "sans-serif",
    textAlign: "center" as const,
    backgroundColor: "#f8f8f8",
    minHeight: "100vh",
  },
  title: {
    fontSize: "2rem",
    marginBottom: "1rem",
  },
  subtitle: {
    fontSize: "1rem",
    marginBottom: "2rem",
    color: "#666",
  },
};
