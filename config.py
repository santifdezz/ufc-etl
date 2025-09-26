# Global scraping configuration
MAX_WORKERS = 5  # Number of concurrent workers for ThreadPoolExecutor
DELAY = 3        # Delay (seconds) between requests
# Modo desarrollo/test
DEV_MODE = False  # Cambia a True en tests
DEV_LIMIT = 20    # Número máximo de registros a procesar en modo dev/test

## Rutas BASE
BASE_URL = "http://ufcstats.com"
FIGHTERS_URL = f"{BASE_URL}/statistics/fighters"
EVENTS_COMPLETED_URL = f"{BASE_URL}/statistics/events/completed"
EVENTS_UPCOMING_URL = f"{BASE_URL}/statistics/events/upcoming"
EVENT_URL = f"{BASE_URL}/event-details"
FIGHTER_URL = f"{BASE_URL}/fighter-details"
FIGHT_URL = f"{BASE_URL}/fight-details"

# Rutas base para datos y tests
DATA_DIR = 'data'
TEST_DATA_DIR = 'data/tests'

ALPHABET = [chr(i) for i in range(97, 123)]  # a to z

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
