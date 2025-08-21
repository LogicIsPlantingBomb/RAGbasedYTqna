# 🎥 YouTube Transcript Q&A Assistant.

An AI-powered web application that allows users to ask questions about any YouTube video by analyzing its transcript content. Built with Streamlit, LangChain, and Google's Gemini AI.
<img width="1914" height="903" alt="Screenshot_2025-08-19_02-25-43" src="https://github.com/user-attachments/assets/a80afa12-0030-43bc-84f4-df1cbcc2f39d" />


## ✨ Features

- **🎯 Smart Q&A**: Ask specific questions about YouTube video content
- **🌐 Multi-language Support**: Supports 10+ languages for subtitles
- **🔗 Flexible Input**: Accept full YouTube URLs or just video IDs
- **🎨 Modern UI**: Dark theme with smooth animations and loading indicators
- **⚡ Fast Processing**: Efficient vector search using FAISS
- **🤖 AI-Powered**: Uses Google's Gemini 1.5 Flash model for intelligent responses


## 📋 Prerequisites

- Python 3.8 or higher
- Google API Key (for Gemini AI)
- Internet connection for YouTube transcript fetching

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/youtube-qa-assistant.git
   cd youtube-qa-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   
   **Get your Google API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your `.env` file

5. **Run the application**
   ```bash
   streamlit run new.py
   ```

6. **Open your browser**
   
   Navigate to `http://localhost:8501`

## 🎯 Usage

### Step 1: Enter Video Information
- **Video URL/ID**: Paste any YouTube URL or just the video ID
  - ✅ `https://youtube.com/watch?v=VIDEO_ID`
  - ✅ `https://youtu.be/VIDEO_ID`
  - ✅ `VIDEO_ID` (11 characters)
- **Language**: Select subtitle language (defaults to English)

### Step 2: Ask Your Question
- Be specific about what you want to know
- Examples:
  - "What are the main points discussed in this video?"
  - "How does the speaker explain quantum computing?"
  - "What solutions are proposed for climate change?"

### Step 3: Get AI-Powered Answers
- The app will process the video transcript
- AI analyzes the content and provides relevant answers
- Processing typically takes 10-30 seconds

## 🌍 Supported Languages

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | en | Portuguese | pt |
| Spanish | es | Russian | ru |
| French | fr | Japanese | ja |
| German | de | Korean | ko |
| Italian | it | Chinese | zh |
| Hindi | hi |

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│  YouTube API     │───▶│  Text Splitter  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Answer   │◀───│   Gemini AI      │◀───│   FAISS Vector  │
└─────────────────┘    └──────────────────┘    │     Store       │
                                                └─────────────────┘
```

## 📁 Project Structure

```
youtube-qa-assistant/
│
├── new.py                 # Main application file
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── README.md            # Project documentation
└── .gitignore           # Git ignore file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Your Google AI API key | ✅ Yes |

### Model Settings

- **Embedding Model**: `models/embedding-001`
- **LLM Model**: `gemini-1.5-flash`
- **Temperature**: 0.0 (deterministic responses)
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters

## 🔧 Troubleshooting

### Common Issues

**1. "No subtitles available"**
- The video doesn't have captions enabled
- Try a different video with subtitles

**2. "Invalid YouTube URL"**
- Check the URL format
- Ensure the video is public and accessible

**3. "API Key Error"**
- Verify your Google API key is correct
- Check if the API key has proper permissions

**4. "Module not found"**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate your virtual environment

### Performance Tips

- **Video Length**: Shorter videos process faster
- **Internet Speed**: Faster connection = quicker transcript fetching
- **Question Specificity**: More specific questions get better answers

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Web app framework
- [LangChain](https://langchain.com/) - LLM application framework
- [Google AI](https://ai.google/) - Gemini AI models
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) - Transcript fetching

## 📞 Support

If you have any questions or run into issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Review the documentation

---

⭐ **If you found this project helpful, please give it a star!**
