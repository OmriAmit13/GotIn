# GotIn - בדיקת קבלה לאוניברסיטה

GotIn is a web application that helps prospective students check their admission chances for various universities in Israel. Users can input their psychometric and matriculation scores, select their desired degree program, and receive instant feedback about their admission prospects.

## Features

- Check admission chances for multiple Israeli universities:
  - Hebrew University of Jerusalem
  - Technion
  - Ben-Gurion University
  - Tel Aviv University
- User-friendly interface in Hebrew
- Real-time results
- Cross-platform compatibility

## Prerequisites

- Python 3.x
- Google Chrome Browser
- Bash-compatible shell (Git Bash for Windows users)
- The following Python packages:
  ```
  flask
  flask-cors
  selenium
  webdriver-manager
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd GotIn
   ```

2. Install required Python packages:
   ```bash
   pip install flask flask-cors selenium webdriver-manager
   ```

## Running the Application

### Starting the Application

1. Make the start script executable:
   ```bash
   chmod +x startWebsite.sh
   ```

2. Run the start script:
   ```bash
   ./startWebsite.sh
   ```

This will:
- Start all backend servers
- Open the frontend application in your default browser

### Stopping the Application

1. Make the stop script executable:
   ```bash
   chmod +x stopWebsite.sh
   ```

2. Run the stop script:
   ```bash
   ./stopWebsite.sh
   ```

This will terminate all running backend servers.

## Port Configuration

The application uses a central `config.json` file in the root directory to manage port configurations for all backend services. The default configuration is:

```json
{
  "ports": {
    "hebrew_university": 3002,
    "technion": 3003,
    "bgu": 3001,
    "tel_aviv": 3004
  }
}
```

You can modify these port numbers in the config file to match your environment requirements. Each backend service will automatically use its configured port, falling back to default values if the configuration is unavailable.

## Project Structure

```
.
├── config.json              # Port configuration file
├── Frontend/               # Frontend web interface
|   ├── config.js
│   ├── index.html            # Landing page
│   ├── index.css
│   ├── submissionForm.html   # Main form for data input
│   ├── submissionForm.css
│   ├── results.html          # Results display page
│   └── results.css
│
├── Backend_Hebrew_university/ # Hebrew University backend service
│   ├── app.py               # Flask server
│   └── HebrewUniversity.py  # University-specific logic
│
├── Backend_technion/         # Technion backend service
│   ├── app.py
│   └── technion_scraper.py
│
├── Backend-BGU/              # Ben-Gurion University backend service
│   ├── app.py
│   └── BenGurionUniversity.py
│
├── Backend-TelAvivUniversity/ # Tel Aviv University backend service
│   ├── app.py
│   └── TelAvivUniversity.py
│
├── startWebsite.sh          # Script to start all services
├── stopWebsite.sh           # Script to stop all services

```

## Technologies Used

- **Frontend:**
  - HTML5
  - CSS3
  - JavaScript

- **Backend:**
  - Python 3.x
  - Flask (Web Framework)
  - Flask-CORS (Cross-Origin Resource Sharing)
  - Selenium (Web Scraping)
  - Chrome WebDriver (Browser Automation)

## Cross-Platform Compatibility

The application is designed to work on:
- Linux
- macOS
- Windows (using Git Bash or similar shell)

The start and stop scripts automatically detect your operating system and use the appropriate commands.
