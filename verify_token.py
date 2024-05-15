from epic_events.controllers.authentication import verify_and_decode_jwt_token

decoded_payload = verify_and_decode_jwt_token()

if decoded_payload:
    print("User_id du token :", decoded_payload['user_id'])
else:
    print("\033[91mLe jeton JWT est invalide ou expiré.\033[0m")