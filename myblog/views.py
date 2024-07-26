
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, get_object_or_404
import re
import requests
from django.db.models import Q
from django.http import HttpResponse
from .models import profileModel
from .models import postcreateModel
from django.urls import reverse


def home(request):
    recent_posts = postcreateModel.objects.order_by('-created_at')[:3]
    return render(request,'index.html',{'recent_posts': recent_posts})



def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email=request.POST['email']
        confirm_password = request.POST['confirm-password']

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Password do not match.")
            return redirect('signup')  # Redirect to signup page

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('signup')  # Redirect to signup page

        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, f"Account created for {username}. You can now login.")
        return redirect('user_login')  # Redirect to login page after successful signup

    return render(request, 'SignUp.html')  # Render the signup.html template for GET requests



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page on successful login
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'Login.html') 




def logout(request):
    auth_logout(request)
    return redirect('home')  # Redirect to the login page



@login_required
def profile(request):
    profile = profileModel.objects.filter(user=request.user).first()
    return render(request, 'ProfilePage.html', {'profile': profile})



@login_required
def createprofile(request):
    # Retrieve the profile if it exists
    profile = profileModel.objects.filter(user=request.user).first()

    if request.method == 'POST':
        bio = request.POST.get('bio')
        image = request.FILES.get('profile_image')

        if profile:
            # Update existing profile
            profile.bio = bio
            if image:
                profile.profile_image = image
            profile.save()
            #messages.success(request, 'Profile updated successfully!')
        else:
            # Create new profile
            profile = profileModel.objects.create(user=request.user, bio=bio, profile_image=image)
            #messages.success(request, 'Profile created successfully!')

        return redirect('profile')  # Redirect to profile page after profile update or creation

    return render(request, 'ProfilePage.html', {'profile': profile})




@login_required
def createpost(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        # Create a new post with the current user
        postcreateModel.objects.create(
            title=title, 
            content=content, 
            image=image, 
            user=request.user 
        )
        #messages.success(request, 'Post created successfully!')
        return redirect('allposts')  # Redirect to home page or wherever appropriate
    posts=postcreateModel.objects.all()
    return render(request, 'CreateEditPost.html',{'posts':posts,'action':'create'})




def allposts(request):
    posts = postcreateModel.objects.all().select_related('user__profile').order_by('-created_at')#Remember
    return render(request, 'Posts.html', {'posts': posts})


@login_required
def editpost(request, pk):
    post = get_object_or_404(postcreateModel, id=pk, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        post.title = title
        post.content = content
        if image:
            post.image = image
        post.save()
        
        return redirect('allposts')  # Assuming you have a view named 'allposts'
    
    return render(request, 'CreateEditPost.html', {'post': post,'action':'edit'})



@login_required
def deletepost(request, pk):
    post = get_object_or_404(postcreateModel, pk=pk, user=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('mypost')  # Assuming you have a view named 'allposts'
    return render(request, 'Posts.html')
    


def readmore(request,pk):
    post = get_object_or_404(postcreateModel, pk=pk) 
    return render(request, 'IndividualBlogPost.html',{'post':post,'action':'readmore'})  



def mypost(request):
    user = request.user  # Fetch the current authenticated user
    posts = postcreateModel.objects.filter(user=user)  # Filter posts by the current user
    return render(request, 'IndividualBlogPost.html',{'posts':posts,'action':'mypost'}) #Remember to add comma in value




@login_required
def delete_profile(request):
    user = request.user

    if request.method == 'POST':
        

        # Attempt to get and delete the associated profile
        try:
            profile = profileModel.objects.get(user=user)
            
            # Delete the profile image if it exists
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            
            profile.delete()  # Delete the profile instance
            
        except profileModel.DoesNotExist:
            # Profile does not exist, continue
            pass

        # Delete the user
        user.delete()
        #messages.success(request, "Your profile has been deleted successfully.")
        return redirect(reverse('home'))  # Redirect to a home or login page

    return redirect('createprofile') 






def search_results(request):
    query = request.GET.get('query', '')
    context = {'search_query': query}

    if query and len(query)>2:
        # Split the query into individual keywords
        keywords = query.lower().split()
        
        # Build the query conditions using Q objects
        query_conditions = Q()
        for keyword in keywords:
            query_conditions |= Q(title__icontains=keyword) | Q(content__icontains=keyword)

        # Filter posts based on the query conditions
        posts = postcreateModel.objects.filter(query_conditions)
        
        if posts.exists():
            context['search_results'] = posts
        else:
            # If no posts are found, search for Ghibli information via API
            response = requests.get(f'https://ghibliapi.herokuapp.com/films')
            if response.status_code == 200:
                data = response.json()
                context['api_results'] = [film for film in data if query.lower() in film['title'].lower() or query.lower() in film['description'].lower()]
            else:
                context['api_results'] = []

    return render(request, 'search_results.html', context)
