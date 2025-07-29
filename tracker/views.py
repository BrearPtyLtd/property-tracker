from django.shortcuts import render, get_object_or_404
from .models import Project, ProjectStakeholder, ChecklistItem, Document
from django.shortcuts import redirect
from .forms import ProjectForm, StakeholderForm, ChecklistItemForm
from .forms import ProjectStakeholderForm
from .forms import DocumentForm
from django.contrib.auth.decorators import login_required

from django.template.loader import get_template
from xhtml2pdf import pisa

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

from django.http import HttpResponse
from .models import Project

@login_required
def export_project_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)
    stakeholders = ProjectStakeholder.objects.filter(project=project).select_related('stakeholder')
    checklist = ChecklistItem.objects.filter(project=project)
    documents = Document.objects.filter(project=project)

    template = get_template('tracker/project_pdf.html')
    html = template.render({
        'project': project,
        'stakeholders': stakeholders,
        'checklist': checklist,
        'documents': documents
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="project_{project.pk}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed', status=500)
    return response

    from django.db.models import Q
from django.utils.dateparse import parse_date

@login_required
def project_report(request):
    projects = Project.objects.all().order_by('-start_date')
    stage = request.GET.get('stage')
    q = request.GET.get('q')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    if q:
        projects = projects.filter(Q(name__icontains=q) | Q(project_number__icontains=q))
    if stage:
        projects = projects.filter(stage__iexact=stage)
    if start:
        projects = projects.filter(start_date__gte=parse_date(start))
    if end:
        projects = projects.filter(start_date__lte=parse_date(end))

    stages = Project.objects.values_list('stage', flat=True).distinct()

    return render(request, 'tracker/project_report.html', {
        'projects': projects,
        'stage': stage,
        'q': q,
        'start_date': start,
        'end_date': end,
        'stages': stages,
    })

@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('project_detail', pk=project.pk)
    return render(request, 'tracker/project_form.html', {'form': form})

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return redirect('project_detail', pk=pk)

# User registration
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect('dashboard')  # or wherever you want to send them
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})    
