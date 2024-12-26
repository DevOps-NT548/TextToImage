import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import User, Profile, hash_password
from account.serializers import UserSerializer, ProfileSerializer
from rest_framework.parsers import JSONParser
from django.contrib.sessions.models import Session
from google.cloud import storage
from dotenv import load_dotenv
from django.conf import settings
import base64
import re
from PIL import Image
from io import BytesIO

# Load the environment variables from the .env file
load_dotenv()

credential_json = settings.CREDENTIAL_JSON
bucket_name = settings.STORAGE_BUCKET
avatar_folder = 'AVATARs'
default_path = 'https://storage.googleapis.com/img_bucket04/AVATARs'

try:
    storage_client = storage.Client.from_service_account_json(credential_json)
    bucket = storage_client.bucket(bucket_name)
    print("Successfully accessed the bucket")
except Exception as e:
    print(f"Failed to access the bucket: {e}")


def save_uploaded_file(uploaded_file_base64: str, file_name: str) -> str:
    """
    Saves a base64-encoded image file to a Google Cloud Storage bucket.

    Args:
        uploaded_file_base64 (str): Base64-encoded content of the file.
        file_name (str): The name of the file (without extension).
        file_extension (str): The file extension (e.g., 'jpg', 'png').

    Returns:
        str: The full destination path of the uploaded file in the bucket.

    Raises:
        ValueError: If the base64 decoding or image validation fails.
        Exception: If the upload to GCP fails.
    """
    # Validate file extension
    try:
        _, uploaded_file_base64 = uploaded_file_base64.split(",", 1)
        print(uploaded_file_base64[0:100])
        file_data = base64.b64decode(uploaded_file_base64)
        with Image.open(BytesIO(file_data)) as img:
            img.verify()
            file_extension = img.format.lower()
            print(file_extension)
    except Exception as e:
        raise ValueError("The provided base64 string does not represent a valid image.") from e

    # Construct the full destination path
    sanitized_file_name = re.sub(r'[^a-zA-Z0-9_-]', '', file_name)
    file_path_in_bucket = os.path.join(
        default_path, f"{sanitized_file_name}.{file_extension.lower()}"
    )

    try:
        # Create a blob and upload the file data
        blob = bucket.blob(f"{avatar_folder}/{sanitized_file_name}.{file_extension.lower()}")
        blob.upload_from_string(file_data, content_type=f"image/{file_extension.lower()}")
    except Exception as e:
        raise Exception(f"Failed to upload the file to the bucket: {e}")

    return file_path_in_bucket


class Register(APIView):
    def post(self, request, *args, **kwargs):
        """
        This function handles the HTTP POST request. It receives the request object, which contains the data sent by the client. The function expects a JSON object in the request body, containing the user's full name and password. It returns a response object with the appropriate status code and data.

        Parameters:
            request: The HTTP request object containing the JSON data sent by the client.

        Returns:
            response: The HTTP response object containing the result of the POST request. If the request is valid, a success response is returned with the user data excluding the password. If the request is invalid, an error response is returned with the appropriate status code and error message.
        """
        user_data = JSONParser().parse(request)
        print(user_data)
        profile_serializers = ProfileSerializer(
            data={"full_name": user_data["full_name"], "bio": ""}
        )
        if profile_serializers.is_valid():
            profile_serializers.save()
        else:
            return Response(
                {"status": "error", "data": profile_serializers.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = Profile.objects.last()

        user_data.update({"profile": getattr(profile, "profile_id")})
        # Hashing the password
        user_data.update({"password": hash_password(user_data["password"])})
        user_serializers = UserSerializer(data=user_data)

        if user_serializers.is_valid():
            if user_serializers.is_valid():
                user_serializers.save()
                return Response(
                    {
                        "status": "success",
                        "data": {
                            key: value
                            for key, value in user_serializers.data.items()
                            if key != "password"
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "data": user_serializers.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # modify error message when user is invalid --> trim the 'profile' message
            print(type(user_serializers.errors))
            error_response = {}
            error_response.update(user_serializers.errors)
            if "profile" in error_response:
                del error_response["profile"]
            return Response(
                {"status": "error", "data": error_response},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Login(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for logging in a user.

        Args:
            request: The request object containing the user data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the login status and user data.
        """
        try:
            user_data = JSONParser().parse(request)
            user_serializers = UserSerializer(data=user_data)

            temp_serializers = {}
            temp_serializers.update(user_serializers.initial_data)
            del temp_serializers["password"]

            for user in User.objects.all():
                if user.isAuthenticated(user_data["username"], user_data["password"]):
                    temp_serializers["profile"] = str(user.getProfileId())
                    temp_serializers["user_id"] = user.user_id
                    temp_serializers["email"] = user.email
                    return Response(
                        {"status": "Logged in successfully", "data": temp_serializers},
                        status=status.HTTP_200_OK,
                    )

            return Response(
                {
                    "status": "Wrong password or account doesn't exist!",
                    "data": temp_serializers,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            print(error)
            return Response(
                {"status": "Failed to log in", "data": user_data},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Logout(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to log out a user.

        Parameters:
            request (Request): The HTTP request object.
            args (list): Positional arguments passed to the function.
            kwargs (dict): Keyword arguments passed to the function.

        Returns:
            Response: The HTTP response object containing the result of the logout operation.
        """
        response_data = {}
        try:
            sessionid = request.data.get("sessionid")
            userid = request.data.get("userid")
            # logout user by delete session id
            Session.objects.filter(session_key=sessionid).delete()
            response_data["status"] = "Logged out successfully"
            print("logout...")
        except Exception as error:
            print(error)
            return Response(
                {"status": "Failed to log out", "data": error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(response_data, status=status.HTTP_200_OK)


class GetUserData(APIView):
    def post(self, request, *args, **kwargs):
        """
        This function handles the HTTP POST request to retrieve user data.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args (tuple): Variable length argument list.
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object containing the retrieved user data or an error message.
        """
        username = kwargs.get("username")
        user_id = User.objects.get(username=username).user_id
        try:
            username, email, full_name, bio, date_joined, avatar = User.objects.get(
                user_id=user_id
            ).getUserData()
            response_data = {}
            response_data["username"] = username
            response_data["email"] = email
            response_data["full_name"] = full_name
            response_data["bio"] = bio
            response_data["date_joined"] = date_joined
            response_data["avatar"] = avatar
            return Response(
                {"status": "Got user data successfully!", "data": response_data},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"status": "error", "data": "This user does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UpdateProfile(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to update a user's profile data.

        Parameters:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object containing the updated profile data.
        """
        username = kwargs.get("username")
        profile_data = request.data
        user_id = User.objects.get(username=username).user_id
        full_name = profile_data["full_name"]
        bio = profile_data["bio"]
        avatar = profile_data["avatar"]
        print("toi duoc cho nay roi")
        try:
            profile = User.objects.get(user_id=user_id).profile
            response_data = {}
            if "https" not in avatar:
                response_data["avatar"] = save_uploaded_file(avatar, username)
                profile.updateAvatar(response_data["avatar"])
            profile.updateName(full_name)
            profile.updateBio(bio)

            response_data["full_name"] = full_name
            response_data["bio"] = bio

            print(response_data)

            return Response(
                {"status": "Updated profile data successfully!", "data": response_data},
                status=status.HTTP_200_OK,
            )
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "data": "This profile does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
