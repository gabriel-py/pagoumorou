from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from pagoumorou.models import Property, Rental, Room, RoomFeature, RoomPhoto, RoomPrice

@receiver(post_save, sender=Room)
@receiver(post_delete, sender=Room)
def invalidate_room_cache(sender, instance, **kwargs):
    """
    Invalidates the cache for a specific room when it's saved or deleted.
    Also clears the entire cache as room changes affect search results.
    """
    # Invalidate specific room detail cache
    cache.delete(f"room_details_{instance.id}")
    # Clear general search caches (more complex to granularly invalidate search results,
    # so a full clear is simpler but less efficient for broad searches).
    cache.clear()

@receiver(post_save, sender=RoomPrice)
@receiver(post_delete, sender=RoomPrice)
def invalidate_room_price_cache(sender, instance, **kwargs):
    """
    Invalidates the room's detail cache and general search caches when room prices change.
    """
    cache.delete(f"room_details_{instance.room.id}")
    cache.clear()

@receiver(post_save, sender=RoomPhoto)
@receiver(post_delete, sender=RoomPhoto)
def invalidate_room_photo_cache(sender, instance, **kwargs):
    """
    Invalidates the room's detail cache and general search caches when room photos change.
    """
    cache.delete(f"room_details_{instance.room.id}")
    cache.clear()

@receiver(post_save, sender=RoomFeature)
@receiver(post_delete, sender=RoomFeature)
def invalidate_room_feature_cache(sender, instance, **kwargs):
    """
    Invalidates the room's detail cache and general search caches when room features change.
    """
    cache.delete(f"room_details_{instance.room.id}")
    cache.clear()

@receiver(post_save, sender=Property)
@receiver(post_delete, sender=Property)
def invalidate_property_related_caches(sender, instance, **kwargs):
    """
    Invalidates caches for all rooms related to a property when the property changes.
    """
    for room in instance.room_set.all():
        cache.delete(f"room_details_{room.id}")
    cache.clear() # Clear general search caches as property changes can affect many rooms

@receiver(post_save, sender=Rental)
@receiver(post_delete, sender=Rental)
def invalidate_rental_related_caches(sender, instance, **kwargs):
    """
    Invalidates the room's detail cache and general search caches when rental data changes,
    as rentals affect room availability.
    """
    cache.delete(f"room_details_{instance.room.id}")
    cache.clear()
