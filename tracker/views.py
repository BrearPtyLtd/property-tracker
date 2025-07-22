from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectStakeholder, ChecklistItem, Document
from django.shortcuts import redirect
from .forms import ProjectForm, StakeholderForm, ChecklistItemForm
from .forms import ProjectStakeholderForm
from .forms import DocumentForm
from django.contrib.auth.decorators import login_required

from django.db.models import Q

def project_list(request):
    query = request.GET.get('q')
    stage = request.GET.get('stage')
    projects = Project.objects.all().order_by('-start_date')

    if query:
        projects = projects.filter(
            Q(name__icontains=query) |
            Q(project_number__icontains=query)
        )

    if stage:
        projects = projects.filter(stage__iexact=stage)

    stages = Project.objects.values_list('stage', flat=True).distinct()

    return render(request, 'tracker/project_list.html', {
        'projects': projects,
        'query': query,
        'stage': stage,
        'stages': stages,
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    stakeholders = ProjectStakeholder.objects.filter(project=project).select_related('stakeholder')
    checklist = ChecklistItem.objects.filter(project=project).order_by('-updated_at')
    documents = Document.objects.filter(project=project).order_by('-uploaded_at')

    return render(request, 'tracker/project_detail.html', {
        'project': project,
        'stakeholders': stakeholders,
        'checklist': checklist,
        'documents': documents,
    })

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'tracker/project_form.html', {'form': form})

def add_checklist_item(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ChecklistItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.save()
            return redirect('project_detail', pk=pk)
    else:
        form = ChecklistItemForm()
    return render(request, 'tracker/checklist_form.html', {'form': form, 'project': project})

def assign_stakeholder(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectStakeholderForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.project = project
            assignment.save()
            return redirect('project_detail', pk=pk)
    else:
        form = ProjectStakeholderForm()
    return render(request, 'tracker/assign_stakeholder.html', {'form': form, 'project': project})

def create_stakeholder(request):
    if request.method == 'POST':
        form = StakeholderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')  # Or redirect to assign if context is passed
    else:
        form = StakeholderForm()
    return render(request, 'tracker/stakeholder_form.html', {'form': form})

def upload_document(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.project = project
            doc.save()
            return redirect('project_detail', pk=pk)
    else:
        form = DocumentForm()
    return render(request, 'tracker/document_form.html', {'form': form, 'project': project})

from django.db.models import Count, Q
from .models import Project, ChecklistItem

@login_required
def dashboard(request):
    total_projects = Project.objects.count()

    stage_counts = (
        Project.objects
        .values('stage')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    pending_checklist = (
        ChecklistItem.objects
        .filter(status='pending')
        .count()
    )

    recent_projects = (
        Project.objects
        .order_by('-start_date')[:5]
    )

    return render(request, 'tracker/dashboard.html', {
        'total_projects': total_projects,
        'stage_counts': stage_counts,
        'pending_checklist': pending_checklist,
        'recent_projects': recent_projects,
    })

from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard')