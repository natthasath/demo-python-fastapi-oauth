import fastapi
import jwt
import datetime

app = fastapi.FastAPI()

# A simple example of client data
client_data = {
    "client_id": "123456789",
    "client_secret": "abcdefghijklmno",
    "redirect_uri": "http://localhost:5000/callback",
}

# Set the secret key for JWT
app.secret_key = "api"

# A function to generate an access token and refresh token for a client
def generate_tokens(client_id):
    # Set the expiration time for the tokens
    access_token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=600) # 10 minutes
    refresh_token_expiration = datetime.datetime.utcnow() + datetime.timedelta(seconds=86400) # 24 hours
    
    # Generate the access token and refresh token using JWT
    access_token = jwt.encode(
        {"client_id": client_id, "exp": access_token_expiration},
        app.secret_key,
        algorithm="HS256",
    )
    refresh_token = jwt.encode(
        {"client_id": client_id, "exp": refresh_token_expiration},
        app.secret_key,
        algorithm="HS256",
    )
    
    # Return the access token and refresh token
    return access_token, refresh_token

# A route for the client to request an OAuth token
@app.post("/oauth/token")
async def request_token(client_id: str, client_secret: str, redirect_uri: str):
    # Check if the client data is valid
    if (
        client_id != client_data["client_id"]
        or client_secret != client_data["client_secret"]
        or redirect_uri != client_data["redirect_uri"]
    ):
        return {"error": "invalid_client"}, 400
    
    # Generate the access token and refresh token
    access_token, refresh_token = generate_tokens(client_id)
    
    # Return the access token and refresh token to the client
    return {"access_token": access_token, "refresh_token": refresh_token}, 200

# A route for the client to refresh an access token
@app.post("/oauth/refresh")
async def refresh_token(refresh_token: str):
    # Check if the refresh token is valid
    try:
        decoded_refresh_token = jwt.decode(refresh_token, app.secret_key, algorithms=["HS256"])
        client_id = decoded_refresh_token["client_id"]
    except Exception as e:
        return {"error": "invalid_refresh_token"}, 400
    
    # Generate a new access token
    access_token, _ = generate_tokens(client_id)
    
    # Return the new access token to the client
    return {"access_token": access_token}, 200
