from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import OriginalImage, ResizedImage, Settings
from django.core.files.storage import FileSystemStorage
from PIL import Image, ExifTags
import os
import zipfile
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
            return render(request, 'login.html')
    return render(request, 'login.html')

def upload(request):

    # Fetch the settings from the database
    mobile_settings = Settings.objects.get(device='mobile')
    tablet_settings = Settings.objects.get(device='tablet')
    desktop_settings = Settings.objects.get(device='desktop')

    # Pass the settings to the template
    context = {
        'mobile_width': mobile_settings.width,
        'mobile_height': mobile_settings.height,
        'tablet_width': tablet_settings.width,
        'tablet_height': tablet_settings.height,
        'desktop_width': desktop_settings.width,
        'desktop_height': desktop_settings.height,
        'is_authenticated': request.user.is_authenticated,
    }

    if request.method == 'POST' and request.FILES.get('file'):

        if not request.user.is_authenticated:
            messages.warning(request, 'You must be logged in to upload your files to the server')
            return redirect('login')

        file = request.FILES['file']
        fs = FileSystemStorage()
        original_filename = fs.save('original-images/' + file.name, file)

        # Create an original image linked to the current user
        original_image = OriginalImage.objects.create(filename=file.name, user=request.user)

        # Open the image
        image = Image.open(fs.path(original_filename))

        # Ensure the image is in RGB mode for saving as JPEG
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Check for EXIF data and correct the orientation
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation)
                if orientation_value is not None:
                    if orientation_value == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation_value == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation_value == 8:
                        image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # No EXIF data, or orientation not found
            pass

        sizes = Settings.objects.all()

        for size in sizes:
            # Maintain the aspect ratio when resizing
            image.thumbnail((size.width, size.height), Image.LANCZOS)
            resized_filename = f"{file.name}-{size.device}.jpg"
            resized_path = os.path.join('uploads/resized-images/', resized_filename)
            # Ensure RGB conversion before saving
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(resized_path, format='JPEG')  # Specify JPEG format

            # Create a resized image object
            ResizedImage.objects.create(original=original_image, filename=resized_filename, device=size.device)

        messages.success(request, 'Image uploaded and resized successfully!')
        return redirect('dashboard')

    return render(request, 'upload.html', context)

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Show only images uploaded by the current user
    images = OriginalImage.objects.filter(user=request.user)
    settings = Settings.objects.all()
    settings_list = [{'device': setting.device, 'width': setting.width, 'height': setting.height} for setting in settings]

    return render(request, 'dashboard.html', {'original_images': images, 'settings': settings_list})


def update_settings(request):
    if request.method == 'POST':
        for device in ['mobile', 'tablet', 'desktop']:
            width = request.POST.get(f'{device}_width')
            height = request.POST.get(f'{device}_height')
            setting = Settings.objects.get(device=device)
            setting.width = width
            setting.height = height
            setting.save()

        messages.success(request, 'Settings updated successfully!')

    return redirect('dashboard')

def preview(request, id):
    original_image_id = OriginalImage.objects.get(id=id)
    resized_images = ResizedImage.objects.filter(original=original_image_id)
    return render(request, 'preview.html', {'resized_images': resized_images, 'id':id})

def download_all_resized_images(request, id):
    try:
        # Fetch the original image based on the ID
        original_image = OriginalImage.objects.get(id=id)
        original_image_filename = original_image.filename.split('.')[0]  # Remove the file extension

        # Create a ZIP filename and path
        zip_filename = f"{original_image_filename}_resized_images.zip"
        zip_file_path = os.path.join('uploads/resized-images', zip_filename)

        # Open the ZIP file for writing
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            # Fetch all resized images associated with the original image
            resized_images = ResizedImage.objects.filter(original=original_image)

            # Loop over resized images and add to ZIP
            for resized_image in resized_images:
                file_path = os.path.join('uploads/resized-images', resized_image.filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))

        # Serve the ZIP file as a downloadable response
        with open(zip_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={zip_filename}'

        # Show a success message to the user
        messages.success(request, 'Download of all resized images successful!')
        return redirect(f'/preview/{id}')  # Adjust this to your actual preview URL

    except OriginalImage.DoesNotExist:
        messages.error(request, 'Original image not found!')
        return HttpResponse(status=404)

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return HttpResponse(status=500)


def delete_images(request, original_image_id):
    original_image = get_object_or_404(OriginalImage, pk=original_image_id)
    
    original_image_path = os.path.join(settings.MEDIA_ROOT, 'original-images', original_image.filename)
    resized_images = original_image.resized_images.all()
    
    if os.path.exists(original_image_path):
        os.remove(original_image_path)
    
    for resized_image in resized_images:
        resized_image_path = os.path.join(settings.MEDIA_ROOT, 'resized-images', resized_image.filename)
        if os.path.exists(resized_image_path):
            os.remove(resized_image_path)
    
    resized_images.delete()
    original_image.delete()
    
    messages.success(request, 'Images deleted successfully!')
    return redirect('dashboard')

def logout(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')
