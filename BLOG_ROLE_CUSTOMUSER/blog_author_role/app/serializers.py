
from .models import Blog, BookMark, CustomUser,Ratings
from .models import Role
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from django.contrib.auth.hashers import make_password


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_user']

class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = RoleSerializer()

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data['role']
        role = role['role_user']
        if role == 1:
            user = CustomUser.objects.create(
                email=validated_data['email'], first_name=validated_data['first_name'], last_name=validated_data['last_name'], role_id=role)
            user.set_password(validated_data['password'])
            user.save()
            return user
        elif role == 2:
            user = CustomUser.objects.create(
                email=validated_data['email'], first_name=validated_data['first_name'], last_name=validated_data['last_name'], role_id=role, is_active=True)
            user.set_password(validated_data['password'])
            user.save()
            return user
        elif role == 3:
            user = CustomUser.objects.create(
                email=validated_data['email'], first_name=validated_data['first_name'], last_name=validated_data['last_name'], role_id=role, is_active=True)
            user.set_password(validated_data['password'])
            user.save()
            return user
        else:
            return None


class BlogRatingSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    # user=UserSerializer()
    class Meta:
        model=Ratings
        fields = ['name', 'rating']
        
    def get_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

class BlogSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    rating_list = serializers.SerializerMethodField()
    average_rating=serializers.SerializerMethodField()
    def get_author(self,obj):
        #print(obj,"%%%%%%")
        return (obj.author.first_name + " " +obj.author.last_name)
    class Meta:
        model=Blog
        fields = ['id', 'author', 'blog_title', 'blog_description','blog_image', 'created_at', 'type', 'rating_list','average_rating']
        
    def get_rating_list(self, obj):
        try:
            #print(self.data,'****')
            ratting = Ratings.objects.filter(blog_id=obj.id)
            
            if ratting:
                return BlogRatingSerializer(ratting, many=True).data
            else:
                return []
        except Ratings.DoesNotExist:
            return []
    
    def get_average_rating(self,obj):
        try:
            ratings=Ratings.objects.filter(blog_id=obj.id)
            if ratings:
                sum=0
                for points in ratings:
                    sum+=points.rating
                return sum/len(ratings)
            else:
                return 0
        except Ratings.DoesNotExist:
            return 0

    def to_representation(self, instance):
        if self.context.get('type') == 'true':
            data = super(BlogSerializer,self).to_representation(instance)
            if data.get('rating_list'):
                if len(data.get('rating_list')) > 0:
                    return data
                else:
                    return
            else:
                return
        elif self.context.get('type') == 'false':
            data = super(BlogSerializer,self).to_representation(instance)
            if not data.get('rating_list'):
                return data
            else:
                return



class BlogSerializer2(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    blog_image=serializers.SerializerMethodField()
    def get_author(self, obj):
        #print(obj,"%%%%%%")
        return (obj.author.first_name + " " + obj.author.last_name)

    class Meta:
        model = Blog
        fields = ['id', 'author', 'blog_title', 'blog_description','blog_image', 'created_at', 'type', 'ratings', 'average_rating']

    def get_blog_image(self,obj):
        return "http://127.0.0.1:8000"+obj.blog_image.url
    def get_ratings(self, obj):
        try:
            #print(Ratings.objects.get(blog_id=obj.id,user_id=self.context.get('id')),'^^^^^^^^^^^^^^^^^^^^^^^')
            rating = Ratings.objects.filter(blog_id=obj.id, user_id=self.context.get('id'))
        except Ratings.DoesNotExist:
            return 0
        else:
            if not rating:
                return 0
            else:
                return Ratings.objects.filter(blog_id=obj.id, user_id=self.context.get('id')).values_list('rating', flat=True).first()

    def get_average_rating(self, obj):
        try:
            ratings = Ratings.objects.filter(blog_id=obj.id)
            if ratings:
                sum = 0
                for points in ratings:
                    sum += points.rating
                return sum/len(ratings)
            else:
                return 0
        except Ratings.DoesNotExist:
            return 0


class UserBlogSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    role=serializers.SerializerMethodField()
    blog_list=serializers.SerializerMethodField()
    class Meta:
        model=CustomUser
        fields=['id', 'name','role', 'blog_list']
    
    def get_id(self,obj):
        return obj.id
    def get_name(self,obj):
        return obj.first_name + " " + obj.last_name
    def get_role(self,obj):
        return obj.role.name
    def get_blog_list(self,obj):
        blogs=Blog.objects.filter(type='Accepted')
        blog=Blog.objects.filter(id__in=blogs)
        #print(blog,'&&&&&&&&')
        return BlogSerializer2(blog, context={'id': obj.id},many=True).data

class UserBookMarkSerializer(serializers.ModelSerializer):
    id=serializers.SerializerMethodField()
    name=serializers.SerializerMethodField()
    blog_list=serializers.SerializerMethodField()
    class Meta:
        model=CustomUser
        fields=['id','name','blog_list']
    def get_id(self,obj):
        return obj.id
    def get_name(self,obj):
        return obj.first_name + " " + obj.last_name
    def get_blog_list(self,obj):
        blogs=BookMark.objects.filter(user_id=obj.id).values('blog_id')
        blog=Blog.objects.filter(id__in=blogs)
        return BlogSerializer2(blog,context={'id':obj.id},many=True).data


class BlogSerializerRatingOnly(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    blog_image = serializers.SerializerMethodField()

    def get_author(self, obj):
        #print(obj,"%%%%%%")
        return (obj.author.first_name + " " + obj.author.last_name)

    class Meta:
        model = Blog
        fields = ['id', 'author', 'blog_title', 'blog_description','blog_image', 'created_at', 'type', 'ratings', 'average_rating']

    def get_blog_image(self, obj):
        return "http://127.0.0.1:8000"+obj.blog_image.url

    def get_ratings(self, obj):
        try:
            #print(self.data,'****')
            ratting = Ratings.objects.filter(blog_id=obj.id)

            if ratting:
                return BlogRatingSerializer(ratting, many=True).data
            else:
                return []
        except Ratings.DoesNotExist:
            return []

    def get_average_rating(self, obj):
        try:
            ratings = Ratings.objects.filter(blog_id=obj.id)
            if ratings:
                sum = 0
                for points in ratings:
                    sum += points.rating
                return sum/len(ratings)
            else:
                return 0
        except Ratings.DoesNotExist:
            return 0

    def to_representation(self,instance):
        if self.context.get('type')=='true':
            data=super(BlogSerializerRatingOnly,self).to_representation(instance)
            if len(data.get('ratings'))>0:
                return data
            else:
                return
        elif self.context.get('type')=='false':
            data = super(BlogSerializerRatingOnly,self).to_representation(instance)
            if len(data.get('ratings'))==0:
                return data
            else:
                return
