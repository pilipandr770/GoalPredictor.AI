# Tennis Integration - Deployment Guide

## ✅ Completed

### Backend
- ✅ ML Model trained (ROC-AUC: 0.705, Accuracy: 64.8%)
- ✅ Database models added (TennisPlayer, TennisMatch, TennisPrediction)
- ✅ API service created (services/tennis_api.py) with RapidAPI integration + demo fallback
- ✅ Prediction service created (tennis/predict.py) with feature extraction
- ✅ API routes created (api/routes_tennis.py):
  - `GET /api/tennis/matches?days=7` - Get upcoming matches
  - `GET /api/tennis/predictions/<match_id>` - Get prediction (Premium only)
  - `GET /api/tennis/health` - Health check
- ✅ Blueprint registered in app.py

### Frontend
- ✅ Tennis template created (templates/tennis.html) with German localization
- ✅ Navigation updated (base.html) - added "🎾 Tennis" link
- ✅ Footer updated with Tennis link
- ✅ Route added in app.py (`/tennis`)

## 📋 Deployment Steps

### 1. Environment Variables

Add to `.env` (optional - works with demo mode without key):
```env
# Tennis API ATP-WTA-ITF by MatchStat (RapidAPI - 100 requests/month free)
RAPIDAPI_TENNIS_KEY=your_key_here
```

Get free API key:
1. Visit https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf
2. Sign up and subscribe to Free tier (100 requests/month)
3. Copy API key and add to `.env`

