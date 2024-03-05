"""Login response implementation."""

response_login = {
    "login": {
        200: {"description": "api017"},
        401: {"description": 'api006 to api008'},
        422: {"description": 'api018 - api019'}
    },
    "refresh": {
        401: {"description": 'api007'},
    },
    "first_access": {
        200: {"description": "api017"},
        400: {"description": "api001 to api005 - api007 - api009 - api112"},
        401: {"description": "api007"},
        412: {"description": "api010"},
    },

}
