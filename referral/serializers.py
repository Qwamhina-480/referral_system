from rest_framework import serializers
from .models import User, Reward
import re, phonenumbers, random
from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['points', 'reason', 'created_at']

class SignupSerializer(serializers.ModelSerializer):
    contact = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'contact', 'password', 'referral_code']

    def validate(self, data):
        contact = data.get('contact')
        if not contact:
            raise serializers.ValidationError("Contact is required.")

        if '@' in contact:
        # Validate the email structure
            try:
                validate_email(contact)
                data['email'] = contact.lower()
            except DjangoValidationError:
                raise serializers.ValidationError("Invalid email address.")
        else:
            # Assume it's a phone number
            try:
                parsed_number = phonenumbers.parse(contact, "GH")  # Ghana-specific parsing
                if not phonenumbers.is_valid_number(parsed_number):
                    raise serializers.ValidationError("Invalid phone number.")
                formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                data['phone_number'] = formatted_number
            except phonenumbers.NumberParseException:
                raise serializers.ValidationError("Invalid phone number format.")

        return data

    def create(self, validated_data): 
        contact = validated_data.pop('contact', None)
        password = validated_data.pop('password')
        referral_code = validated_data.pop('referral_code', None)
        ip_address = validated_data.pop('ip_address', None)
        referrer = None

        # Get referrer from referral_code
        if referral_code:
            referrer = User.objects.filter(referral_code=referral_code).first()

        # Create user instance
        user = User(**validated_data)

        # Assign contact properly
        if contact:
            if '@' in contact:
                user.email = contact
            else:
                user.phone_number = contact

        user.set_password(password)

        if ip_address:
            user.ip_address = ip_address
        if referrer:
            user.referrer = referrer

        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    contact = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        contact = data.get('contact')
        password = data.get('password')

        user = User.objects.filter(
            models.Q(email=contact) | models.Q(phone_number=contact)
        ).first()

        if not user:
            raise serializers.ValidationError("User not found.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password.")

        if not user.is_verified:
            raise serializers.ValidationError("Please verify your account before logging in.")

        data['user'] = user
        return data
    


class UserSerializer(serializers.ModelSerializer):
    total_points = serializers.IntegerField(read_only=True)
    referral_count = serializers.IntegerField(read_only=True)
    referral_link = serializers.CharField(source='get_referral_link', read_only=True)
   


    class Meta:
        model = User
        fields = ['id', 'email','contact', 'username', 'referral_code', 'referrer', 'referral_link','ip_address', 'created_at', 'total_points', 'referral_count']

        def get_referral_link(self, obj):
            return obj.get_referral_link()

class CreateReferralSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    ip_address = serializers.IPAddressField()
    referrer_code = serializers.CharField(max_length=10)


class UserDashboardSerializer(serializers.ModelSerializer):
    total_points = serializers.SerializerMethodField()
    referral_link = serializers.SerializerMethodField()
    rewards = serializers.SerializerMethodField()
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'referral_code', 'referral_link', 'total_points', 'rewards', 'referrals']

    def get_total_points(self, obj):
        return obj.total_points()

    def get_referral_link(self, obj):
        return obj.get_referral_link()

    def get_rewards(self, obj):
        return [
            {
                'points': reward.points,
                'reason': reward.reason,
                'date': reward.created_at.strftime('%Y-%m-%d')
            }
            for reward in obj.rewards.all()
        ]

    def get_referrals(self, obj):
        return [
            {
                'username': referral.username,
                'joined': referral.created_at.strftime('%Y-%m-%d')
            }
            for referral in obj.referrals.all()
        ]
