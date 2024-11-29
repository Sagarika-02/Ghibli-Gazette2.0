
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

#For password Reset feature
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.template.loader import render_to_string
from django.core.mail import send_mail,EmailMessage
from django.contrib import messages
from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError  # Add this import
from datetime import timedelta,datetime
from django.utils.timezone import now
from django.conf import settings







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
        user = User.objects.create_user(username=username,  email=email, password=password)
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

        # Check if bio and image are provided, and handle missing data
        if not bio or not image:
            # Handle case where either bio or image is missing
            error_message = "Both bio and profile image are required."
            # Optionally, you can use Django's messages framework to display this error message
            return render(request, 'ProfilePage.html', {'profile': profile, 'error_message': error_message})

        if profile:
            # Update existing profile
            profile.bio = bio
            profile.profile_image = image
            profile.save()
        else:
            # Create new profile
            profile = profileModel.objects.create(user=request.user, bio=bio, profile_image=image)

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








#Password Reset through rate limt and Time bounded Token sent in respective email

#(1)Linke Expiry: This defines that the reset link will expire in 3 minutes after it is generated.
PASSWORD_RESET_TIMEOUT = timedelta(minutes=6)

def rate_limit(request, email=None):
    ip = request.META.get('REMOTE_ADDR')
    
#(2)Rate Limit:This part ensures that a user can only make 3 requests per hour from the same IP address. If the user has exceeded 3 requests, they will be blocked for the next hour.

    # IP rate limiting
    attempts = cache.get(ip, 0)
    if attempts >= 3:
        return "Too many requests from this IP. Try again later."
    
    # Set rate limit for IP
    cache.set(ip, attempts + 1, timeout=3600)  # Timeout set to 1 hour that is one can not make a new request for next 1 hour



#(3)Email-based Flood Prevention:This section ensures that the user can only make a reset request once every 5 minutes using the same email. If they try again before 5 minutes, they must wait 1 hour (as defined by the 1-hour cache timeout) before making another request.

    if email:
        # Check last reset request for email within 5 minutes
        last_request_time = cache.get(f"last_reset_request_{email}")
        if last_request_time:
            if datetime.now() - last_request_time < timedelta(minutes=5):  # One request per 5 minutes
                return "Too many reset requests from this email. Please try again later."
        
        # Set the last request time for this email
        cache.set(f"last_reset_request_{email}", datetime.now(), timeout=3600)  # Store last request time (1 hour timeout)

    return None



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check for rate limit security
        rate_limit_message = rate_limit(request, email=email)
        if rate_limit_message:
            messages.error(request, rate_limit_message)
            return redirect('forgot_password')

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

        
            # Convert PASSWORD_RESET_TIMEOUT to seconds
            timeout_seconds = PASSWORD_RESET_TIMEOUT.total_seconds()

            # Set expiration time for the reset link (3 minutes)
            reset_link_expiry = datetime.now() + PASSWORD_RESET_TIMEOUT
            cache.set(f"reset_link_{uid}", reset_link_expiry, timeout=timeout_seconds)

            # Generate the password reset URL
            reset_url = reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
            reset_url = request.build_absolute_uri(reset_url)

            # Send email with reset link
            subject = "Password Reset Request"
            message = render_to_string('password_reset_email.html', {
                'reset_url': reset_url,
                'user': user,
            })
            
             # Create an EmailMessage instance with proper headers
            email_message = EmailMessage(
                subject,  # Email subject
                message,  # Email message body
                'no-reply@example.com',  # Sender's email address (no-reply)
                [user.email],  # Recipient's email
            )

            # Set the "From" header explicitly with sender name as 'noreply'
            email_message.extra_headers = {
                'From': 'noreply <no-reply@example.com>',  # This will show 'noreply' in the From field
                'Reply-To': 'no-reply@example.com',  # Ensures that the user cannot reply to this email
            }

            # Send the email
            email_message.send()



            messages.success(request, "Password reset link sent to your email.")
            return redirect('forgot_password')
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return render(request, 'check_email.html')

    return render(request, 'check_email.html')




def reset_password(request, uidb64, token):
    try:
        # Decode the uidb64 to get the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Check for token expiration
        reset_link_expiry = cache.get(f"reset_link_{uidb64}")
        if reset_link_expiry is None or datetime.now() > reset_link_expiry:
            messages.error(request, "The reset link has expired.")
            return redirect('forgot_password')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Validate the token
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new-password')
            confirm_password = request.POST.get('confirm-password')
            
            # Check if the passwords match
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'resetPW.html', {'uidb64': uidb64, 'token': token})

            try:
                validate_password(new_password, user)
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset.")
                return redirect('user_login')  # Redirect to login page after successful password reset
            except ValidationError as e:
                messages.error(request, ", ".join(e.messages))
                return render(request, 'resetPW.html', {'uidb64': uidb64, 'token': token})

        return render(request, 'resetPW.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, "The reset link is invalid or expired.")
        return redirect('forgot_password')
