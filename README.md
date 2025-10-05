# 🖼️ AI Art Diagnostics Agent

***

## 🌟 Project Description

The **AI Art Diagnostics Agent** is a powerful multimodal AI assistant designed to perform **in-depth visual analysis** and **artistic criticism** on user-uploaded artwork.

This project utilizes **Streamlit** for an interactive user interface and the **LangGraph** (ReAct Agent) framework, powered by the **Google Gemini 2.5 Flash** model, for advanced image and text processing capabilities.

The agent's primary goal is to provide expert insights into the **style, historical period, technique, and potential authentication** of an artwork.

***

## ✨ Key Features

* **Multimodal Analysis:** Capable of processing and analyzing both images (**PNG, JPG, JPEG**) and textual queries simultaneously.
* **Authoritative Art Criticism:** Provides detailed analysis covering **technique, style, period, and potential artists**.
* **ReAct Agent Framework:** Utilizes **LangGraph** for structured reasoning and execution flow.
* **Interactive UI:** Built with Streamlit, featuring chat history, file uploading, and dynamic suggestion chips.
* **Bilingual Response:** The agent is configured to respond in the same language as the user's last message (Indonesian or English).

***

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Core AI Model** | `gemini-2.5-flash` | Google AI's multimodal model for image and text analysis. |
| **Agent Framework** | `LangGraph` (ReAct) | For complex and structured agent workflow. |
| **User Interface (UI)** | `Streamlit` | Used to create a fast, interactive web application. |
| **Programming Language** | `Python` | The main development language. |

***

## 🚀 Installation and Local Setup

Follow these steps to run the project on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/arifinddc/chatbot-art-diagnostics-agent
    cd chatbot-art-diagnostics-agent
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup API Key:** Create a folder named `.streamlit` in the project root and add a file named `secrets.toml` inside it:
    ```toml
    # .streamlit/secrets.toml
    google_api_key="YOUR_GEMINI_API_KEY_HERE"
    ```
4.  **Run the Application:**
    ```bash
    streamlit run art_diagnostics_agent.py
    ```
