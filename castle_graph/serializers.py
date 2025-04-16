from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator

from castle_graph.models import Invite, ContestUser, ContestGroup, Submission, CaptureCastle, Gif, Castle, \
    SubmissionItem
from question.models import Question
from user.models import User


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


class RegisterContestUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone_number = serializers.CharField(
        required=True,
        allow_null=True,
        max_length=11,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=True
        )

        user.set_password(validated_data['password'])

        with transaction.atomic():
            user.save()
            contest_user = ContestUser.objects.create(user=user)

        return user, contest_user


class ContestGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestGroup
        exclude = ('lead_user',)

    def create(self, validated_data):
        with transaction.atomic():
            group = ContestGroup.objects.create(**validated_data, lead_user=self.context.get('user'))
            self.context.get('user').group = group
            self.context.get('user').save()

        return group


class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'

    def get_user(self, obj):
        return self.context['contest_user']

    def get_group(self, obj):
        return self.context['group']

    def create(self, validated_data):
        return Submission.objects.create(**validated_data, user=self.context['contest_user'],
                                         group=self.context['group'])

    def validate(self, attrs):
        if CaptureCastle.objects.filter(castle_id=attrs['castle']).exists():
            raise serializers.ValidationError('Castle Conqueror')
        return attrs

class GifSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gif
        fields = "__all__"
        read_only_fields = ["user", "confirmed"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'name', 'question']


class CastleSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = Castle
        fields = ['id', 'question', 'castle_name', 'score', 'x', 'y']
