# Video Chat Assistant - Deployment Guide

## 🎯 Quick Start for New Computer

### Prerequisites
- Windows 10/11
- Internet connection
- At least 2GB free disk space

### 🚀 **Option 1: Automatic Setup (Recommended)**

1. **Copy the entire project folder** to the new computer
2. **Double-click `setup.bat`** and wait for installation to complete
3. **Double-click `run_app.bat`** to start the application
4. **Open browser** and go to `http://localhost:8501`

### 🛠️ **Option 2: Manual Setup**

#### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://python.org)
2. ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart computer after installation

#### Step 2: Setup Project
1. Copy project folder to desired location
2. Open Command Prompt in project folder
3. Run these commands:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 3: Run Application
```cmd
.venv\Scripts\python.exe -m streamlit run video_chat_lite.py
```

## 📁 **Project Structure**
```
project-taha/
├── video_chat_lite.py      # Main application
├── requirements.txt        # Python dependencies
├── setup.bat              # Automatic setup script
├── run_app.bat            # Run application script
├── transcriptions/        # Video transcript files (35 files)
├── faiss_index/          # Search index files
└── README.md             # This file
```

## 🌐 **Accessing from Other Devices**

Once running, the app is available at:
- **Same computer**: `http://localhost:8501`
- **Other devices**: `http://[COMPUTER_IP]:8501`

To find your computer's IP:
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network connection.

## 🎯 **Application Features**

### 🎥 **Video Chat Assistant**
- Educational video about plant immunity
- Smart search through video transcriptions
- Arabic and English language support
- Web search fallback functionality

### 💬 **Chat Interface**
- Ask questions in Arabic or English
- Get answers from video content
- Real-time search results
- Source attribution

### 🔍 **Search Capabilities**
- Text-based search through 35 transcript files
- FAISS-powered efficient searching
- Web search using DuckDuckGo
- Smart keyword matching

## 🔧 **Troubleshooting**

### Python Not Found
- Reinstall Python with "Add to PATH" option
- Restart computer
- Try `python3` instead of `python`

### Dependencies Installation Failed
- Check internet connection
- Run as Administrator: `pip install -r requirements.txt`
- Try: `pip install --user -r requirements.txt`

### Port Already in Use
- Change port in run_app.bat: `--server.port=8502`
- Or stop other applications using port 8501

### Firewall Issues
Run as Administrator:
```cmd
netsh advfirewall firewall add rule name="Streamlit" dir=in action=allow protocol=TCP localport=8501
```

## 📊 **System Requirements**

### Minimum:
- Windows 10
- Python 3.8+
- 2GB RAM
- 1GB free disk space
- Internet connection

### Recommended:
- Windows 11
- Python 3.10+
- 4GB RAM
- 2GB free disk space
- Stable internet connection

## 🔒 **Security Notes**

- The app runs on your local network
- No data is sent to external servers (except web search)
- All video transcriptions are stored locally
- Safe for educational and research use

## 💡 **Usage Tips**

1. **Best Questions**: Ask specific questions about plant immunity
2. **Language**: Works in both Arabic and English
3. **Search**: Try different keywords if no results found
4. **Performance**: Close unused applications for better performance

## 📞 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all files are copied correctly
3. Verify Python installation
4. Try running as Administrator

---
*Video Chat Assistant - Educational AI Tool for Plant Immunity Research*