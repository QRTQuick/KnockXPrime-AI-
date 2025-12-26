# KnockXPrime AI - CLI Frontend

A beautiful, feature-rich command-line interface for the KnockXPrime AI service with ASCII art, colors, and an intuitive user experience.

## Features

🎨 **Beautiful Interface**
- ASCII art banner with pyfiglet
- Rich colors and styling with Rich library
- Professional panels and tables
- Loading animations and progress indicators

🔐 **Authentication**
- User registration and login
- Session persistence
- API key management
- Secure credential handling

💬 **Interactive Chat**
- Real-time AI conversations
- Conversation history
- Usage tracking during chat
- Typing indicators and animations

📊 **Analytics & Management**
- Usage statistics and monitoring
- Subscription plan information
- Profile management
- Token usage tracking

🚀 **User Experience**
- Intuitive menu navigation
- Error handling with helpful messages
- Keyboard interrupt handling
- Session management

## Installation

### 1. Install Dependencies

```bash
cd KnockXPrime-AI-frontend
pip install -r requirements.txt
```

### 2. Make Executable (Optional)

```bash
chmod +x cli_app.py
```

## Usage

### Basic Usage

```bash
# Run with default server (localhost:8000)
python cli_app.py

# Or if made executable
./cli_app.py
```

### Custom Server

```bash
# Connect to different server
python cli_app.py --server https://your-api-server.com

# Help
python cli_app.py --help
```

## Features Overview

### 🏠 Main Menu (Unauthenticated)
- **Login**: Sign in to your account
- **Register**: Create a new account
- **View Plans**: See subscription options
- **Settings**: Configuration options
- **Exit**: Quit the application

### 🏠 Main Menu (Authenticated)
- **Start Chat**: Interactive AI conversation
- **Usage Stats**: View token usage and limits
- **Profile**: Account information
- **View Plans**: Subscription options
- **Logout**: Sign out
- **Exit**: Quit the application

### 💬 Chat Session
- Type messages to chat with AI
- Commands:
  - `quit`, `exit`, `bye`: End chat session
  - `clear`: Clear conversation history
- Real-time usage tracking
- Token limit warnings

### 📊 Usage Statistics
- Current month token usage
- Remaining tokens
- Usage percentage with color coding
- Request count
- Plan information

### 👤 Profile Management
- View account details
- API key information
- Subscription plan
- Member since date

## Screenshots

### Banner
```
    __ __                 __   _  ______       _
   / //_/____  ____  _____/ /__| |/ / __ \_____(_)___ ___  ___
  / ,<  / __ \/ __ \/ ___/ //_/|   / /_/ / ___/ / __ `__ \/ _ \
 / /| |/ / / / /_/ / /__/ ,<  /   / ____/ /  / / / / / / /  __/
/_/ |_/_/ /_/\____/\___/_/|_|/_/|_/_/   /_/  /_/_/ /_/ /_/\___/

     ___    ____
    /   |  /  _/
   / /| |  / /
  / ___ |_/ /
 /_/  |_/___/

🚀 Welcome to KnockXPrime AI
Your Premium AI Assistant
```

### Menu Interface
```
┌─ 🎯 Main Menu ─────────────────────────────┐
│  1.    💬 Start Chat Session              │
│  2.    📊 View Usage Statistics           │
│  3.    👤 View Profile                    │
│  4.    💳 View Plans                      │
│  5.    🚪 Logout                          │
│  6.    ❌ Exit                            │
└────────────────────────────────────────────┘
```

## Session Management

The CLI automatically saves your session to `~/.knockxprime_session` so you don't need to login every time.

## Error Handling

- **Connection Issues**: Clear error messages with suggestions
- **Authentication Errors**: Helpful login prompts
- **API Errors**: User-friendly error descriptions
- **Token Limits**: Clear warnings and upgrade suggestions

## Customization

### Colors and Styling
The app uses Rich library for styling. You can modify colors in the code:
- `cyan`: Primary accent color
- `green`: Success messages
- `red`: Error messages
- `yellow`: Warnings
- `blue`: AI responses
- `magenta`: Headers

### ASCII Art Fonts
The banner uses pyfiglet fonts. Available fonts:
- `slant`: Main title
- `big`: Subtitle
- You can change fonts in the `display_banner()` method

## Development

### Project Structure
```
KnockXPrime-AI-frontend/
├── cli_app.py          # Main CLI application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Key Classes
- `KnockXPrimeClient`: API client for backend communication
- `KnockXPrimeCLI`: Main CLI interface and user interaction

### Adding Features
1. Add new methods to `KnockXPrimeClient` for API calls
2. Add corresponding UI methods to `KnockXPrimeCLI`
3. Update the menu system in `run()` method

## Troubleshooting

### Common Issues

**"Failed to connect to API"**
- Make sure the backend server is running
- Check the server URL (default: http://localhost:8000)
- Verify network connectivity

**"Authentication failed"**
- Check username and password
- Try registering if you don't have an account
- Clear session: delete `~/.knockxprime_session`

**"Module not found"**
- Install requirements: `pip install -r requirements.txt`
- Use virtual environment if needed

### Debug Mode
Add `--verbose` flag support by modifying the click command for detailed logging.

## License

KnockXPrime AI Proprietary License
- Source code is property of the owner
- Unauthorized commercial use prohibited
- Contact for licensing or collaboration