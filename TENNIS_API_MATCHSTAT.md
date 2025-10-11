# Tennis API Integration - MatchStat

## 🎾 Overview

We're using **Tennis API ATP-WTA-ITF** by MatchStat - a professional tennis data API used by their betting tips service at [MatchStat.com](https://matchstat.com/).

## 📊 Provider Information

- **Provider**: MatchStat
- **Website**: https://matchstat.com/
- **API Name**: Tennis API ATP-WTA-ITF
- **RapidAPI Link**: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf
- **Documentation**: https://matchstat.com/predictions-tips/the-best-tennis-data-api-for-stats/
- **Tutorial**: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf/tutorials/how-to-use-apis
- **Support Email**: tennisapi@matchstat.com

## 🎯 Features

### Data Coverage
- **ATP** (Association of Tennis Professionals) - Men's tennis
- **WTA** (Women's Tennis Association) - Women's tennis
- **ITF** (International Tennis Federation) - Challenger/Futures

### Available Data
✅ Live scores and match results
✅ Fixtures and schedules
✅ Player rankings (ATP/WTA)
✅ Player profiles and statistics
✅ Head-to-head records
✅ Historical match data
✅ Tournament information
✅ Surface-specific statistics (Hard/Clay/Grass)

### Used by MatchStat for:
- Daily betting tips: https://matchstat.com/tennis/betting-tips/
- Match predictions with AI/ML models
- Professional tennis forecasting service

## 💰 Pricing

### Free Tier
- **100 requests per month**
- Full access to all endpoints
- Perfect for MVP and testing
- No credit card required

### Pro Plans (if needed later)
- **Basic**: 500 requests/month
- **Pro**: 2,000 requests/month
- **Ultra**: 10,000 requests/month

## 🔑 Setup

### 1. Sign Up
1. Visit: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf
2. Click "Subscribe to Test"
3. Choose **Free** plan (100 requests/month)
4. Copy your API key from dashboard

### 2. Add to .env
```bash
RAPIDAPI_TENNIS_KEY=your_rapidapi_key_here
```

### 3. Test Connection
```powershell
# Run the app
python app.py

# Test health endpoint
curl http://localhost:5000/api/tennis/health

# Get upcoming matches
curl http://localhost:5000/api/tennis/matches?days=7
```

## 📡 API Endpoints

### Current Implementation

Our `services/tennis_api.py` uses:

#### 1. Get Fixtures
```
GET /fixtures?date=YYYY-MM-DD
```
Returns upcoming matches for a specific date.

**Response**:
```json
{
  "results": 10,
  "response": [
    {
      "id": "12345",
      "tournament": {
        "name": "ATP Paris Masters",
        "category": "ATP 1000"
      },
      "date": "2025-10-12T14:00:00Z",
      "status": "Not Started",
      "teams": {
        "home": {
          "name": "Novak Djokovic",
          "rank": 1,
          "country": { "code": "SRB" }
        },
        "away": {
          "name": "Carlos Alcaraz",
          "rank": 2,
          "country": { "code": "ESP" }
        }
      },
      "surface": "Hard",
      "round": "Final"
    }
  ]
}
```

#### 2. Get Live Scores (Future Enhancement)
```
GET /live
```
Returns matches currently in progress.

#### 3. Get Rankings (Future Enhancement)
```
GET /rankings?tour=ATP&date=YYYY-MM-DD
```
Returns current ATP/WTA rankings.

#### 4. Get Player Statistics (Future Enhancement)
```
GET /player/{player_id}/statistics
```
Returns detailed player stats.

#### 5. Get Head-to-Head (Future Enhancement)
```
GET /h2h?player1={id}&player2={id}
```
Returns head-to-head record between two players.

## 🛠️ Implementation Details

### Current Code Structure

```python
# services/tennis_api.py
class TennisAPIService:
    BASE_URL = "https://tennis-api-atp-wta-itf.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_TENNIS_KEY')
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'tennis-api-atp-wta-itf.p.rapidapi.com'
        }
    
    def get_upcoming_matches(self, days=7):
        """Fetch fixtures for next N days"""
        # Returns matches with player names, ranks, surface, etc.
        pass
```

### Demo Mode
When `RAPIDAPI_TENNIS_KEY` is not set:
- API automatically falls back to demo data
- Shows 5 realistic demo matches
- Includes Djokovic, Alcaraz, Medvedev, Sinner, etc.
- No API key required for development

### Caching
- **TTL**: 24 hours per request
- **Storage**: In-memory dictionary
- **Key**: `fixtures_{date}`
- **Purpose**: Minimize API calls to stay within free tier limits

## 📊 API Comparison

### vs Previous API (api-tennis by API-Sports)

| Feature | MatchStat Tennis API | api-tennis |
|---------|---------------------|------------|
| Free Tier | 100 req/month | 100 req/day |
| Coverage | ATP + WTA + ITF | ATP only |
| Provider | MatchStat.com | API-Sports |
| Live Scores | ✅ Yes | ✅ Yes |
| Rankings | ✅ Yes | ✅ Yes |
| H2H Stats | ✅ Yes | ⚠️ Limited |
| Use Case | Betting/Predictions | General data |
| Support | Direct email | Forum only |

**Why we chose MatchStat**:
- ✅ Professional provider used for betting tips
- ✅ More detailed statistics
- ✅ Direct support (tennisapi@matchstat.com)
- ✅ Better documentation
- ✅ ATP + WTA + ITF coverage

## 🔍 Request Optimization

To stay within 100 requests/month:

### Smart Caching Strategy
```python
# Cache fixtures for 24 hours
self.cache_ttl = 86400  # seconds

# Don't re-fetch if cached
if cache_key in self.cache:
    cached_data, cached_time = self.cache[cache_key]
    if (datetime.now().timestamp() - cached_time) < self.cache_ttl:
        return cached_data
```

### Batch Requests
```python
# Fetch 7 days of matches at once
matches = tennis_api.get_upcoming_matches(days=7)

# Instead of making separate requests per match
```

### Demo Mode First
```python
# Use demo data during development
if not self.api_key or self.api_key == 'DEMO_KEY':
    return self._get_demo_data(endpoint)
```

### Estimated Usage
- **Development**: 0 requests (demo mode)
- **Testing**: ~10 requests
- **Production**: 
  - Daily match fetch: ~30 requests/month
  - User predictions: ~50 requests/month
  - Headroom: 20 requests/month
- **Total**: ~100 requests/month ✅ Within limit!

## 🚀 Future Enhancements

### Phase 1 (Current)
- ✅ Get upcoming fixtures
- ✅ Parse match data
- ✅ Demo mode fallback

### Phase 2 (Next)
- [ ] Live scores integration
- [ ] Real-time match updates
- [ ] WebSocket support for live data

### Phase 3 (Later)
- [ ] Player rankings display
- [ ] Head-to-head statistics
- [ ] Historical match analysis
- [ ] Player profile pages

### Phase 4 (Advanced)
- [ ] Live betting odds integration
- [ ] Match prediction accuracy tracking
- [ ] Tournament bracket visualization
- [ ] Push notifications for matches

## 📧 Support

### Contact MatchStat
- **Email**: tennisapi@matchstat.com
- **Subject**: "Tennis API ATP-WTA-ITF - [Your Question]"
- **Response Time**: Usually within 24 hours

### Common Questions
**Q: How to increase request limit?**
A: Upgrade to paid plan on RapidAPI

**Q: Can I get historical data?**
A: Yes, use `/fixtures?date=YYYY-MM-DD` for past dates

**Q: Live scores included?**
A: Yes, use `/live` endpoint (not yet implemented in our app)

**Q: Which tournaments covered?**
A: All ATP, WTA, ITF tournaments including Grand Slams

## 🔗 Useful Links

- **MatchStat Website**: https://matchstat.com/
- **Tennis Betting Tips**: https://matchstat.com/tennis/betting-tips/
- **RapidAPI Page**: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf
- **Documentation**: https://matchstat.com/predictions-tips/the-best-tennis-data-api-for-stats/
- **API Tutorial**: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf/tutorials/how-to-use-apis

## ✅ Integration Status

- [x] API service created (`services/tennis_api.py`)
- [x] Headers configured for MatchStat API
- [x] Demo mode fallback implemented
- [x] Caching strategy implemented
- [x] Fixtures endpoint integrated
- [x] Match parsing working
- [x] Documentation updated
- [ ] Live scores (future)
- [ ] Rankings (future)
- [ ] H2H stats (future)

## 🎉 Ready to Use!

The integration is **production-ready** with:
- ✅ Demo mode for development (no API key needed)
- ✅ Professional data provider (MatchStat)
- ✅ Smart caching (24h TTL)
- ✅ Error handling and fallbacks
- ✅ Comprehensive documentation

Just add your API key to start using real tennis data! 🎾
