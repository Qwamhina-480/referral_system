from django.contrib import admin
from .models import User, Reward
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.


class UserAdmin(BaseUserAdmin):  # ✅ Inherit from BaseUserAdmin
    list_display = (
        'username',
        'email',
        'ip_address',
        'referral_code',
        'referrer_username',
        'referral_count',
        'total_points_display',
        'latest_reward_reason',
        'date_joined',
    )
    
    search_fields = ('username', 'email', 'referral_code')
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone_number', 'password')}),
        ('Referral Info', {'fields': ('referral_code', 'referrer', 'ip_address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def total_points_display(self, obj):
        return obj.total_points()
    total_points_display.short_description = 'Total Points'

    def referrer_username(self, obj):
        return obj.referrer.username if obj.referrer else '-'
    referrer_username.short_description = 'Referrer'

    def referral_count(self, obj):
        return obj.referrals.count()
    referral_count.short_description = 'Referrals'

    def latest_reward_reason(self, obj):
        latest = obj.rewards.order_by('-created_at').first()
        return latest.reason if latest else '-'
    latest_reward_reason.short_description = 'Latest Reward'

class RewardAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'points',
        'reason',
        'created_at'
    )
    search_fields = ('user__username', 'reason')
    list_filter = ('reason', 'created_at')
    ordering = ('-created_at',)  # Newest rewards at top

# ✅ Register Reward with custom admin
admin.site.register(Reward, RewardAdmin)
admin.site.register(User, UserAdmin)
