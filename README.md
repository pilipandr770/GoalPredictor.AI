# GoalPredictor.AI ⚽🤖

AI-powered football match predictions for the top 5 European leagues with detailed explanations.

## 🌟 Features

- **Daily AI Analytics**: Intelligent predictions for football matches from Europe's top 5 leagues:
  - 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (England)
  - 🇪🇸 La Liga (Spain)
  - 🇩🇪 Bundesliga (Germany)
  - 🇮🇹 Serie A (Italy)
  - 🇫🇷 Ligue 1 (France)

- **Smart Predictions with Explanations**: Get AI-powered predictions with detailed reasoning, such as:
  - "Both teams scored >2.5 goals in 70% of their last 10 matches"
  - "Home team has won 80% of recent head-to-head encounters"
  - "Combined attacking strength suggests high-scoring match"

- **Multiple Prediction Types**:
  - Over/Under 2.5 goals
  - Both Teams To Score (BTTS)
  - Match Winner (Home/Draw/Away)

- **Flexible Monetization**:
  - **Free Tier**: 3 predictions per day
  - **Premium Subscription**: €5-10/month for unlimited predictions, detailed statistics, and push notifications

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pilipandr770/GoalPredictor.AI.git
cd GoalPredictor.AI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp config/.env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Get Upcoming Matches
```http
GET /api/v1/matches?league=premier_league&days=7
```

Returns upcoming matches for the specified league.

#### Get Predictions
```http
POST /api/v1/predictions
Content-Type: application/json

{
  "match_id": 1,
  "user_id": 1,
  "prediction_types": ["over_2.5", "btts", "match_winner"]
}
```

Returns AI predictions with detailed explanations.

**Example Response:**
```json
{
  "match": {
    "id": 1,
    "league": "premier_league",
    "home_team": "Manchester City",
    "away_team": "Liverpool",
    "match_date": "2024-01-20T15:00:00Z"
  },
  "predictions": [
    {
      "prediction_type": "over_2.5",
      "predicted_outcome": "Yes",
      "confidence": 0.75,
      "explanations": [
        {
          "factor": "Recent Goal-Scoring Form",
          "description": "Manchester City scored over 2.5 goals in 70% of their last 10 matches...",
          "confidence": 0.8
        }
      ]
    }
  ],
  "remaining_daily_predictions": 2
}
```

#### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "footballfan"
}
```

#### Upgrade to Premium
```http
POST /api/v1/subscription/upgrade
Content-Type: application/json

{
  "user_id": 1,
  "duration_months": 1
}
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## 🏗️ Project Structure

```
GoalPredictor.AI/
├── src/
│   ├── models/          # Data models (User, Match, Prediction)
│   │   ├── user.py
│   │   ├── match.py
│   │   └── prediction.py
│   ├── services/        # Business logic
│   │   ├── football_data.py      # Fetch match data
│   │   ├── prediction_engine.py  # AI predictions
│   │   └── user_service.py       # User management
│   └── api/            # API endpoints
│       └── routes.py
├── tests/              # Test suite
├── config/             # Configuration files
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── README.md
```

## 💡 How It Works

### Prediction Engine

The AI prediction engine analyzes multiple factors to generate predictions:

1. **Recent Form Analysis**: Evaluates team performance in the last 10 matches
2. **Head-to-Head Statistics**: Analyzes historical matchups between teams
3. **Attacking/Defensive Strength**: Calculates goal-scoring and conceding averages
4. **Home Advantage**: Factors in home team advantage
5. **League-Specific Patterns**: Considers characteristics of each league

Each prediction comes with:
- **Confidence Score**: 0-100% confidence in the prediction
- **Detailed Explanations**: Human-readable reasoning for each factor
- **Multiple Prediction Types**: Over/Under goals, BTTS, and match winner

### User Quota System

- **Free Users**: 3 predictions per day
- **Premium Users**: Unlimited predictions
- Daily limits reset at midnight UTC
- Premium subscriptions tracked with expiration dates

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Football Data API (optional for production data)
FOOTBALL_API_KEY=your_api_key_here

# Database
DATABASE_URL=sqlite:///./goalpredictor.db

# Free tier daily limit
FREE_TIER_DAILY_LIMIT=3

# Premium subscription price
PREMIUM_MONTHLY_PRICE_EUR=7.99
```

## 🗺️ Roadmap

- [ ] Integration with real football data APIs (football-data.org, API-Football)
- [ ] Enhanced ML models using historical match data
- [ ] User authentication and JWT tokens
- [ ] Push notifications for premium users
- [ ] Mobile app (iOS/Android)
- [ ] Live match tracking and in-play predictions
- [ ] Social features (share predictions, leaderboards)
- [ ] Payment integration (Stripe, PayPal)
- [ ] Multi-language support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Andrii Pylypchuk**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This application provides predictions for entertainment purposes only. Always gamble responsibly and within your means. The predictions are based on statistical analysis and should not be considered as guaranteed outcomes.