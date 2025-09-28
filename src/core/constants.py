"""
Constantes globales para el scraper de UFC.
Incluye URLs base, campos de datos y otros valores fijos utilizados en el pipeline ETL.
Facilita la centralización y el mantenimiento de valores estáticos.
"""

 # URLs base para el scraping de datos
BASE_URL = "http://ufcstats.com"
FIGHTERS_URL = f"{BASE_URL}/statistics/fighters"
EVENTS_COMPLETED_URL = f"{BASE_URL}/statistics/events/completed"
EVENTS_UPCOMING_URL = f"{BASE_URL}/statistics/events/upcoming"
EVENT_URL = f"{BASE_URL}/event-details"
FIGHTER_URL = f"{BASE_URL}/fighter-details"
FIGHT_URL = f"{BASE_URL}/fight-details"

 # Campos de datos esperados para cada entidad
FIGHTER_FIELDS = [
    'fighter_id', 'first', 'last', 'nickname', 'height', 
    'weight', 'reach', 'stance', 'wins', 'defeats', 'draws', 'belt'
]

FIGHTER_DETAIL_FIELDS = [
    'dob', 'slpm', 'str_acc', 'sapm', 'str_def', 'td_avg', 'td_acc', 'td_def', 'sub_avg'
]

EVENT_FIELDS = ['event_id', 'name', 'date', 'location']

FIGHT_FIELDS = [
    'event_id', 'fight_id', 'fight_order', 'red_id', 'red_name',
    'blue_id', 'blue_name', 'winner_id', 'weight_class', 'referee',
    'round', 'time', 'time_format', 'method', 'details', 'bonus',
    'kd1', 'kd2', 'str1', 'str2', 'td1', 'td2', 'sub1', 'sub2',
    'control_time1', 'control_time2', 'sig_head1', 'sig_head2',
    'sig_body1', 'sig_body2', 'sig_leg1', 'sig_leg2',
    'total_str1', 'total_str2', 'pass1', 'pass2', 'rev1', 'rev2'
]

# Alfabeto utilizado para el scraping de luchadores (a-z)
ALPHABET = [chr(i) for i in range(97, 123)]  # a-z
