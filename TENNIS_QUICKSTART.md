# Tennis Feature - Quick Start Guide

## ✅ What's Been Added

### Tennis Predictions
- **ML Model**: 70.5% accuracy (better than football models!)
- **API Integration**: RapidAPI Tennis API with demo mode fallback
- **Premium Feature**: Only premium users can generate predictions
- **German UI**: Fully localized interface

### Features
- View upcoming tennis matches (ATP/WTA)
- Filter by surface (Hard/Clay/Grass), tournament, date range
- Generate AI predictions with confidence scores
- See detailed analysis (ranking, form, H2H, surface stats)

## 🚀 Quick Test (Local)

### 1. Run the App

```powershell
# Navigate to project
cd c:\Users\ПК\GoalPredictor.AI

# Run Flask app
python app.py
```

App will start at: http://localhost:5000

### 2. Test Tennis Page

Open browser: http://localhost:5000/tennis

You should see:
- ✅ Tennis page with upcoming matches (demo mode)
- ✅ 5 realistic demo matches (Djokovic vs Alcaraz, etc.)
- ✅ Filters for surface, tournament, date range
- ⚠️ "Premium erforderlich" warning if not logged in as Premium user

### 3. Test API Endpoints

```powershell
# Health check
curl http://localhost:5000/api/tennis/health

# Get matches (public endpoint)
curl http://localhost:5000/api/tennis/matches?days=7

# Get prediction (requires Premium login)
# First login as Premium user, then:
curl http://localhost:5000/api/tennis/predictions/demo_1
```

### 4. Test Navigation

Check these links work:
- Home → "🎾 Tennis" link in navbar
- Footer → "🎾 Tennis-Prognosen" link

## 📱 User Flow

### Non-Premium User
1. Visit `/tennis`
2. See demo matches
3. Click "Prognose anzeigen"
4. Redirected to `/pricing` page

### Premium User
1. Visit `/tennis`
2. See demo matches
3. Click "Prognose anzeigen"
4. Modal opens with prediction:
   - Player 1: 58.4% win probability
   - Player 2: 41.6% win probability
   - Confidence: Medium/High/Low
   - Explanation in German
   - Key factors (ranking, form, H2H)

## 🔧 Environment Setup (Optional)

### Add RapidAPI Key (Optional - works without it)

1. Sign up: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf
2. Subscribe to Free tier (100 requests/month)
3. Copy your API key
4. Create `.env` file:

```env
# Copy from .env.example
cp .env.example .env

# Add Tennis API key to .env
RAPIDAPI_TENNIS_KEY=your_key_here
```

**Provider**: MatchStat (https://matchstat.com/) - Professional tennis data API
**Features**: ATP, WTA, ITF coverage with detailed statistics
**Documentation**: https://matchstat.com/predictions-tips/the-best-tennis-data-api-for-stats/

**Note**: App works perfectly in demo mode without API key!

## 🎯 Testing Checklist

- [ ] Tennis page loads at `/tennis`
- [ ] Demo matches display (5 matches)
- [ ] Filters work (Surface, Tournament, Days)
- [ ] Navigation links work (navbar + footer)
- [ ] Non-premium user sees "Premium erforderlich" warning
- [ ] Premium user can generate predictions
- [ ] Prediction modal shows:
  - [ ] Win probabilities (e.g., 58.4% vs 41.6%)
  - [ ] Confidence level (High/Medium/Low)
  - [ ] German explanation
  - [ ] Key factors with impact levels
- [ ] Mobile responsive design works
- [ ] API health check responds

## 🐛 Common Issues

### Issue: App won't start
**Solution**: Check DATABASE_URL in .env uses local SQLite:
```env
DATABASE_URL=sqlite:///goalpredictor.db
```

### Issue: Demo matches not showing
**Solution**: Check console for errors. Demo mode should always work.
Verify `services/tennis_api.py` has `_get_demo_data()` method.

### Issue: Can't generate predictions
**Solution**: 
1. Check you're logged in as Premium user
2. Verify model files exist in `tennis/models/`
3. Check browser console for JavaScript errors

### Issue: Prediction shows error
**Solution**: Check Flask console for Python errors.
Common causes:
- Model files missing
- Database connection issues
- Feature extraction failed

## 📊 Demo Data

Demo mode includes 5 realistic matches:

1. **Novak Djokovic vs Carlos Alcaraz** (Miami Masters, Hard)
2. **Daniil Medvedev vs Jannik Sinner** (Monte Carlo, Clay)
3. **Iga Swiatek vs Aryna Sabalenka** (Madrid, Clay)
4. **Stefanos Tsitsipas vs Andrey Rublev** (Rome Masters, Clay)
5. **Alexander Zverev vs Casper Ruud** (French Open, Clay)

## 🚢 Deploy to Production

When ready to deploy:

```powershell
# Commit all changes
git add .
git commit -m "feat(tennis): Complete tennis integration"

# Push to production
git push origin master:main
```

Render will automatically:
- Build the app
- Run database migrations
- Start the service

Test production: https://your-app.onrender.com/tennis

## 📈 Next Steps

After testing locally:
1. Test with real Premium account
2. Verify all predictions work
3. Test on mobile devices
4. Deploy to production
5. Monitor logs for errors
6. Add RapidAPI key to Render environment variables (optional)

## 🎓 Architecture

```
User Request
    ↓
/tennis (Route in app.py)
    ↓
templates/tennis.html (Frontend)
    ↓
/api/tennis/matches (API endpoint)
    ↓
services/tennis_api.py (RapidAPI client)
    ↓
Demo Data / RapidAPI (Data source)

User clicks "Prognose anzeigen"
    ↓
/api/tennis/predictions/<match_id>
    ↓
tennis/predict.py (ML service)
    ↓
tennis/models/tennis_player1_win_model.pkl
    ↓
Prediction with probabilities
```

## 📚 Documentation

- `TENNIS_INTEGRATION_PLAN.md` - Original integration plan
- `TENNIS_PROGRESS.md` - Development progress
- `TENNIS_DEPLOYMENT.md` - Deployment guide (this file)
- `README.md` - Main project documentation

## 🎉 Success!

If you can:
- ✅ See tennis matches at `/tennis`
- ✅ Generate predictions as Premium user
- ✅ See German UI with confidence scores

Then tennis integration is complete! 🎾
