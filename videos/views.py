from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import os
from django.shortcuts import render
print("Cloud name:", os.environ.get("CLOUDINARY_CLOUD_NAME"))
print("API key:", os.environ.get("CLOUDINARY_API_KEY"))
print("API secret:", os.environ.get("CLOUDINARY_API_SECRET"))
from .models import Video, Comment, Like, Photo, ContactMessage
from .forms import VideoForm, CommentForm, PhotoForm


# ---------------- Age Gate ----------------
def age_gate(request):
    if request.session.get('is_adult'):
        return redirect('home')
    return render(request, 'videos/age_gate.html')


def age_accept(request):
    request.session['is_adult'] = True
    request.session.save()
    return redirect('home')


# ---------------- Home ----------------
def home(request):
    query = request.GET.get('q', '')

    if query:
        videos = Video.objects.filter(
            is_published=True,
            title__icontains=query
        ).order_by('-created_at')
    else:
        videos = Video.objects.filter(
            is_published=True
        ).order_by('-created_at')

    return render(request, 'videos/home.html', {
        'videos': videos,
        'query': query
    })


# ---------------- Video Detail ----------------
def video_detail(request, pk):
    if not request.session.get('is_adult'):
        return redirect('age_gate')

    video = get_object_or_404(Video, pk=pk, is_published=True)

    video.views += 1
    video.save(update_fields=['views'])

    comments = video.comments.order_by('-created_at')

    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(
            user=request.user,
            video=video
        ).exists()

    # Related videos
    related_videos = Video.objects.filter(
        user=video.user,
        is_published=True
    ).exclude(pk=video.pk).order_by('-created_at')[:10]

    # Comment form
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)

            if form.is_valid():
                comment = form.save(commit=False)
                comment.video = video
                comment.user = request.user
                comment.save()

                return redirect('video_detail', pk=video.pk)

        else:
            return redirect('login')

    else:
        form = CommentForm()

    return render(request, 'videos/video_detail.html', {
        'video': video,
        'comments': comments,
        'form': form,
        'liked': liked,
        'related_videos': related_videos,
    })


# ---------------- Session Test ----------------
def session_test(request):
    request.session['test'] = 'ok'
    return HttpResponse(f"Session test: {request.session.get('test')}")


# ---------------- Upload Video ----------------
@login_required
def upload_video(request):

    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)

        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user

            from cloudinary.uploader import upload

            file = request.FILES['file']
            result = upload(file, resource_type="video")

            video.file = result['secure_url']
            video.save()

            return redirect('home')

    else:
        form = VideoForm()

    return render(request, 'videos/upload_video.html', {'form': form})


# ---------------- My Videos ----------------
@login_required
def my_videos(request):
    videos = Video.objects.filter(user=request.user)

    return render(request, 'videos/my_videos.html', {
        'videos': videos
    })


# ---------------- Signup ----------------
def signup(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('home')

    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {
        'form': form
    })


# ---------------- Logout ----------------
def custom_logout(request):

    if 'is_adult' in request.session:
        del request.session['is_adult']

    logout(request)

    return redirect('login')


# ---------------- Like Toggle ----------------
@login_required
def toggle_like(request, pk):

    if request.method == "POST":

        video = get_object_or_404(Video, pk=pk)

        like, created = Like.objects.get_or_create(
            user=request.user,
            video=video
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            "liked": liked,
            "total_likes": Like.objects.filter(video=video).count()
        })


# ---------------- Edit Video ----------------
@login_required
def edit_video(request, pk):

    video = get_object_or_404(Video, pk=pk)

    if video.user != request.user:
        messages.error(request, "You are not allowed to edit this video.")
        return redirect('home')

    if request.method == "POST":

        form = VideoForm(
            request.POST,
            request.FILES,
            instance=video
        )

        if form.is_valid():
            form.save()

            messages.success(request, "Video updated successfully.")

            return redirect('home')

    else:
        form = VideoForm(instance=video)

    return render(request, 'videos/edit_video.html', {
        'form': form,
        'video': video
    })


# ---------------- Delete Video ----------------
@login_required
def delete_video(request, pk):

    video = get_object_or_404(Video, pk=pk)

    if video.user != request.user:
        messages.error(request, "You are not allowed to delete this video.")
        return redirect('home')

    if request.method == "POST":

        video.delete()

        messages.success(request, "Video deleted successfully.")

        return redirect('home')

    return render(request, 'videos/delete_video.html', {
        'video': video
    })


# ---------------- Photo Gallery ----------------
def photo_gallery(request):

    query = request.GET.get('q', '')

    if query:
        photos = Photo.objects.filter(
            is_published=True,
            title__icontains=query
        ).order_by('-created_at')
    else:
        photos = Photo.objects.filter(
            is_published=True
        ).order_by('-created_at')

    return render(request, 'videos/photo_gallery.html', {
        'photos': photos,
        'query': query
    })


# ---------------- Photo Detail ----------------
def photo_detail(request, pk):

    photo = get_object_or_404(
        Photo,
        pk=pk,
        is_published=True
    )

    return render(request, 'videos/photo_detail.html', {
        'photo': photo
    })


# ---------------- Upload Photo ----------------
@login_required
def upload_photo(request):

    if request.method == 'POST':

        form = PhotoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()

            return redirect('photo_gallery')

    else:
        form = PhotoForm()

    return render(request, 'videos/upload_photo.html', {
        'form': form
    })


# ---------------- Edit Photo ----------------
@login_required
def edit_photo(request, pk):

    photo = get_object_or_404(Photo, pk=pk)

    if photo.user != request.user:
        messages.error(request, "You are not allowed to edit this photo.")
        return redirect('photo_gallery')

    if request.method == "POST":

        form = PhotoForm(
            request.POST,
            request.FILES,
            instance=photo
        )

        if form.is_valid():
            form.save()

            messages.success(request, "Photo updated successfully.")

            return redirect('photo_gallery')

    else:
        form = PhotoForm(instance=photo)

    return render(request, 'videos/edit_photo.html', {
        'form': form,
        'photo': photo
    })


# ---------------- Delete Photo ----------------
@login_required
def delete_photo(request, pk):

    photo = get_object_or_404(Photo, pk=pk)

    if photo.user != request.user:
        messages.error(request, "You are not allowed to delete this photo.")
        return redirect('photo_gallery')

    if request.method == "POST":

        photo.delete()

        messages.success(request, "Photo deleted successfully.")

        return redirect('photo_gallery')

    return render(request, 'videos/delete_photo.html', {
        'photo': photo
    })


# ---------------- Contact ----------------
def contact(request):

    success = False
    error = None

    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        try:

            send_mail(
                subject=f"New contact from {name}",
                message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_text}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )

            success = True

        except BadHeaderError:
            error = "Invalid header found."

        except Exception as e:
            error = f"An error occurred: {e}"

    return render(request, 'videos/contact.html', {
        'success': success,
        'error': error
    })
def privacy_policy(request):
    return render(request, 'privacy.html')

def terms_policy(request):
    return render(request, 'terms.html')