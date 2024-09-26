from django.contrib import admin
from django.utils.html import format_html
from .models import OriginalImage, ResizedImage, Settings

class OriginalImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'user', 'id')  # Display filename, user, and image preview
    search_fields = ('filename', 'user__username')  # Enable search by filename and username
    list_filter = ('user',)  # Filter by user

    def image_preview(self, obj):
        if obj.filename:  # Ensure the filename is available
            return format_html('<img src="/uploads/original-images/{}" style="width: 35px; height: 35px;" />', obj.filename)  # Display image as thumbnail
        return "No Image"
    
    image_preview.short_description = 'Image Preview'  # Set column title

class ResizedImageAdmin(admin.ModelAdmin):    
    list_display = ('id', 'image_preview', 'original', 'device')  # Show original image reference, details, and image preview
    search_fields = ('filename', 'original__filename')  # Enable search by resized filename and original filename
    list_filter = ('device',)  # Filter by device type    
    
    def image_preview(self, obj):
        if obj.filename:  # Ensure the filename is available
            return format_html('<img src="/uploads/resized-images/{}" style="width: 35px; height: 35px;" />', obj.filename)  # Display image as thumbnail
        return "No Image"
    image_preview.short_description = 'Image Preview'  # Set column title

class SettingsAdmin(admin.ModelAdmin):
    list_display = ('device', 'width', 'height')  # Show device dimensions
    search_fields = ('device',)  # Enable search by device name
    ordering = ('device',)  # Order by device name

# Register models with the admin site
admin.site.register(OriginalImage, OriginalImageAdmin)
admin.site.register(ResizedImage, ResizedImageAdmin)
admin.site.register(Settings, SettingsAdmin)
