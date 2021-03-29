# Student Project
## Password-less login
The process for the password-less login is the following one:
1. User goes to '/x/login'.
2. User enters username.
3. A JWT is generated. This token allows the user to log in during the following LOGIN_URL_EXPIRES_IN seconds.
4. A URL is generated, which contains such token as an argument.
5. The URL is sent to the user (for now, printed to the console).
6. The user clicks URL in the device he/she/x wants to log in in.
7. The JWT is verified, that is:
    1. It was signed by the server using the secret key.
    2. It has not expired.
    3. It corresponds to the user we are trying to load.
    4. It allows action 'login'.
8. The user is logged in.


## Password-less signup
The process for the password-less signup (assuming you want to use email) would be the following one (no temp password required):
1. User goes to '/x/sign-up'.
2. User enters username and email.
3. A JWT is generated. This token allows the user to sign in during the following SIGNUP_URL_EXPIRES_IN seconds.
4. A URL is generated, which contains such token as an argument.
5. The URL is sent to the user (for now, printed to the console).
6. The user clicks URL in the device he/she/x wants to sign-up in to confirm the email.
7. The JWT is verified, that is:
    1. It was signed by the server using the secret key.
    2. It has not expired.
    3. It corresponds to the user we are trying to load.
    4. It allows action 'signup'.
8. The user is signed-up.
9. The user is logged in.