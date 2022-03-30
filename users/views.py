import email
from urllib import request
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import requests
from django.core.exceptions import ValidationError
from django.conf import settings

from django.http import HttpResponse

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.compat import set_cookie_with_token

from users.models import Player
from django.contrib.auth.models import User

qualified_emails = [
    "f20180029@pilani.bits-pilani.ac.in"
]

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'

def jwt_login(*, response, user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    if api_settings.JWT_AUTH_COOKIE:
        set_cookie_with_token(response, api_settings.JWT_AUTH_COOKIE, token)

    return response

class UserAuthorization(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("Entered login....")

        id_token = request.headers.get('Authorization')
        response = requests.get(
            GOOGLE_ID_TOKEN_INFO_URL,
            params={'id_token': id_token}
        )
        print("Got response from google")

        if not response.ok:
            raise ValidationError('id_token is invalid.')

        audience = response.json()['aud']

        if audience != settings.GOOGLE_OAUTH2_CLIENT_ID:
            raise ValidationError('Invalid audience.')

        user_email = request.data["email"]
        domain = user_email.split('@')[1]
        if domain != "pilani.bits-pilani.ac.in":
            return Response(data = {"msg": "You can only login using BITS Email!"}, status=401)


        ### FOR ROUND 2 ###
        # if user_email not in qualified_emails:
        #     return Response(data = {"msg": "Sorry, you have not qualified to compete in Level 2!"}, status=201)
        ###################

        name = request.data["first_name"] + " " + request.data["last_name"]

        user = User.objects.get_or_create(username = user_email, email = user_email)[0]
        print(user)
        if user is not None:
            player = Player.objects.get_or_create(user = user)[0]
            print(player)
            player.name = name
            player.save()

            user_data = {
                "email": user_email,
                "name": name,
            }
            response = Response(data = user_data, status=200)
            response = jwt_login(response = response, user = user)

            return response 
        else:
            return Response(data = {"msg": "Failed to login! Please try again."}, status=401)
