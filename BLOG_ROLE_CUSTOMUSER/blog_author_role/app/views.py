import json
from django.shortcuts import render
from rest_framework.response import Response
from django.http import Http404, HttpResponseRedirect
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .EmailBackend import EmailBackend
from django.shortcuts import redirect
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import jwt
from rest_framework import filters
from django.db import IntegrityError
from rest_framework import generics
from .paginator import CustomPaginationClass
import django_filters
from .TokenGeneration import *
from django.core.mail import EmailMessage
from datetime import datetime

class RegisterView(APIView):
    def get(self, request):
        return Response({"message": """please enter details as follows :{'first_name': 'First name','last_name': 'Last name','email': 'email@gmail.com','password':'XXXXX','role': {'role_user': 1/2/3}"""})

    def post(self, request):
        serializer_user = UserRegistrationSerializer(data=request.data)

        if serializer_user.is_valid():
            try:
                serializer_user.save()
            except AssertionError:
                return Response('You Entered Some Wrong Data, Plase Try Again')
            else:
                return Response(serializer_user.data)
        else:
            return Response(serializer_user.errors)


class LoginView(APIView):
    def get(self,request):
        return Response({"Login Page":"Please Enter Email and Password To Login"})
    
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
        if not email or not password:
            return Response({'Error':'Email or Password Cannot be Blank'})
        else:
            user=EmailBackend.authenticate(request,email=email,password=password)
            if user:
                if user.role_id==1:
                    access_token=get_access_token(user)
                    refresh_token=get_refresh_token(user)
                    login(request,user,backend="app.Emailbackend.EmailBackend")
                    data={'email':user.email,'Role':user.role.name,'refresh':refresh_token,'access':access_token}
                    return Response(data)
                else:
                    if user.role_id==3:
                        access_token=get_access_token(user)
                        refresh_token=get_refresh_token(user)
                        login(request,user,backend="app.Emailbackend.EmailBackend")
                        data={'email':user.email,'Role':user.role.name,'refresh':refresh_token,'access':access_token}
                        return Response(data)

                    else:
                        access_token = get_access_token(user)
                        refresh_token = get_refresh_token(user)
                        data={"Success":"User Page",'email':str(email),'role':str(user.role.name),'refresh': refresh_token,'access': access_token}
                        login(request,user,backend='app.Emailbackend.EmailBackend')
                        return Response(data)
            else:
                return Response({"Error":"User Not Found for Given Credentials"})



class BlogList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = BlogSerializer
    pagination_class = CustomPaginationClass
    
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter]
    
    search_fields = ['author__first_name', 'blog_title']
    
    filterset_fields = ['author', 'blog_title']
    
    ordering_fields = ['blog_title', 'created_at']
    
    def get_queryset(self):
        blog_type = self.request.GET.get('type', None)
        VALID_TYPE=['pending','accepted','rejected']
        if self.request.user.role_id==3:
            if not blog_type:
                return Blog.objects.filter(author=self.request.user.id)
            else:
                if blog_type in VALID_TYPE:
                    return Blog.objects.filter(author=self.request.user.id , type=blog_type)
                else:
                    return Blog.objects.filter(author=self.request.user.id)
        elif self.request.user.role_id== 2:
            return Blog.objects.none()
        else:
            if not blog_type:
                return Blog.objects.all()
            else:
                if blog_type in VALID_TYPE:
                    return Blog.objects.filter(type=blog_type)
                else:
                    return Blog.objects.all()


