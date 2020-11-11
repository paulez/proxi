## Current authentication scheme

User can register a username, which is then mapped to a radius around the user location. The session mechanism is used to authenticated upcoming requests.
Only user with the session can re-use the username in the area for a given time. After this time expires, the user can be expired when someone claims the same username
in the same area.

## Problems

* Authentication is performed using sessions. This is expensive on the backend as sessions have to be tracked.
* The username re-use logic is complex. An active session is need to be able to re-use the username.

## Proposed solution

Use DRF Token authentication instead of session. User registers a username, and gets a token to authenticate with this username. The area logic is kept to allow same usernames on different locations. Username registration is linked to the creation of a User on the backend. The user will be expired when the user has not been used for a given time, and a user tries to register the same username in the area. A new backend user is created when registering with the same username.

## APIs

### register
* path: api/register
* parameters:
 * username
 * position
* returns
 * token

## TODO

* Fix tests
* Use token auth in all existing APIs
* deprecate previous login/logout APIs
