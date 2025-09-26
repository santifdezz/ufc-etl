"""Constants for UFC scraper."""

# Base URLs
BASE_URL = "http://ufcstats.com"
FIGHTERS_URL = f"{BASE_URL}/statistics/fighters"
EVENTS_COMPLETED_URL = f"{BASE_URL}/statistics/events/completed"
EVENTS_UPCOMING_URL = f"{BASE_URL}/statistics/events/upcoming"
EVENT_URL = f"{BASE_URL}/event-details"
FIGHTER_URL = f"{BASE_URL}/fighter-details"
FIGHT_URL = f"{BASE_URL}/fight-details"

# Data fields
FIGHTER_FIELDS = [
    'fighter_id', 'first', 'last', 'nickname', 'height', 
    'weight', 'reach', 'stance', 'wins', 'losses', 'defeats', 'belt'
]

FIGHTER_DETAIL_FIELDS = [
    'dob', 'slpm', 'str_acc', 'sapm', 'str_def', 'td_avg', 'td_acc', 'td_def', 'sub_avg'
]

EVENT_FIELDS = ['event_id', 'name', 'date', 'location', 'status']

FIGHT_FIELDS = [
    'event_id', 'fight_id', 'fight_order', 'fighter1_id', 'fighter1_name',
    'fighter2_id', 'fighter2_name', 'winner_id', 'weight_class', 'referee',
    'round', 'time', 'time_format', 'method', 'details', 'bonus',
    'kd1', 'kd2', 'str1', 'str2', 'td1', 'td2', 'sub1', 'sub2',
    'control_time1', 'control_time2', 'sig_head1', 'sig_head2',
    'sig_body1', 'sig_body2', 'sig_leg1', 'sig_leg2',
    'total_str1', 'total_str2', 'pass1', 'pass2', 'rev1', 'rev2'
]

# Alphabet for fighter scraping
ALPHABET = [chr(i) for i in range(97, 123)]  # a-z
