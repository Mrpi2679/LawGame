# Git Repository Setup Script

echo "Initializing Git repository for Law Game..."
echo

# Initialize git repository
git init

# Add all files to git
git add .

# Initial commit
git commit -m "Initial commit: Complete Law Game application

Features:
- Level-based learning mode with progressive unlocking
- You vs Bot challenge mode with AI competition
- Scenario chains for real-world legal situations
- Professional UI with courtroom theme
- Enhanced UX with breadcrumbs, progress indicators, animations
- Responsive design for all devices
- User authentication and session management
- SQLite database with comprehensive schema
- Modern CSS with micro-interactions
- Accessibility features and keyboard navigation

Technical:
- Flask 3.0.0 backend
- HTML5/CSS3/JavaScript frontend
- Responsive grid/flexbox layouts
- Professional animations and transitions
- Form validation and loading states
- Error handling and user feedback"

echo
echo "Git repository initialized successfully!"
echo
echo "Next steps:"
echo "1. Create a GitHub repository at https://github.com/new"
echo "2. Add remote: git remote add origin <your-repository-url>"
echo "3. Push to GitHub: git push -u origin main"
echo
echo "Repository is ready for deployment!"