"""Admin User response implementation."""

admin_user = {
    "create_user": {
        200: {"description": "api024"},
        401: {"description": 'api006 to api008'},
        422: {"description": 'api018 - api019'}
    },
    "update_user": {
        200: {"description": "api036"},
        400: {"description": "api001 to api005 - api009 - api112"},
        401: {"description": "api007"},
        412: {"description": "api010"},
    }
}