**Provider**: [MatchStat](https://matchstat.com/) - Professional tennis data API
**Documentation**: https://matchstat.com/predictions-tips/the-best-tennis-data-api-for-stats/
**Contact**: tennisapi@matchstat.com

**Note**: Demo mode works without API key, showing 5 realistic demo matches.

### 2. Database Migration

#### Local Development (SQLite)
```bash
# Set local database URL
export DATABASE_URL=sqlite:///goalpredictor.db

# Create migration
flask db migrate -m "Add tennis models"

# Apply migration
flask db upgrade
```

#### Production (PostgreSQL on Render)
Database migration will be automatically applied when you deploy to Render.

Manual migration (if needed):
```bash
# Connect to Render PostgreSQL
# (DATABASE_URL is already set on Render)
flask db migrate -m "Add tennis models"
flask db upgrade
```

### 3. Testing Locally

```bash
# Start Flask app
python app.py

# Test endpoints
curl http://localhost:5000/api/tennis/health
curl http://localhost:5000/api/tennis/matches?days=7
curl http://localhost:5000/api/tennis/predictions/demo_1  # Need to be logged in as Premium user

# Visit pages
http://localhost:5000/tennis
http://localhost:5000/predictions
```

### 4. Deploy to Render

```bash
# Commit changes
git add .
git commit -m "feat(tennis): Complete tennis integration with UI"

# Push to production
git push origin master:main
```

Render will automatically:
- Build the app
- Apply database migrations
- Restart the service

### 5. Post-Deployment Testing

Visit your production URL:
- `https://your-app.onrender.com/tennis` - Tennis page
- `https://your-app.onrender.com/api/tennis/matches` - API endpoint
- `https://your-app.onrender.com/api/tennis/health` - Health check

Test as Premium user:
1. Login with Premium account
2. Visit `/tennis`
3. Click on any match
4. Verify prediction displays correctly

## 🎯 Features

### User Experience
- **Public**: Can view upcoming match schedule (7 days)
- **Premium**: Can generate predictions with confidence scores
- **German UI**: All text in German (`Prognosen`, `Siegchance`, etc.)
- **Filters**: Surface (Hard/Clay/Grass), Tournament, Date range

### API Response Example

`GET /api/tennis/matches`:
```json
{
  "success": true,
  "matches": [
    {
      "id": "demo_1",
      "tournament": "ATP Masters 1000 Miami",
      "round": "Viertelfinale",
      "surface": "Hard",
      "date": "2024-03-28T19:00:00",
      "player1": {
        "name": "Novak Djokovic",
        "rank": 1,
        "country": "🇷🇸"
      },
      "player2": {
        "name": "Carlos Alcaraz",
        "rank": 2,
        "country": "🇪🇸"
      }
    }
  ]
}
```

`GET /api/tennis/predictions/demo_1` (Premium only):
```json
{
  "success": true,
  "prediction": {
    "player1_win_probability": 0.584,
    "player2_win_probability": 0.416,
    "predicted_winner": "Novak Djokovic",
    "confidence": "medium",
    "explanation": "Novak Djokovic hat eine 58.4% Wahrscheinlichkeit zu gewinnen...",
    "factors": [
      {
        "factor": "Weltranglistenunterschied",
        "impact": "high",
        "description": "Djokovic ist auf Platz 1 (Alcaraz: 2)"
      }
    ]
  }
}
```

## 🔧 Troubleshooting

### Database Migration Fails
If using production DB URL locally, it won't connect. Use local SQLite:
```bash
export DATABASE_URL=sqlite:///goalpredictor.db
flask db migrate -m "Add tennis models"
flask db upgrade
```

### Demo Mode Not Working
Demo mode should always work even without API key. Check:
- `services/tennis_api.py` has `_get_demo_data()` method
- Demo data includes 5 matches with realistic players
- API endpoint returns `demo_1` to `demo_5` IDs

### Prediction Generation Fails
Check:
1. Model files exist in `tennis/models/`:
   - `tennis_player1_win_model.pkl`
   - `tennis_feature_columns.pkl`
   - `tennis_model_metadata.json`
2. User has Premium subscription
3. Match ID exists in demo data or API response

### API Key Issues
If RapidAPI key is not working:
- Check subscription is active on RapidAPI
- Verify 100 requests/day limit not exceeded
- App will automatically fall back to demo mode

## 📊 Model Details

- **Training Data**: 13,174 ATP matches (2020-2024)
- **Features**: 25 features (rank, form, H2H, surface stats)
- **Algorithm**: RandomForest + CalibratedClassifierCV
- **Performance**:
  - ROC-AUC: 0.705
  - Accuracy: 64.8%
  - Brier Score: 0.218
- **Top Features**:
  1. rank_difference (17.86%)
  2. surface_winrate_diff (9.62%)
  3. form_difference (7.60%)

## 🎓 Next Steps (Future Enhancements)

1. **Live Scores**: Integrate live match results
2. **Historical Analysis**: Show past predictions vs actual results
3. **Player Profiles**: Detailed player statistics pages
4. **Betting Insights**: Add betting value analysis
5. **WTA Integration**: Add women's tennis
6. **Push Notifications**: Alert users before big matches
7. **Social Features**: Share predictions, leaderboards

## 📝 Files Modified/Created

### New Files
- `templates/tennis.html` - Frontend UI
- `api/routes_tennis.py` - Flask API endpoints
- `tennis/predict.py` - Prediction service
- `services/tennis_api.py` - RapidAPI client
- `tennis/download_data.py` - Data downloader
- `tennis/prepare_training_data.py` - Feature engineering
- `tennis/train_model.py` - ML training
- `TENNIS_INTEGRATION_PLAN.md` - Integration plan
- `TENNIS_PROGRESS.md` - Progress report
- `TENNIS_DEPLOYMENT.md` - This file

### Modified Files
- `app.py` - Added `/tennis` route and tennis_bp registration
- `templates/base.html` - Added Tennis navigation links
- `models.py` - Added TennisPlayer, TennisMatch, TennisPrediction

### Data Files (not committed to git)
- `tennis/data/atp_matches_combined.csv` (7.9 MB)
- `tennis/data/tennis_training_data.csv` (2.1 MB)
- `tennis/models/*.pkl` - ML models

## ✨ Success Criteria

- [x] Tennis page loads at `/tennis`
- [x] Navigation shows "🎾 Tennis" link
- [x] Demo matches display without API key
- [x] Premium users can generate predictions
- [x] Predictions show German explanations
- [x] Confidence levels displayed (High/Medium/Low)
- [x] Mobile-responsive design
- [x] Error handling for failed predictions
