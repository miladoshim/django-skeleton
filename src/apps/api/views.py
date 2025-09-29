import datetime
from django.contrib import auth
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import NotAcceptable
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from apps.accounts.serializers import (
    ObtainTokenSerializer,
    RequestOTPSerialize,
    VerifyOTPSerialize,
)
from apps.accounts.models import OtpRequest, User
from apps.api.pagination import CustomPagination
from apps.api.renderers import UserRenderer

# from apps.blog.documents import PostDocument
from apps.api.serializers import (
    UserForgotPasswordSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserResetPasswordSerializer,
)
from apps.blog.models import Category, Post, Tag
from apps.blog.serializers import (
    CategoryTreeSerializer,
    CreateCategoryNodeSerializer,
    PostSerializer,
    CategorySerializer,
    TagSerializer,
)

from utils.helpers import Helpers


class TagViewSet(ReadOnlyModelViewSet):
    """
    Return a list of all tags
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostViewSet(ReadOnlyModelViewSet):
    """
    Return a list of all blog posts
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostSearch(APIView):
    serializer_class = PostSerializer
    # document_class = PostDocument

    def generate_q_expression(self, query):
        return Q("match", name={"query": query, "fuzziness": "auto"})

    def get(self, request, query):
        q = self.generate_q_expression(query)
        search = self.document_class.search().query(q)
        return Response(self.serializer_class(search.to_queryset(), many=True).data)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryTreeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = Helpers.get_tokens_for_user(user)
            context = {
                "token": token,
                "user": user,
                "message": "registration is successful",
            }
            return Response(context, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RegisterView(APIView):
#     def post(self, request):
#         mobile = request.data.get('mobile')
#         if not mobile:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         user, created = User.objects.get_or_create(mobile=mobile)
#         if not created:
#             return Response({'data': 'user registered'}, status=status.HTTP_400_BAD_REQUEST)

#         code = random.randint(10000, 99999)

#         # send sms

#         return Response({'code': code})


class UserLoginView(GenericAPIView):
    renderer_classes = [UserRenderer]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)


# class UserProfileView(APIView):
# renderer_classes = [UserRenderer]
#     permission_classes = [IsAuthenticated]

#     def get(self,  request, format=None):
#         token = request.COOKIES.get('jwt')

#         if not token:
#             raise AuthenticationFailed('unauthenticate')

#         try:
#             payload = jwt.decode(token, 'secret', algorithm='HS256')
#         except jwt.ExpiredSignatureError:
#             raise AuthenticationFailed('un authenticate')

#         user = User.objects.get(id=payload['id'])
#         serializer = UserProfileSerializer(user)
#         return Response(serializer.data)


class UserLogoutView(GenericAPIView):
    # serializer_class = UserLogoutSerializer
    permission_classes = IsAuthenticated

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("logout", status=status.HTTP_204_NO_CONTENT)


class UserForgotPasswordAPIView(GenericAPIView):
    serializer_class = UserForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "password reset link sent"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetAPIView(GenericAPIView):
    serializer_class = UserResetPasswordSerializer

    def post(self, request, uid, token):
        serializer = self.serializer_class(data=request.data)
        context = {"uid": uid, "token": token}
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "password reset successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserGoogleOAuthAuthAPIView(GenericAPIView):
    pass


# class UserChangePasswordAPIView(APIView):
# renderer_classes = [UserRenderer]
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


def search(request):
    if request.method == "POST":
        query = request.POST.get("q")
        if query:
            query_for_search = SearchQuery(query)
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "body", weight="B"
            )
            search_rank = SearchRank(search_vector, query_for_search)
            posts = (
                Post.objects.published.annotate(search=search_vector, rank=search_rank)
                .filter(search=query_for_search)
                .order_by("-rank")
            )
            return Response({"posts": posts})


class OTPView(APIView):
    def get(self, request):
        serializer = RequestOTPSerialize(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                otp = OtpRequest.objects.generate(data)
            except Exception as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = VerifyOTPSerialize(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if OtpRequest.objects.is_valid(
                data["receiver"], data["request_id"], data["password"]
            ):
                return Response(self._handle_login(data))
            else:
                pass
        else:
            pass

    def _handle_login(self, otp):
        userModel = User
        query = userModel.objects.filter(username=otp["receiver"])
        if query.exits():
            created = False
            user = query.first()
        else:
            user = User.objects.create(username=otp["receiver"])
            created = True
        refresh = RefreshToken.for_user(user)
        return ObtainTokenSerializer(
            {
                "refresh": str(refresh),
                "token": str(refresh.access_token),
                "created": created,
            }
        ).data


class OncePerMinuteThrottle(UserRateThrottle):
    rate = "1/minute"


class RequestOtpAPIView(APIView):

    # throttle_classes = [OncePerMinuteThrottle]

    def post(self, request):
        serializer = RequestOtpSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data["mobile"]
            channel = serializer.validated_data["channel"]
            otp_request = OtpRequest(mobile=mobile, channel=channel)
            otp_request.generate_otp()
            otp_request.save()

            # Send sms

            return Response(RequestOtpResponseSerializer(otp_request).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpAPIView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            request_id = serializer.validated_data["request_id"]
            mobile = serializer.validated_data["mobile"]
            password = serializer.validated_data["password"]

            otp_request = OtpRequest.objects.filter(
                request_id=request_id, mobile=mobile, valid_until__gte=timezone.now()
            )
            if otp_request.exists():
                userq = User.objects.filter(mobile=mobile)
                if userq.exists():
                    user = userq.first()
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({"token": token, "new_user": False})
                else:
                    user = User.objects.create(mobile=mobile)
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({"token": token, "new_user": True})

            else:
                return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
