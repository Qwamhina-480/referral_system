from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Sum, Q, Count
from .models import User, Reward
from .serializers import UserSerializer, SignupSerializer, LoginSerializer
from .serializers import UserDashboardSerializer
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.contrib.auth import authenticate, login, logout
import requests
from django.db import models
from rest_framework.views import APIView
from django.contrib import messages



# Create your views here.
class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        contact = validated.get("contact")
        username = validated.get("username")
        referrer_code = validated.get("referral_code")

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        # Check for duplicate contact
        if User.objects.filter(Q(email=contact) | Q(phone_number=contact)).exists():
            return Response({"detail": "This contact (email or phone) has already been used."}, status=400)

       
        # Resolve referrer before saving
        referrer = User.objects.filter(referral_code=referrer_code).first() if referrer_code else None

        # Check for fraud
       # fraud_detected = User.objects.filter(ip_address=ip_address, referrer=referrer).exists()
        fraud_detected = False


        # Save the user (serializer handles password, contact, referrer)
        user = serializer.save()
        user.ip_address = ip_address
        user.referrer = referrer
        user.save()

        # Apply rewards
        if referrer:
            Reward.objects.create(user=user, points=2, reason="Signed up using a referral code")

            if not fraud_detected:
                Reward.objects.create(user=referrer, points=10, reason="Referred a new user")

                if referrer.referrer:
                    Reward.objects.create(
                        user=referrer.referrer,
                        points=5,
                        reason="Indirect referral (grandparent reward)"
                    )

        return Response({
            "message": "User created successfully.",
            "username": user.username,
            "referral_code": user.referral_code,
            "referral_link": user.get_referral_link(),
            "total_points": user.total_points()
        }, status=status.HTTP_201_CREATED)
    

"""
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Optional: Use JWT instead
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Login successful.',
            'token': token.key,
            'username': user.username,
            'referral_code': user.referral_code,
        })

"""
class CheckPointsView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'referral_code'
    lookup_url_kwarg = 'referral_code'

class LeaderboardView(APIView):
    def get(self, request):
        leaders = User.objects.all().order_by('-rewards__points').distinct()[:5]  # You can filter top 5 here if needed

        data = [
            {
                "username": user.username,
                "referral_code": user.referral_code,
                "total_points": user.total_points()
            }
            for user in leaders
        ]
        return Response(data)
    

class UserDashboardView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDashboardSerializer
    lookup_field = 'referral_code'  

class ReferralRedirectView(View):
    def get(self, request, referral_code):
        # Optional: check if referral code exists
        user = get_object_or_404(User, referral_code=referral_code)

        # Redirect to signup page with referral code in query
        return redirect(f'/signup?referrer_code={referral_code}')



def admin_dashboard(request):
    rewards = Reward.objects.all().order_by('-created_at')
    users = User.objects.annotate(referral_count=Count('referrals'),  # reverse FK from User to User (referrer)
    total_points=Sum('rewards__points')).order_by('-rewards__points') # reverse FK from User to Reward
    user_count = User.objects.count()
    
    return render(request, 'referral/admin_dashboard.html', {'users': users, 'rewards': rewards, 'user_count':user_count})

"""
def user_dashboard(request, referral_code):
    user = get_object_or_404(User, referral_code=referral_code)

    # Get all users ordered by total points
    all_users = sorted(User.objects.all(), key=lambda u: u.total_points(), reverse=True)

    # Calculate user rank (index + 1)
    user_rank = next((i + 1 for i, u in enumerate(all_users) if u.id == user.id), None)

    # Get user rewards
    rewards = Reward.objects.filter(user=user).order_by('-created_at')

    return render(request, 'referral/user_dashboard.html', {
        'user': user,
        'rewards': rewards,
        'user_rank': user_rank,
        'total_users': len(all_users),
        'referral_link': f"http://127.0.0.1:8000/ref/{user.referral_code}/",
    })
"""
def user_dashboard(request, referral_code):
    api_url = f'http://127.0.0.1:8000/points/{referral_code}/'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
    else:
        data = {'error': 'Could not fetch user data'}
    user = get_object_or_404(User, referral_code=referral_code)

    # Get rewards related to this user
    rewards = Reward.objects.filter(user=user)

    # Get all referred users
    referred_users = user.referrals.count()

    # Calculate rank
    users = list(User.objects.all())
    users.sort(key=lambda u: u.total_points(), reverse=True)
    user_rank = users.index(user) + 1
    leaders = User.objects.annotate(total_points=Sum('rewards__points')).order_by('-total_points')[:5]


    data = {
        'username': user.username,
        'referral_code': user.referral_code,
        'referral_link': user.get_referral_link(),
        'total_points': user.total_points(),
        'direct_referrals': referred_users,
        'rewards': rewards,
        'referred_users': referred_users,
        'user_rank': user_rank,
        'contact' : user.email if user.email else user.phone_number,
    }


    return render(request, 'referral/user_dashboard.html', {'user_data': data, 'leaders':leaders})


def leaderboard_html(request):
    try:
        response = requests.get('http://127.0.0.1:8000/leaderboard/')
        data = response.json()
        return render(request, 'referral/leaderboard.html', {'leaders': data})
    except Exception as e:
        print("Error fetching leaderboard:", e)
        return render(request, 'referral/leaderboard.html', {'leaders': []})
    
API_BASE = "http://127.0.0.1:8000"

def signup_html(request):
    if request.method == "POST":
        username = request.POST.get("username")
        contact = request.POST.get("contact")
        password = request.POST.get("password")
        referral_code = request.POST.get("referral_code")

        # Check if user exists
        if User.objects.filter(email=contact).exists():
            return render(
                request,
                "referral/signup.html",
                {"error": "User already exists. Please log in."},
            )

        # Register via API
        try:
            data = {
            "username": username,
            "contact": contact,
            "password": password,
            "referral_code": referral_code,
            }
            res = requests.post(f"{API_BASE}/referral/", data=data)

            if res.status_code == 201:
                user = User.objects.get(username=username)
                login(request, user)
                return redirect("user-dashboard", referral_code=user.referral_code)
            else:
                error_data = res.json()
        
                # Handle "detail" key or full serializer error dict
                if "detail" in error_data:
                    error_message = error_data["detail"]
                else:
                    # Join multiple field errors into a single string
                    error_list = []
                for field, messages in error_data.items():
                    error_list.append(f"{', '.join(messages)}")
            error_message = " ".join(error_list)

            return render(request, "referral/signup.html", {"error": error_message})
        except Exception:
            return render( request, "referral/signup.html", {"error": "API error. Please try again."})
    referral_code = request.GET.get("ref", "")
    return render(request, "referral/signup.html",{'referral_code': referral_code})





def login_html(request):  # Note: Renamed to avoid conflict with Django's login()
    if request.method == "POST":
        contact = request.POST.get("contact")  # Email or phone
        password = request.POST.get("password")

        # Find user by email or phone
        user = (
            User.objects.filter(email=contact).first()
            or User.objects.filter(phone_number=contact).first()
        )

        if user:
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                login(request, auth_user)
                return redirect("user-dashboard", referral_code=user.referral_code)
            else:
                return render(
                    request,
                    "referral/login.html",
                    {"error": "Incorrect password."},
                )
        else:
            return render(
                request,
                "referral/login.html",
                {"error": "User not found. Please sign up."},
            )

    return render(request, "referral/login.html")

def logout_html(request):
    logout(request)
    return redirect("login")


def landing_html(request):
    return render(request, "referral/landingpage.html")


def delete(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('signup')  # Replace 'home' with the actual name of your homepage URL
    return redirect('profile') 