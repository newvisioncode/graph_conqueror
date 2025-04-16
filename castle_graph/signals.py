from django.db.models.signals import post_save
from django.dispatch import receiver

from castle_graph.models import CaptureCastle
from channels.layers import get_channel_layer


@receiver(post_save, sender=CaptureCastle, dispatch_uid="captured_castle")
async def capture_castle(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    if created:
        await channel_layer.group_send(
            'global',
            {"type": "capture_castle", "message": {
                "type": "capture_castle",
                "message": {
                    "castle": {
                        "name": instance.castle.castle_name,
                        "id": instance.castle.id
                    },
                    "group": {
                        "name": instance.group.name,
                        "id": instance.group.id
                    }
                }
            }},
        )
