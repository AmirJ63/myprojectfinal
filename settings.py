from os import environ


SESSION_CONFIGS = [
    dict(
        name='study',
        display_name="Study",
        app_sequence=['kk11', 'kk2', 'cardgame'],
        num_demo_participants=4
    ),
    dict(
        name='kk11',
        display_name="kk11",
        app_sequence=['kk11', 'kk2'],
        num_demo_participants=3,
    ),
    dict(
        name='kk11_test',
        display_name="kk11 (Test)",
        app_sequence=['kk11', 'kk2'],
        num_demo_participants=10,
    ),
    dict(
        name='cardgame',
        display_name="card game",
        app_sequence=['cardgame'],
        num_demo_participants=2,
    )
]




# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = [
    'score',
    'group',
    'cardgame_to_pay',
    'cardgame_score_1',
    'cardgame_payoff_1',
    'cardgame_score_2',
    'cardgame_payoff_2'
]

SESSION_FIELDS = [
    'scores',
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '5765689287549'

INSTALLED_APPS = ['otree']
