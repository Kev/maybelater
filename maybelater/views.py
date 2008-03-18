# Create your views here.

from django.shortcuts import render_to_response 
from django.db.models import Q
from maybelater.models import Task, Project, Context, PRIORITIES, EFFORTS

def templatePrefix():
    """ Return the user's chosen interface prefix.
    """
    return "simple"

def standardDict():
    """ Return values which are useful in most templates.
    """
    return {}

def taskSearchFilter(query):
    """ Generate tuple of Q filters for Tasks.
    """
    return (
        Q(name__icontains=query) |
        Q(project__name__icontains=query) |
        Q(context__name__icontains=query)
    )

def searchTasks(request, filterQ=()):
    """ Search the tasks for the given filter, also filtering by search term
        if request contains a GET search query
    """
    query = request.GET.get('search', '')
    if query:
        tasks = Task.objects.filter(taskSearchFilter(query) & filterQ).distinct()
    else:
        tasks = Task.objects.filter(filterQ)
    return (taskResultToDictList(tasks), query)

def taskResultToDictList(tasks):
    """ Take the result of a Task.objects query and add to array.
    """
    todo_listing= [] 
    oddRow = 1
    for task in tasks: 
        todo_dict = {} 
        todo_dict['task_object'] = task 
        if oddRow == 1:
            todo_dict['odd_row'] = True
        oddRow = 1 - oddRow
        todo_listing.append(todo_dict)
    return todo_listing

def context_listing():
    """ List all contexts
    """
    context_listing = [] 
    for context in Context.objects.all(): 
        context_dict = {} 
        context_dict['context_object'] = context 
        context_listing.append(context_dict)
    return context_listing

def project_listing():
    """ List all projects
    """
    project_listing = [] 
    for project in Project.objects.all(): 
        project_dict = {} 
        project_dict['project_object'] = project 
        project_listing.append(project_dict)
    return project_listing

def priority_listing():
    """ List all priorities
    """
    priority_listing = [] 
    for (index, name) in PRIORITIES: 
        priority_dict = {} 
        priority_dict['index'] = index
        priority_dict['name'] = name
        priority_listing.append(priority_dict)
    return priority_listing
 
def effort_listing():
    """ List all efforts
    """
    effort_listing = [] 
    for (index, name) in EFFORTS: 
        effort_dict = {} 
        effort_dict['index'] = index
        effort_dict['name'] = name
        effort_listing.append(effort_dict)
    return effort_listing
  
def constructTaskLink(prefix, typeId):
    """ Construct the prefix for task URLs depending if there's a typeId.
    """
    link = prefix
    if typeId:
        link = "%s/%d" % (link, typeId)
    return "%s/%s" % (link, "task")

def menu_items(currentLink):
    """ Construct a list of menu items, including setting the highlighted one.
    """
    links = [#{'name':'Inbox','link':'/context/','current':False},#Inbox is treated specially in the template, it's not a real view
            {'name':'Contexts','link':'/context/','current':False},
            {'name':'Projects','link':'/project/','current':False},
            {'name':'To Complete','link':'/outstanding/','current':False},
            {'name':'Completed','link':'/completed/','current':False},
            {'name':'Archived','link':'/archived/','current':False},
            {'name':'Process / Review','link':'/review/','current':False}]
    for linkDict in links:
        if linkDict['name'] == currentLink:
            linkDict['current'] = True
    return links


def mergeStandardDict(newDict, currentLink):
    """ Merges specialist dict with the standard template args.
        Specialist keys overwrite standard keys.
    """  
    standard = {'menu_items':menu_items(currentLink), 'context_listing':context_listing(), 'project_listing':project_listing(), 'effort_listing':effort_listing(), 'priority_listing':priority_listing()}
    for newKey in newDict:
        standard[newKey] = newDict[newKey]
    return standard
    
