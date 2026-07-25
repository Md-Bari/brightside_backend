from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Restricts JWT login to staff/superuser Django accounts, used only for
    protecting /api/v1/admin/* endpoints (session + knowledge base admin APIs).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not (self.user.is_staff or self.user.is_superuser):
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError("This account is not authorized for admin access.")
        return data
