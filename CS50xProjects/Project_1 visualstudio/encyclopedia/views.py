from django.shortcuts import render
import markdown
from . import util
import random


def convert_markdown_to_html(title):
    content = util.get_entry(title)
    markdowner = markdown.Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)


def index(request):
    entries = util.list_entries()
    css_file = util.get_entry("CSS")
    coffee = util.get_entry("coffee")
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    html_content = convert_markdown_to_html(title)
    if html_content == None:
        return render(request, "encyclopedia/error.html", {
            "message": "This Entry does not exist"
        })
    else:
        return render(request, "encyclopedia/entry.html",{
            "title": title,
            "content": html_content
        })


def search(request):
    if request.method == "POST":
        search_entry = request.POST['q']
        find_entry = util.get_entry(search_entry)
        content = convert_markdown_to_html(search_entry)
        if find_entry is not None:
            return render(request, "encyclopedia/entry.html", {
                "title": search_entry,
                "content": content,
            })
        else:
            allEntries = util.list_entries()
            recommendlist =[]
            message = "There is no similar page, please search again"
            for entry in allEntries:
                if search_entry.lower() in entry.lower():
                    recommendlist.append(entry)
                    message = "Here are the pages most similar to your search"
            return render(request, "encyclopedia/search.html", {
                "recommendations": recommendlist,
                "message": message
            })
        
                
def new_page(request):
    if request.method =="GET":
        return render(request, "encyclopedia/new_page.html")
    else:
        title = request.POST['title']
        content = request.POST['content']
        titleExist = util.get_entry(title)
        if titleExist is not None:
            return render(request, "encyclopedia/error.html",{
                "message": "Entry page already exists"
            })
        else:
            util.save_entry(title, content)
            html_content = convert_markdown_to_html(title)
            return render(request, "encyclopedia/entry.html",{
                "title": title,
                "content": html_content
            })


def edit_page(request):
    if request.method =="POST":
        title = request.POST['title']
        content = util.get_entry(title)
        return render (request, "encyclopedia/edit_page.html",{
            "title": title,
            "content": content
        })

def save(request):
    if request.method =="POST":
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        html_content = convert_markdown_to_html(title)
        return render(request, "encyclopedia/entry.html",{
                "title": title,
                "content": html_content
            })

def rand(request):
    allEntries = util.list_entries()
    rand_entry = random.choice(allEntries)
    html_content = convert_markdown_to_html(rand_entry)
    return render(request, "encyclopedia/entry.html", {
        "title": rand_entry,
        "content": html_content
    })