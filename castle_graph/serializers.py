from rest_framework import serializers

from castle_graph.models import Invite


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = '__all__'
        read_only_fields = ('id', 'time_created', 'status')

    def validate(self, data):
        if data['user'].group != None:
            raise serializers.ValidationError("User is already in a group")
        return data
