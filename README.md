# 🚀 AI Developer Challenge: Openfabric Python App

This repository contains an AI-powered application built using Openfabric SDK, Ollama, and Gradio. The app processes user prompts to generate images and 3D models using advanced AI models.

---

## 📋 Features

- **Text-to-Image Generation**: Converts user prompts into stunning images.
- **Image-to-3D Conversion**: Transforms generated images into 3D models.
- **Interactive Gradio Interface**: Provides a user-friendly interface for interacting with the app.
- **Integration with Ollama**: Utilizes the Mistral model for prompt expansion.

---

## 🛠️ Project Structure

```
├── app/
│   ├── core/
│   │   ├── stub.py          # Handles remote connections and API calls
│   │   ├── main.py          # Main execution logic
│   ├── gradio_app.py        # Gradio-based UI for the app
│   ├── start.sh             # Startup script for the app
│   ├── Dockerfile           # Docker configuration
│   └── pyproject.toml       # Poetry configuration
├── README.md                # Project documentation
└── swagger-ui.png           # Screenshot of Swagger UI
```

---

## 🚀 How to Start

### Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/krish341360/ai-test.git
   cd ai-test
   ```
2. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the application:
   ```bash
   sh app/start.sh
   ```

### Run in Docker
1. Build the Docker image:
   ```bash
   docker build -t ai-challenge .
   ```
2. Run the container:
   ```bash
   docker run -p 8888:8888 -p 11434:11434 ai-challenge
   ```

---

## 🌟 Gradio Interface

The application includes an interactive Gradio interface for user-friendly interaction. The interface allows users to input prompts and view generated images and 3D models directly in the browser.

### How to Access
1. Start the application (locally or in Docker).
2. Open your browser and navigate to:
   ```
   http://localhost:7860
   ```
   Replace `7860` with the port specified in your `gradio_app.py` file if different.

### Example Workflow
1. Enter a prompt (e.g., "Glowing dragon on a cliff at sunset").
2. Click "Submit."
3. View the generated image and 3D model in the interface.

---

## 📡 API Endpoints

### **POST /execution**
- **Description**: Processes user prompts and generates images/3D models.
- **Request Body**:
  ```json
  {
    "prompt": "Glowing dragon on a cliff at sunset"
  }
  ```
- **Response**:
  ```json
  {
    "result": "<image_bytes>"
  }
  ```

---

## 🖼️ Swagger UI
Access the Swagger UI at `http://localhost:8888/swagger-ui/#/App/post_execution` to test the API interactively.

![Swagger UI](./swagger-ui.png)

---

## 🧰 Dependencies

- **Python**: 3.8+
- **Openfabric SDK**
- **Ollama**
- **Gradio**
- **Poetry**

---

## 🐛 Troubleshooting

### Common Issues
1. **Port Conflict**:
   - Ensure no other process is using ports `8888` or `11434`.
   - Use `lsof -i :8888` to check and kill conflicting processes.

2. **Docker Container Exiting**:
   - Ensure `ollama serve` is running in the foreground.
   - Check container logs using `docker logs <container_id>`.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📧 Contact

For questions or support, please contact [krish341360@gmail.com](mailto:krish341360@gmail.com).
