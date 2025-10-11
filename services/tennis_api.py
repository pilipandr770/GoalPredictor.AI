"""
Tennis API Service
Integration with Tennis API ATP-WTA-ITF by MatchStat (RapidAPI)
Website: https://matchstat.com/
Documentation: https://matchstat.com/predictions-tips/the-best-tennis-data-api-for-stats/
FREE tier: 100 requests/month
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TennisAPIService:
    """
    Tennis API Service using Tennis API ATP-WTA-ITF from MatchStat
    
    FREE PLAN: 100 requests/month
    Signup: https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf
    Contact: tennisapi@matchstat.com
    
    Features:
    - Live scores and fixtures
    - ATP, WTA, ITF coverage
    - Head-to-head statistics
    - Player rankings and profiles
    - Historical match data
    """
    
    BASE_URL = "https://tennis-api-atp-wta-itf.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_TENNIS_KEY')
        
        # Debug logging
        if self.api_key and not self.api_key.startswith('your-'):
            print(f"✅ Tennis API key loaded: {self.api_key[:20]}...{self.api_key[-10:]}")
        else:
            print("⚠️  Tennis API key NOT loaded - using demo mode")
            
        self.headers = {
            'X-RapidAPI-Key': self.api_key if self.api_key else 'DEMO_KEY',
            'X-RapidAPI-Host': 'tennis-api-atp-wta-itf.p.rapidapi.com'
        }
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            # Check if we have API key
            if not self.api_key or self.api_key == 'DEMO_KEY' or self.api_key.startswith('your-'):
                logger.warning("⚠️  RAPIDAPI_TENNIS_KEY not set. Using demo data.")
                return self._get_demo_data(endpoint, params)
            
            # Build URL based on endpoint type
            if endpoint == 'fixtures' and params and 'date' in params:
                # Date fixtures: /tennis/v2/atp/fixtures/{date}
                date_str = params['date']
                url = f"{self.BASE_URL}/tennis/v2/atp/fixtures/{date_str}"
            elif endpoint == 'rankings':
                # Rankings: /tennis/v2/atp/rankings/singles
                url = f"{self.BASE_URL}/tennis/v2/atp/rankings/singles"
            else:
                # Fallback
                url = f"{self.BASE_URL}/{endpoint}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            print(f"🔍 API Request: {url}")
            print(f"🔍 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"🔍 Response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                if isinstance(data, dict) and 'results' in data:
                    print(f"🔍 Found {data.get('results', 0)} results")
                logger.info(f"✓ API call successful: {endpoint}")
                return data
            elif response.status_code == 401:
                logger.error(f"❌ Authentication failed - check your API key")
                return self._get_demo_data(endpoint, params)
            elif response.status_code == 429:
                logger.error(f"❌ Rate limit exceeded - using demo data")
                return self._get_demo_data(endpoint, params)
            else:
                logger.error(f"❌ API error {response.status_code}: {endpoint}")
                return self._get_demo_data(endpoint, params)
                
        except Exception as e:
            logger.error(f"❌ API exception: {e}")
            return self._get_demo_data(endpoint, params)
    
    def _get_demo_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Return demo data when API key is not available"""
        if 'fixtures' in endpoint or (params and 'date' in params):
            return {
                'results': 5,
                'response': [
                    {
                        'id': 'demo_1',
                        'tournament': {'name': 'ATP Paris Masters'},
                        'date': (datetime.now() + timedelta(days=1)).isoformat(),
                        'status': 'Not Started',
                        'teams': {
                            'home': {'name': 'Novak Djokovic', 'rank': 1},
                            'away': {'name': 'Carlos Alcaraz', 'rank': 2}
                        },
                        'surface': 'Hard',
                        'round': 'Final'
                    },
                    {
                        'id': 'demo_2',
                        'tournament': {'name': 'ATP Paris Masters'},
                        'date': (datetime.now() + timedelta(days=1)).isoformat(),
                        'status': 'Not Started',
                        'teams': {
                            'home': {'name': 'Daniil Medvedev', 'rank': 3},
                            'away': {'name': 'Jannik Sinner', 'rank': 4}
                        },
                        'surface': 'Hard',
                        'round': 'Semifinal'
                    },
                    {
                        'id': 'demo_3',
                        'tournament': {'name': 'WTA Finals'},
                        'date': (datetime.now() + timedelta(days=2)).isoformat(),
                        'status': 'Not Started',
                        'teams': {
                            'home': {'name': 'Iga Swiatek', 'rank': 1},
                            'away': {'name': 'Aryna Sabalenka', 'rank': 2}
                        },
                        'surface': 'Hard',
                        'round': 'Final'
                    },
                    {
                        'id': 'demo_4',
                        'tournament': {'name': 'ATP Paris Masters'},
                        'date': datetime.now().isoformat(),
                        'status': 'Not Started',
                        'teams': {
                            'home': {'name': 'Alexander Zverev', 'rank': 5},
                            'away': {'name': 'Stefanos Tsitsipas', 'rank': 6}
                        },
                        'surface': 'Hard',
                        'round': 'Quarterfinal'
                    },
                    {
                        'id': 'demo_5',
                        'tournament': {'name': 'ATP Paris Masters'},
                        'date': datetime.now().isoformat(),
                        'status': 'Not Started',
                        'teams': {
                            'home': {'name': 'Andrey Rublev', 'rank': 7},
                            'away': {'name': 'Holger Rune', 'rank': 8}
                        },
                        'surface': 'Hard',
                        'round': 'Quarterfinal'
                    }
                ]
            }
        
        return {'results': 0, 'response': []}
    
    def get_upcoming_matches(self, days: int = 7) -> List[Dict]:
        """
        Get upcoming tennis matches for next N days
        
        Returns:
            List of matches with structure:
            {
                'id': 'match_id',
                'date': datetime,
                'tournament': 'Australian Open',
                'round': 'Quarterfinal',
                'surface': 'Hard',
                'player1': {
                    'name': 'Novak Djokovic',
                    'rank': 1,
                    'country': 'SRB'
                },
                'player2': {
                    'name': 'Carlos Alcaraz',
                    'rank': 2,
                    'country': 'ESP'
                }
            }
        """
        logger.info(f"🎾 Fetching upcoming tennis matches (next {days} days)...")
        
        matches = []
        
        # Try to get matches for next N days
        for day_offset in range(days):
            date = datetime.now() + timedelta(days=day_offset)
            date_str = date.strftime('%Y-%m-%d')
            
            # Cache key
            cache_key = f"fixtures_{date_str}"
            
            # Check cache
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now().timestamp() - cached_time) < self.cache_ttl:
                    logger.info(f"  ✓ Using cached data for {date_str}")
                    data = cached_data
                else:
                    data = self._make_request('fixtures', {'date': date_str})
                    self.cache[cache_key] = (data, datetime.now().timestamp())
            else:
                data = self._make_request('fixtures', {'date': date_str})
                if data:
                    self.cache[cache_key] = (data, datetime.now().timestamp())
            
            # API returns 'data' key with array of matches
            if data and 'data' in data:
                for fixture in data['data']:
                    try:
                        match = self._parse_fixture(fixture)
                        if match:
                            matches.append(match)
                    except Exception as e:
                        logger.error(f"Error parsing fixture: {e}")
                        continue
        
        logger.info(f"  ✓ Found {len(matches)} upcoming matches")
        return matches
    
    def _parse_fixture(self, fixture: Dict) -> Optional[Dict]:
        """Parse API fixture to our format (MatchStat API structure)"""
        try:
            # Extract data from MatchStat API response
            match_id = str(fixture.get('id', ''))
            
            # Date
            date_str = fixture.get('date', '')
            match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else datetime.now()
            
            # Players - directly in fixture object
            player1 = fixture.get('player1', {})
            player2 = fixture.get('player2', {})
            
            # Tournament ID (we'll need to fetch tournament name separately or use cache)
            tournament_id = fixture.get('tournamentId', '')
            tournament_name = f'Tournament {tournament_id}'  # Simplified for now
            
            # Round ID (we'll map common rounds)
            round_id = fixture.get('roundId', 0)
            round_map = {
                1: 'Final', 2: 'Semifinal', 3: 'Quarterfinal',
                4: 'R16', 5: 'R32', 6: 'R64', 7: 'R128',
                10: 'Qualifying', 11: 'Q1', 12: 'Q2'
            }
            round_name = round_map.get(round_id, f'Round {round_id}')
            
            # Surface - not in basic fixture, default to Hard
            surface = fixture.get('surface', 'Hard')
            
            match = {
                'id': match_id,
                'date': match_date,
                'tournament': tournament_name,
                'round': round_name,
                'surface': surface,
                'status': 'Scheduled',
                'player1': {
                    'name': player1.get('name', 'Unknown'),
                    'rank': player1.get('rank', 999),  # May not be in fixture
                    'country': player1.get('countryAcr', '')
                },
                'player2': {
                    'name': player2.get('name', 'Unknown'),
                    'rank': player2.get('rank', 999),
                    'country': player2.get('countryAcr', '')
                }
            }
            
            return match
            
        except Exception as e:
            logger.error(f"Error parsing fixture: {e}")
            return None
    
    def get_player_stats(self, player_name: str) -> Optional[Dict]:
        """
        Get player statistics
        
        Returns player info including:
        - Rank
        - Points
        - Recent form
        """
        # Not implemented in demo - would require additional API calls
        logger.info(f"🎾 Getting stats for {player_name}...")
        return None
    
    def get_h2h(self, player1_name: str, player2_name: str) -> Optional[Dict]:
        """
        Get head-to-head statistics
        
        Returns:
            {
                'player1_wins': 5,
                'player2_wins': 3,
                'total': 8
            }
        """
        # Not implemented in demo - would require additional API calls
        logger.info(f"🎾 Getting H2H: {player1_name} vs {player2_name}...")
        return None


# Global instance
tennis_api_service = TennisAPIService()


def get_tennis_api_service() -> TennisAPIService:
    """Get tennis API service instance"""
    return tennis_api_service
