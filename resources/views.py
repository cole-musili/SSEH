from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resource
from .forms import ResourceForm
from django.http import FileResponse, Http404 


@login_required
def resource_list(request):
    """Show all available learning resources (students, teachers, or admin)."""
    user = request.user

    # Teachers and Admins see all
    if user.is_teacher or user.is_superuser:
        resources = Resource.objects.all().order_by('-uploaded_at')
    # Students see only allowed resources
    elif user.is_student:
        resources = Resource.objects.filter(visibility__in=['all', 'students']).order_by('-uploaded_at')
    else:
        resources = Resource.objects.filter(visibility='all').order_by('-uploaded_at')

    return render(request, "resources/resource_list.html", {"resources": resources})


@login_required
def upload_resource(request):
    """Allow teachers or admins to upload learning materials."""
    user = request.user
    if not (user.is_teacher or user.is_superuser):
        messages.error(request, "You do not have permission to upload resources.")
        return redirect("resources:resource_list")

    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploader = user
            resource.save()
            messages.success(request, "Resource uploaded successfully!")
            return redirect("resources:resource_list")
    else:
        form = ResourceForm()

    return render(request, "resources/upload_resource.html", {"form": form})


@login_required
def download_resource(request, pk):
    """Serve the file and increment its download count."""
    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        raise Http404("Resource not found.")

    # Increase the download counter
    resource.download_count += 1
    resource.save(update_fields=["download_count"])

    # Serve file as attachment (so it downloads instead of opening)
    response = FileResponse(resource.file.open("rb"), as_attachment=True, filename=resource.filename)
    return response


@login_required
def delete_resource(request, pk):
    """Allow the uploader or a superuser to delete a resource."""
    resource = get_object_or_404(Resource, pk=pk)

    # Only uploader or superuser can delete
    if request.user != resource.uploader and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this resource.")
        return redirect("resources:resource_list")

    if request.method == "POST":
        resource.delete()
        messages.success(request, "Resource deleted successfully.")
        return redirect("resources:resource_list")

    return render(request, "resources/confirm_delete.html", {"resource": resource})