import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import io

# from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")

from Model.main import Txt2Img

# Load the environment variables from the .env file

load_dotenv()

genObj = Txt2Img()

# Init firebase with your credentials


class GenerateImage(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Parse input data
            prompt_data = request.data
            prompt = prompt_data.get("prompt")
            print("prompt: ", prompt)

            if not prompt or not prompt.strip():
                return Response(
                    {"detail": "Prompt cannot be empty."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Generate the image
            ans = genObj.generate_image(
                prompt
            )  # Assuming this function returns the image as binary data.
            print("Done!")

            # Prepare the image data for response
            image_data = io.BytesIO(ans)  # Wrap the binary image in a BytesIO buffer

            # Send the image response
            response = HttpResponse(image_data.getvalue(), content_type="image/png")
            response['Content-Disposition'] = f'attachment; filename="{hash(prompt)}.png"'
            return response

        except KeyError as e:
            return Response(
                {"detail": f"Missing key: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
