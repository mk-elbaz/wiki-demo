from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import random
from . import util
import markdown2
from markdown2 import Markdown


class NewEntryForm(forms.Form):
    entryTitle = forms.CharField(label="Title" ,widget = forms.TextInput(attrs={'class': 'form-control'}))
    entryText = forms.CharField(label="Text", widget=forms.Textarea(attrs={'class': 'form-control'}) )
    editing = forms.BooleanField(initial = False, required = False, widget=forms.HiddenInput())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(req, entry):
    entryTemp = util.get_entry(entry)
    m = Markdown()
    if entryTemp:
        return render(req, "encyclopedia/entry.html", {
            "entry": m.convert(entryTemp),
            "entryTitle": entry
        })
    else:
        return render(req, "encyclopedia/noEntry.html", {
            "entryTitle": entry
        })

def search(req):
    result = req.GET.get('q')
    #found same name
    if util.get_entry(result):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': result}))
    else:
        searchResults = []
        for i in util.list_entries():
            if result.upper() in i.upper():
                searchResults.append(i)
        return render(req, "encyclopedia/search.html", {
            "result" : result,
            "searchRes" : searchResults
        })

def newEntry(req):
    if req.method == "POST":
        form = NewEntryForm(req.POST)
        if form.is_valid():
            entryTitle = form.cleaned_data["entryTitle"]
            entryText = form.cleaned_data["entryText"]
            ##saving
            if not util.get_entry(entryTitle) or form.cleaned_data["editing"] :
                util.save_entry(entryTitle, entryText)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': entryTitle}))

            #########found
            else:
                return render(req, "encyclopedia/newEntry.html", {
                    "form": form,
                    "entry": entryTitle,
                    "found": True
                })
        else:
            return render(req, "encyclopedia/newEntry.html", {
                "form": form,
                "found": False
            })
    ##if not post        
    else:
         return render(req, "encyclopedia/newEntry.html", {
            "form": NewEntryForm(),
            "found": False
        })        


def editEntry(req,entry):
    this = util.get_entry(entry)
    if not this:
        return render(request, "encyclopedia/noEntry.html", {
            "entryTitle": entry    
        })
    else:
        form = NewEntryForm()
        form.fields["entryTitle"].initial = entry    
        form.fields["entryText"].initial = this
        form.fields["editing"].initial = True
        ###save from new entry
        return render(req ,"encyclopedia/newEntry.html",{
            "form" : form,
            "entryTitle" : form.fields["entryTitle"].initial,
            "editing" : form.fields["editing"].initial
        } )

def randomEntryPage(req):
    entries = util.list_entries()
    ##r = random.randint(0 ,len(entries)-1)
    ##randomEntry = util.get_entry(entries[r])
    randomEntry = random.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': randomEntry}))
    