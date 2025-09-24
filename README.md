# CITTAA Vocalysis – Demo API and Vercel Frontend

This repository contains the Python analysis engine and a lightweight API for deployment.

Quick start (local API):
- python3 -m venv .venv && source .venv/bin/activate
- pip install -r api/requirements.txt
- uvicorn api.main:app --host 0.0.0.0 --port 8080
- Test: curl -F "audio=@/path/to/file.wav" -F region=south_india -F language=english -F age_group=adult -F gender=male http://localhost:8080/analyze

Deploy (Cloud Run):
- Build: docker build -t gcr.io/PROJECT_ID/vocalysis-api:demo -f api/Dockerfile .
- Push: gcloud run deploy vocalysis-api --image gcr.io/PROJECT_ID/vocalysis-api:demo --platform managed --allow-unauthenticated --region us-central1

Frontend (Vercel):
- A Next.js frontend can call POST {BACKEND_URL}/analyze with form-data fields: audio, region, language, age_group, gender.
- The response contains scores, cultural_context, recommendations, and pdf_report_b64 (base64 PDF). Decode on client for download.


# Cittaa Health Services Private Limited

Welcome to the official GitHub account of Cittaa Health Services Private Limited. We are a leading provider of innovative mental health solutions, dedicated to promoting mental well-being and making mental health care more accessible to all.

## 🌟 Flagship Product: Vocalysis

Vocalysis is our cutting-edge, AI-powered mental health assessment bot that provides personalized insights and support to users. With Vocalysis, you can gain a deeper understanding of your mental well-being and receive tailored recommendations to help you thrive.

### Key Features

- 🎙️ Voice Analysis: Vocalysis uses advanced machine learning algorithms to analyze your voice patterns and detect potential mental health concerns.
- 🧠 Personalized Insights: Receive detailed insights into your mental well-being based on your unique voice analysis results.
- 📊 Tracking and Monitoring: Track your mental health progress over time and identify trends and patterns in your well-being.
- 🤖 Intelligent Chatbot: Engage in natural conversations with Vocalysis and receive empathetic and supportive responses.
- 🔒 Privacy and Security: Your data is encrypted and handled with the utmost confidentiality, ensuring your privacy is protected.

### Getting Started

To start using Vocalysis, simply visit our website at [cittaa.in](https://www.cittaa.in) and sign up for an account. Once you've completed the registration process, you can begin interacting with Vocalysis and exploring its features.

## Live Demo

A live demo of the Vocalysis system is available at: [https://vocalysis-demo.streamlit.app](https://vocalysis-demo.streamlit.app)

For investor testing, you can use the following demo links:
- [Normal Mental Health State](https://vocalysis-demo.streamlit.app/?demo=normal)
- [Anxiety Indicators](https://vocalysis-demo.streamlit.app/?demo=anxiety)
- [Depression Indicators](https://vocalysis-demo.streamlit.app/?demo=depression)
- [Stress Indicators](https://vocalysis-demo.streamlit.app/?demo=stress)

### Contributing

We welcome contributions from the open-source community to help us improve Vocalysis and make mental health care more accessible. If you're interested in contributing, please check out our [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started.

## 🌍 Our Mission

At Cittaa, our mission is to revolutionize mental health care by leveraging cutting-edge technology and compassionate support. We believe that everyone deserves access to high-quality mental health resources, and we're committed to making that a reality.

## 📬 Get in Touch

We'd love to hear from you! If you have any questions, feedback, or partnership inquiries, please don't hesitate to reach out to us:

- 📧 Email: support@cittaa.in
- 🐦 Twitter: [@cittaa](https://x.com/cittaa9)
- 💼 LinkedIn: [Cittaa Health Services Private Limited](https://www.linkedin.com/company/cittaa-the-powerofmind)

Thank you for your interest in Cittaa and Vocalysis. Together, let's create a world where mental health is prioritized and supported. 💙