class UpdateBlogStatus(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        return Response({"Message":"Please Enter Blog ID and status_type to Update"})
    
    def post(self,request):
        if request.user.role_id==1:
            id=request.data.get('id')
            type=request.data.get('type')
            VALID_TYPES=['Pending','Accepted','Rejected']
            if not id or not type:
                return Response({"Error":"Id and Status Type Cannot be Blank"})
            else:
                if type not in VALID_TYPES:
                    return Response({"Error":"Please Enter Valid Status Type"})
                else:
                    obj=Blog.objects.get(id=id)
                    obj.type=type
                    now=datetime.now()
                    dt_string = now.strftime("%d/%B/%Y %H:%M:%S")
                    title=obj.blog_title
                    author_id=obj.author_id
                    obj.save()
                    author=CustomUser.objects.get(id=author_id).email
                    author_name=str(CustomUser.objects.get(id=author_id).first_name) +" "+ str(CustomUser.objects.get(id=author_id).last_name)
                    
                    
                    subject = 'Blog API Status Update'
                    html_message = '<p>Hello {author_name},</p>'.format(author_name=author_name)
                    html_message += '<p> Admin has changed the status of your blog <strong>{blog_title}</strong> to:'.format(blog_title=title)
                    if type=="Rejected":
                        html_message+= '<h3 style="color:red;"> {status} </h3>'.format(status=type)
                    elif type=="Accepted":
                        html_message += '<h3 style="color:green;"> {status} </h3>'.format(
                            status=type)
                    else:
                        html_message += '<h3 style="color:yellow;"> {status} </h3>'.format(
                            status=type)
                    html_message+="<p> Status was Changed at <strong>{time}</strong> </p>".format(time=dt_string)
                    email_from = 'pradyumn.pandey.kumar@gmail.com'
                    recipient_list = [author]
                    email_body = EmailMessage(
                    subject=subject,
                    body=html_message,
                    from_email=email_from,
                    to=recipient_list,
                    )
                    email_body.content_subtype = "html"
                    email_body.send(fail_silently=True)
                    return Response({"Success":"Status Changed"})
        else:
            return Response({"User":"You Cannot Change Status"})


class BookmarkBlogs(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        return Response({"Message":"Enter Blog ID and is_bookmark status To Bookmark/Unbookmark It"})
    def post(self,request):
        if request.user.role_id==2:
            blog_id=request.data.get('id')
            is_bookmark=request.data.get('is_bookmark')
            if not blog_id or not is_bookmark or not is_bookmark:
                return Response({"Error":"Blog ID  or is_bookmark Cannot be Blank"})
            else:
                try:
                    Blog.objects.get(id=blog_id)
                except Blog.DoesNotExist:
                    return Response({"Message":"Blog Not Found"})
                else:
                    if is_bookmark=="True":
                        bookmark = BookMark(blog_id=blog_id, user_id=self.request.user.id, is_bookmark=True)
                        bookmark.save()
                        return Response({"Success":"Blog Bookmarked Successfully"})
                    else:
                        bookmark = BookMark.objects.get(blog_id=blog_id, user_id=self.request.user.id)
                        bookmark.delete()
                        return Response({"Success":"Removed Bookmark"})
        else:
            return Response({"Error":"You Cannot Perform This Action"})


class GiveRatings(APIView):
    permission_classes=[IsAuthenticated]
    def get_blog_details(self,id):
        try:
            obj=Blog.objects.get(id=id)
        except Blog.DoesNotExist:
            raise Http404
        else:
            return obj
    
    def get(self,request):
        return Response({"Message":"Enter Blog Id and Rating to Rate the Blog"})
    
    def post(self,request):
        
        id=request.data.get('id')
        rating=request.data.get('rating')
        
        if not id or not rating:
            return Response({"Error":"ID or Rating cannot be blank"})
        else:
            obj_blog=self.get_blog_details(id)
            if obj_blog.type=="Accepted":
                if rating>5 or rating<1:
                    return Response({"Message":"Please enter Rating from 1-5"})
                else:
                    obj=self.get_blog_details(id)
                    try:
                        rating_instance=Ratings.objects.get(user_id=request.user.id,blog_id=id)
                    except Ratings.DoesNotExist:
                        rating_instance=Ratings(user_id=request.user.id,blog_id=id,rating=rating)
                        rating_instance.save()
                    else:
                        rating_instance.rating=rating
                        rating_instance.save()
                    return Response({"Message":"Ratings Update"})
            else:
                return Response({"Message":"You Cannot Rate this blog"})

# class ViewBookMark(generics.ListAPIView):
    
#     permission_classes=[IsAuthenticated]
#     serializer_class=BookMarkSerializer
#     def get_queryset(self):
#         return BookMark.objects.filter(user_id=self.request.user.id)


class ViewBookMark(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            blogs=BookMark.objects.filter(user_id=request.user.id).values('blog_id')
            #print(blogs,'@@@@@@@@@@@')
            #blogs=BookMark.objects.all()
        except BookMark.DoesNotExist:
            return Response({"Message":"No Data"})
        else:
            user=CustomUser.objects.get(id=request.user.id)
            serializer=UserBookMarkSerializer(user)
            #obj=Blog.objects.filter(id__in=blogs)
            #print(obj,'%%%%%%%%%%%%%%%%%%%%%%')
            #serializer=BlogSerializer(obj,many=True)
            return Response(serializer.data)


class UserViewBlogs(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        if request.user.role_id==2:
            #blogs=Blog.objects.filter(type="Accepted")
            #blog=Blog.objects.filter(id__in=blogs)
            user_data=CustomUser.objects.get(id=request.user.id)
            serializer=UserBlogSerializer(user_data)
            #print(serializer.data[0],'#####')
            return Response(serializer.data)
        else:
            return Response({"Only Users Can Access This Page"})


class AdminBlogView(APIView):
    def get(self, request):
        permission_classes =[IsAuthenticated]
        if request.user.role_id == 1:
            search_keyword=self.request.GET.get('rating',None)
            if not search_keyword:
                return Response(BlogSerializer(Blog.objects.all(),many=True).data)
            else:
                if search_keyword.lower() =='true':
                    blogs=Blog.objects.all()
                    serializer = BlogSerializer(blogs, many=True,context={'type': search_keyword})
                    # serializer = BlogSerializerRatingOnly(blogs, many=True,context={'type': search_keyword})
                    l=[]
                    for i in serializer.data:
                        if i:
                            l.append(i)
                    return Response(l)
                else:
                    blogs = Blog.objects.all()
                    serializer = BlogSerializer(blogs, many=True, context={'type': search_keyword})
                    # serializer = BlogSerializerRatingOnly(blogs, many=True, context={'type': search_keyword})
                    l = []
                    for i in serializer.data:
                        if i:
                            l.append(i)
                    return Response(l)
                    
                return Response()
        else:
            return Response({"You Cannot Access This Page"})