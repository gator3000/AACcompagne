#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy as cherrypy
from mako.template import Template
from mako.lookup import TemplateLookup
import tools
import datetime
import time
from connexion_db import Connexion



def E404(**kwargs):
    tools.write_log("USER ERROR 404", "A user found a 404 error or is hacking the server")
    return "<img src='./static/assets/404.jpg' alt='Error 404 Page Not Found' style='min-height: 100%;width: 100%;height: auto;position: fixed;top: 0;left: 0;'/>"
def E500(**kwargs):
    tools.write_log("SERVER ERROR 500", "A user found a 500 error or is hacking the server")
    return "<img src='./static/assets/500.jpg' alt='Error 500 Internal Server Error' style='min-height: 100%;width: 100%;height: auto;position: fixed;top: 0;left: 0;'/>"

class Website(object):
    def __init__(self):
        self.ANNONYMOUS = tools.User("Annonymous", "john.doe@gmail.com", "annonyme", -1)
        self.lookup = TemplateLookup(directories=['static/templates'], input_encoding='utf-8', module_directory='static/tmp/mako_modules')
        self.accountdict = {"myname": "", "mytype": ""}
        try:
            print(tools.log_now("DATABASE starting connexion"))
            self.connexion=Connexion()
        except Exception as e:
            print(e)
            tools.write_log("DATABASE", "connexion failed")
            raise ConnectionError(tools.log_now("DATABASE connexion ERROR"))
        finally:
            print(tools.log_now("DATABASE connected"))
            tools.write_log("DATABASE", "200 connexion made")
            print(tools.log_now("DATABASE initialized"))

    def check_specific_links(self, account):
        if account.type == "drivingschools":
            links = """<li class="pageslinks"><a href="/adding-driving-teacher">Ajouter un Moniteur</a></li>"""
        elif account.type == "drivingteachers":
            links = """"""
        elif account.type == "drivingteachers":
            links = """"""
        else:
            links = ""
        return links



    @cherrypy.expose
    def index(self, **kwargs):
        #print(cherrypy.session["current_account"].id)
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        mytemplate = self.lookup.get_template("index.html")
        account = cherrypy.session["current_account"]
        stats={"driving-pupils": len(self.connexion.SELECT("*","drivingpupils")), "driving-schools": len(self.connexion.SELECT("*","drivingschools"))}
        return mytemplate.render(myPageName="Acceuil", specific_links=self.check_specific_links(cherrypy.session["current_account"]), account=account, stats=stats)
    
    @cherrypy.expose
    def driving_schools(self, **kwargs):
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        mytemplate = self.lookup.get_template("driving-schools.html")
        if "show-teachers" in kwargs:
            current_id = kwargs["show-teachers"]
            id_list = [int(x[0]) for x in self.connexion.SELECT("id", "drivingschools")]
            # print(id_list)
            # print(current_id)
            # print(current_id in id_list)
            #if current_id in id_list:
            school = self.connexion.SELECT("id, name, adress, email, number", "drivingschools", f"id = {current_id}")[0]
            name = school[1]
            mydteachers = self.connexion.SELECT("firstname, lastname, email", "drivingteachers", f"drivingschool = {current_id}")
            text = tools.format_ds_page(school, mydteachers)
            account = cherrypy.session["current_account"]
            return mytemplate.render(myPageName=name, drivingschools=text, account=account)
        pylistofds = self.connexion.SELECT("name, adress, email, number, id", "drivingschools")
        listofds = tools.pylistofdstohtml(pylistofds)
        account = cherrypy.session["current_account"]
        return mytemplate.render(myPageName="Auto-Écoles", drivingschools=listofds, specific_links=self.check_specific_links(cherrypy.session["current_account"]), account=account)

    @cherrypy.expose
    def adding_driving_school(self, **kwargs):
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        mytemplate = self.lookup.get_template("adding-driving-school.html")
        account = cherrypy.session["current_account"]
        return mytemplate.render(myPageName="Ajouter Votre Entreprise", myerror="", specific_links=self.check_specific_links(cherrypy.session["current_account"]), account=account)

    @cherrypy.expose
    def adding_new_driving_school(self, **kwargs):
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        # INSERT INTO drivingschools (name, adress, email, number, password) VALUES ("CAR'rément Permis",  "47 Rue Victor Hugo à Villefranche", "carrementpermis@gmail.com", "0481480203", "835d6dc88b708bc646d6db82c853ef4182fabbd4a8de59c213f2b5ab3ae7d9be");
        if tools.are_all_in("name", "adress", "email", "number", "password", "retyped-password", "description", iterable=kwargs):
            if not tools.are_empty(kwargs["name"], kwargs["adress"], kwargs["email"], kwargs["number"], kwargs["password"], kwargs["retyped-password"]):
                if len(kwargs["number"]) == 10 and kwargs["number"][0] == "0" and " " not in kwargs["number"]:
                    if len(kwargs["name"]) < 256:
                        if len(kwargs["adress"]) < 256:
                            if kwargs["password"] == kwargs["retyped-password"]:
                                if "@" in kwargs['email'] and kwargs['email'].split("@")[1]:
                                    emails = self.connexion.SELECT("*", "drivingschools", f"email = '{kwargs['email']}'")
                                    if not emails:
                                        self.connexion.INSERT("drivingschools", ("name", "adress", "email", "number", "password", "description"), f""" ("{kwargs['name']}", "{kwargs['adress']}", "{kwargs['email']}", "{kwargs['number']}", "{tools.hashme(kwargs['password'])}", "{kwargs['description']}" )""")
                                        raise cherrypy.HTTPRedirect("/driving_schools")
                                    else:myerror = "L'adresse e-mail est déjà utilisée."
                                else:myerror = "L'adresse e-mail n'est pas du bon format !"
                            else:myerror = "Le mot de passe n'est pas le même que celui reécris."
                        else:myerror = "L'adresse de votre Auto-École ne doit pas faire plus de 256 charactères. Essayez de le racourcir."
                    else:myerror = "Le nom de votre entreprise ne doit pas faire plus de 256 charactères."
                else:myerror = "Le numéro saisis n'est pas du bon format (10 chiffres commançant par '0' sans espaces, par exemple : 0123456789)."
            else:myerror = "Remplisez bien tous les champs marqués d'une étoile (tous)."
        else:myerror = ""
        mytemplate = self.lookup.get_template("adding-driving-school.html")
        account = cherrypy.session["current_account"]
        return mytemplate.render(myPageName="Ajouter Votre Entreprise", myerror=myerror, specific_links=self.check_specific_links(cherrypy.session["current_account"]), account=account)


    @cherrypy.expose
    def login(self, **kwargs):
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        if tools.are_all_in("type", "id", "password", iterable=kwargs):
            mytype = kwargs["type"]
            myid = kwargs["id"]
            mypassword = kwargs["password"]
            if not tools.are_empty(mytype, myid, mypassword):
                if mytype in ["drivingschools", "drivingteachers", "drivingpupils"]:
                    tables = "id, email, password, name" if mytype == "drivingschools" else "id, email, password, firstname"
                    account = self.connexion.SELECT(tables, mytype, f"email = '{myid}'")
                    if len(account) == 1:
                        if account[0][2] == tools.hashme(mypassword):
                            cherrypy.session["current_account"] = tools.User(account[0][3], myid, mytype, account[0][0])
                            raise cherrypy.HTTPRedirect("/")
                        else:myerror = "Identifiant ou mot de passe invalide"
                    else:myerror = "Identifiant ou mot de passe invalide"
                else: myerror = "Test"
            else:myerror = "Remplissez bien tout les champs marqués d'une étoile (tous)"
        else:myerror = ""
        myerror = ""
        mytemplate = self.lookup.get_template("login.html")
        account = cherrypy.session["current_account"]
        return mytemplate.render(myPageName="S'identifier", myerror=myerror, specific_links=self.check_specific_links(cherrypy.session["current_account"]), account=account)

    @cherrypy.expose
    def adding_driving_teacher(self, **kwargs):
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        myerror = ""
        mytemplate = self.lookup.get_template("adding-driving-teacher.html")
        account = cherrypy.session["current_account"]
        return mytemplate.render(myPageName="Ajouter un Moniteur", myerror=myerror, specific_links=self.check_specific_links(cherrypy.session["current_account"]), account=account)

    @cherrypy.expose
    def adding_new_driving_teacher(self, **kwargs):
        if "current_account" not in cherrypy.session.keys():
            cherrypy.session["current_account"] = self.ANNONYMOUS
        if tools.are_all_in("firstname", "lastname", "email", iterable=kwargs):
            firstname = kwargs["firstname"]
            lastname = kwargs["lastname"]
            email = kwargs["email"]
            if not tools.are_empty(firstname, lastname, email):
                pass
            else:myerror="Remplissez bien tous les champs marqués d'une étoile (tous)."
        else:myerror=""

    @cherrypy.expose
    def logout(self, **kwargs):
        cherrypy.session["current_account"] = self.ANNONYMOUS
        raise cherrypy.HTTPRedirect("/")


if __name__ == "__main__":
    # port 16384
    tools.write_log("SERVER", "starting")
    cherrypy.config.update({'error_page.404': E404, 'error_page.500': E500})
    WEBSITE = Website()
    cherrypy.quickstart(WEBSITE, config="conf.ini")
    tools.write_log("SERVER", "closed")
    WEBSITE.connexion.close()
    tools.write_log("DATABASE", "disconected")