def all_tasks(request): 
    todo_listing = [] 
    for task in Task.objects.all(): 
        todo_dict = {} 
        todo_dict['task_object'] = task 
        todo_listing.append(todo_dict) 
    return render_to_response("%s/all_tasks.html" % templatePrefix(), { 'todo_listing': todo_listing, 'context_listing':context_listing(), 'project_listing':project_listing() })
    


def completed(request): 
    (todo_listing, query) = searchTasks(request, (Q(completed=True)))
    return render_to_response("%s/completed.html" % templatePrefix(), mergeStandardDict({'task_link_prefix':constructTaskLink('/completed', None),  'todo_listing': todo_listing, 'query': query  }, 'Completed'))

def outstanding(request): 
    (todo_listing, query) = searchTasks(request, (Q(completed=False)))
    return render_to_response("%s/outstanding.html" % templatePrefix(), mergeStandardDict({'task_link_prefix':constructTaskLink('/outstanding',None),  'todo_listing': todo_listing, 'query': query}, 'To Complete'))

def project(request, projectId=None, taskId=None):
    projectName = "Inbox"
    if not projectId: 
        if len(Project.objects.all()) > 0:
            projectId = Project.objects.all()[0].id
        else:
            projectId = None
    else:    
        projectId = int(projectId)
    if projectId:
        projectName = Project.objects.get(id=projectId).name
    else:
        projectName = "No projects"
    if taskId:
        selected_task = Task.objects.get(id=taskId)
    else:
        selected_task = None
    
    (todo_listing, query) = searchTasks(request, (Q(project=projectId)))
    return render_to_response("%s/project.html" % templatePrefix(), mergeStandardDict({'task_link_prefix':constructTaskLink('/project',projectId),  'selected_task':selected_task, 'todo_listing': todo_listing, 'project_name':projectName, 'query': query}, 'Projects'))


def context(request, contextId=None, taskId=None):
    contextName = "Inbox"
    if contextId: 
        contextId = int(contextId)
        contextName = Context.objects.get(id=contextId).name
    else:
        contextId = None
    (todo_listing, query) = searchTasks(request, (Q(context=contextId)))
    if taskId:
        selected_task = Task.objects.get(id=taskId)
    else:
        selected_task = None
    return render_to_response("%s/context.html" % templatePrefix(), mergeStandardDict({'task_link_prefix':constructTaskLink("/context",contextId), 'selected_task':selected_task, 'todo_listing': todo_listing, 'context_name':contextName, 'query': query}, 'Contexts'))
    
def task(request, taskId): 
    taskId = int(taskId)
    taskObject = Task.objects.get(id=taskId)
    return render_to_response("%s/task.html" % templatePrefix(), { 'task_object': taskObject })

def createContext(request): 
    name = request.POST.get('name', '')
    parent = request.POST.get('parent', '')
    if parent:
        parent = Context.objects.get(id=int(parent))
    else:
        parent = None
    newContext = Context(name=name, parent=parent)
    newContext.save()
    return context(request, newContext.id)

def createProject(request): 
    name = request.POST.get('name', '')
    parent = request.POST.get('parent', '')
    if parent:
        parent = Project.objects.get(id=int(parent))
    else:
        parent = None
    newProject = Project(name=name, parent=parent)
    newProject.save()
    return project(request, newProject.id)
    
def createTask(request):
    pass
    
    
def generateTestData(request):
    """ Not really a view - generate test data for a system.
    """
    projects = {}
    for name in ("Psi", "GTD", "Housework", "Inventing"):
        project = Project(name=name)
        project.save()
        projects[name] = project
    contexts = {}
    for name in ("Home", "Work", "On the road", "Shopping"):
        context = Context(name=name)
        context.save()
        contexts[name] = context
    stuff = {'Do stuff':None, 'Do Psi stuff':projects['Psi'], 'Wash dishes':projects['Housework']}
    for name in stuff:
        task = Task(name=name, project=stuff[name])
        task.save()
    return HttpResponse("Done")