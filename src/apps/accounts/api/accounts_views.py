import jwt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
)
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from apps.accounts.models import User
from apps.accounts.api.serializers import (
    UserProfileSerializer,
    UserSerializer,
)

######## Start Dashboard Api ############


class UserProfileAPIView(generics.RetrieveAPIView):
    """
    Endpoint to retrieve user profile.

    """

    permission_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)
    # serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        return self.request.user.userprofile


######## End Dashboard Api ############


class WalletCharge(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.POST.get("amount")


@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(["GET"])
def get_user_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "user does not exists"},
            status=status.HTTP_404_NOT_FOUND,
            exception=True,
        )

    serializer = UserSerializer(user, many=False, context={"request": request})

    # following = False
    # if request.user in user.followers.all():
    #     following = True

    return Response(
        {
            "data": serializer.data,
            "is_out_profile": request.user.username == user.username,
            # "following": following,
        }
    )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("unauthenticated")

        try:
            payload = jwt.decode(token, "secret", algorithm="HS256")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("un authenticate")

        user = User.objects.get(id=payload["id"])
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def user_profile_update(request):
    data = request.data
    try:
        user = User.objects.get(username=request.data["username"])
    except User.DoesNotExist:
        return Response({"error": "user does not exists"})

    serializer = UserProfileSerializer(user, data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({**serializer.data, "success": True})
    return Response({**serializer.error, "success": False})


# class UserChangePasswordAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, format=None):
#         serializer = UserChangePasswordSerializer(data=request.data)
#         context = {'user': request.user, 'msg': 'password changed'}
#         if serializer.is_valid(raise_exception=True):
#             return Response(context, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GetTokenView(APIView):
#     def post(self, request):
#         mobile = request.data.get('mobile')
#         code = request.data.get('code')
