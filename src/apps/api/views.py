import datetime
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import NotAcceptable, AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from apps.api.renderers import UserRenderer

# from apps.blog.documents import PostDocument
from apps.blog.models import Category, Post, Tag
from apps.blog.serializers import (
    CategoryTreeSerializer,
    CreateCategoryNodeSerializer,
    PostSerializer,
    CategorySerializer,
    TagSerializer,
)


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
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


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


# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token)
#     }


# class UserRegisterView(APIView):
#     def post(self, request):
#         serializer = UserRegisterSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             user = serializer.save()
#             token = get_tokens_for_user(user)
#             context = {
#                 'token': token,
#                 'user': user,
#                 'message': 'registration is successful'
#             }
#             return Response(context, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserLoginView(APIView):
# renderer_classes = [UserRenderer]

# #     def post(self, request):
# #         serializer = UserLoginSerializer(data=request.data)
# #         if serializer.is_valid(raise_exception=True):
# #             email = serializer.data.get('email')
# #             password = serializer.data.get('password')
# #             user = authenticate(email=email, password=password)
# #             if user is not None:
# #                 token = get_tokens_for_user(user)
# #                 context = {'user': user, 'token': token,
# #                            'msg': 'login successful'}
# #                 return Response(context, status=status.HTTP_200_OK)
# #             else:
# #                 return Response('email or password is wrong', status=status.HTTP_404_NOT_FOUND)

# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     renderer_classes = [UserRenderer]

# #     def post(self, request):
# #         email = request.data['email']
# #         password = request.data['password']

# #         user = User.objects.get(email=email)
# #         if user is None:
# #             raise AuthenticationFailed('user not found')

# #         if not user.check_password(password):
# #             raise AuthenticationFailed('password wrong')

# #         payload = {
# #             'id': user.id,
# #             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=50),
# #             'iat': datetime.datetime.utcnow()
# #         }

# #         # PyJwt
# #         token = jwt.encode(payload, 'secret',
# #                            algorithm='HS256').decode('utf-8')

# #         response = Response()
# #         response.set_cookie(key='jwt', value=token, httponly=True)
# #         response.data = {
# #             'jwt': token
# #         }
# #         return response


# # class UserProfileView(APIView):
#     renderer_classes = [UserRenderer]
# #     permission_classes = [IsAuthenticated]

# #     def get(self,  request, format=None):
# #         token = request.COOKIES.get('jwt')

# #         if not token:
# #             raise AuthenticationFailed('unauthenticate')

# #         try:
# #             payload = jwt.decode(token, 'secret', algorithm='HS256')
# #         except jwt.ExpiredSignatureError:
# #             raise AuthenticationFailed('un authenticate')

# #         user = User.objects.get(id=payload['id'])
# #         serializer = UserProfileSerializer(user)
# #         return Response(serializer.data)


# # class UserLogoutView(APIView):
# #     def post(self, request):
# #         response = Response()
# #         response.delete_cookie('jwt')
# #         response.data = {'message': 'logout'}
# #         return Response(response)


# # class UserForgotPasswordAPIView(APIView):
# #     def post(self, request):
# #         serializer = UserForgotPasswordSerializer(data=request.data)
# #         if serializer.is_valid(raise_exception=True):
# #             return Response({'msg': 'password reset link sent'}, status=status.HTTP_200_OK)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # class UserPasswordResetAPIView(APIView):
# #     def post(self, request, uid, token):
# #         serializer = UserPasswordSerializer(data=request.data)
# #         context = {'uid': uid, 'token': token}
# #         if serializer.is_valid(raise_exception=True):
# #             return Response({'msg': 'password reset successfully'})
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # class UserChangePasswordAPIView(APIView):
#     renderer_classes = [UserRenderer]
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, format=None):
# #         serializer = UserChangePasswordSerializer(data=request.data)
# #         context = {'user': request.user, 'msg': 'password changed'}
# #         if serializer.is_valid(raise_exception=True):
# #             return Response(context, status=status.HTTP_200_OK)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # class GetTokenView(APIView):
# #     def post(self, request):
# #         mobile = request.data.get('mobile')
# #         code = request.data.get('code')


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
