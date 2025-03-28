from rest_framework import serializers, exceptions

from castle_graph.models import Invite, ContestUser


class InviteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False, allow_null=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Invite
        exclude = ('invited_user',)
        read_only_fields = ('id', 'created_at', 'status', 'uuid')

    def validate(self, data):
        email = data.pop('email', None)
        phone_number = data.pop('phone_number', None)

        if email is None and phone_number is None:
            raise serializers.ValidationError("must be input email or phone_number")

        user = None
        if phone_number:
            temp = ContestUser.objects.filter(is_active=True, user__phone_number=phone_number).first()
            if temp:
                user = temp

        if email:
            temp = ContestUser.objects.filter(is_active=True, user__email=email).first()
            if temp:
                user = temp

        if not user:
            raise exceptions.NotFound("User not found")

        if user.group:
            raise serializers.ValidationError("User is already in a group")

        if data['group'].lead_user != self.context['request'].user.contestuser:
            raise serializers.ValidationError("you dont access to group")

        data['invited_user'] = user

        return data
