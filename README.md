# 🏛️ Law Game - Interactive Legal Learning Platform

An engaging web-based educational game designed to help users learn and practice legal concepts through interactive gameplay modes.

## 🎯 Features

### 📚 Multiple Learning Modes
- **Level-based Learning**: Progress through structured levels, unlocking new content as you master legal concepts
- **You vs Bot**: Challenge AI with random legal scenario questions and get immediate feedback
- **Scenario Chains**: Experience real-world legal situations through multi-step decision-making scenarios

### 🎨 Professional User Experience
- **Responsive Design**: Fully responsive layout that works on desktop, tablet, and mobile devices
- **Modern UI**: Courtroom-themed interface with professional color palette
- **Interactive Navigation**: Breadcrumb navigation, progress indicators, and smooth transitions
- **Accessibility**: ARIA labels, keyboard navigation, and screen reader support

### 🔐 User Management
- User registration and authentication system
- Session-based progress tracking
- Persistent learning progress

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ with Flask 3.0.0
- **Database**: SQLite for lightweight, portable data storage
- **Frontend**: HTML5, CSS3 with modern animations, Vanilla JavaScript
- **Styling**: Professional courtroom-themed design with CSS Grid and Flexbox
- **UX**: Enhanced with micro-interactions, loading states, and toast notifications

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd law_game
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run the Application
```bash
python app.py
```

### 6. Access the Application
Open your web browser and navigate to: `http://127.0.0.1:5000`

## 📁 Project Structure

```
law_game/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── law_game.db          # SQLite database file (auto-generated)
├── templates/            # HTML templates
│   ├── login.html
│   ├── signup.html
│   ├── mode_select.html
│   ├── levels.html
│   ├── play_level.html
│   ├── bot_question_selection.html
│   ├── bot_mode.html
│   ├── bot_results.html
│   ├── scenario_chains.html
│   ├── play_scenario.html
│   └── scenario_outcome.html
└── static/              # Static assets
    ├── style.css         # Main stylesheet
    ├── dialogue_colors.css # Color themes
    ├── ux-enhancements.js # UX utilities and interactions
    └── courtroom.png     # Background image
```

## 🎮 How to Play

### Level-based Learning
1. Select "Level-based Learning" from the main menu
2. Start with Level 1 (unlocked by default)
3. Answer all questions correctly to unlock the next level
4. Progress through increasingly complex legal scenarios

### You vs Bot
1. Choose "You vs Bot" from the main menu
2. Select number of questions for your session
3. Answer questions faster and more accurately than the AI bot
4. Review detailed feedback and explanations

### Scenario Chains
1. Select "Scenario Chains" to explore real-world situations
2. Make decisions at each step of the scenario
3. See immediate consequences and legal explanations
4. Complete the full chain to see the outcome

## 🔧 Configuration

### Database Configuration
The application uses SQLite by default. The database file (`law_game.db`) will be created automatically on first run.

### Security Configuration
- Update the secret key in `app.py` for production deployments
- Implement proper password hashing for production use
- Set up HTTPS and secure cookie handling

## 🧪 Development

### Running Tests
```bash
python test_bot.py
```

### Adding New Questions
1. Access the database directly or use the provided scripts
2. Add questions to the appropriate tables (`questions`, `bot_questions`, `scenario_steps`)
3. Ensure all required fields are populated with valid data

### Customization
- **Colors**: Modify CSS variables in `style.css` under `:root`
- **Themes**: Update `dialogue_colors.css` for different color schemes
- **Content**: Edit HTML templates for layout changes

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚀 Deployment

### Production Considerations
1. **Security**: Update secret key and implement HTTPS
2. **Database**: Consider PostgreSQL/MySQL for larger deployments
3. **Caching**: Implement caching for better performance
4. **Monitoring**: Add logging and error tracking
5. **Backup**: Regular database backups

### Docker Support (Future)
```dockerfile
# Dockerfile coming soon
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use semantic HTML5 markup
- Maintain responsive design principles
- Test across different browsers and devices
- Document new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

- **Issues**: Report bugs via GitHub Issues
- **Features**: Suggest new learning modes or enhancements
- **Security**: Report security vulnerabilities privately

## 🙏 Acknowledgments

- Flask framework for the web backend
- SQLite for lightweight database storage
- Modern CSS for responsive design
- The legal education community for content inspiration

## 📈 Roadmap

- [ ] Multiplayer mode support
- [ ] Leaderboard system
- [ ] Achievement badges
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Content management system for educators
- [ ] Integration with legal research databases
- [ ] Voice narration for accessibility
- [ ] Progress export functionality

---

**Created with ❤️ for legal education enthusiasts**