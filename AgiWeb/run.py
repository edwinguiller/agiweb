from flask import Flask, url_for, request, render_template, redirect
from fonctions_logiques import *
from constantes import *
import sqlite3 as lite
import random

app = Flask(__name__)

# Une belle (Hyp'ss) page d'accueil avec un lien vers la partie Agilean et un vers la partie Agilog
@app.route('/')
def index():
    return render_template('accueil.html');

#La page Agilog
@app.route('/Agilog')
def agilog():
    return render_template('agiLog_accueil.html');


@app.route('/Agilog/Encours')
def encoursAlog():
    return render_template('encours_alog.html')

@app.route('/Agilog/Encours/<id>')  # route pour passer la pièce (dont l'idéee est séléctionnée) du stock encours à stock réel: Programmeur à faire
def actualize_id(id): #Programmeur à faire
    # TODO: handle the id in the sql


    # return render_template('encours_alog.html')

    return redirect(url_for('encoursAlog'))

@app.route('/Agilog/Encours/Commande_agipart')
def commandepart(): #à faire
    return render_template('cmd_agipart.html')

@app.route('/Agilog/Encours/Commande_agigreen')
def commandegreen(): #à faire
    return render_template('cmd_agigreen.html')


@app.route('/Agilog/Encours/Declarer_kit', methods=['GET', 'POST'])#recupere 2 variable nom et prnom et les ajoutent a la base de données (a modifier pour mettre piece et quantite)
def declarer_kit():

    contenu = ""
    contenu += "<form method='get' action='declarer_kit'>"
    contenu += "num kit "
    contenu += "<input type='text' name='num_kit' value=''>"
    contenu += "<input type='submit' value='Envoyer'>"

    num_kite=request.args.get('num_kit','')
    #génération de l'id
    con = lite.connect(cheminbdd) #attention chez toi c'est pas rangé au meme endroit
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT id FROM production")
    liste_id1 = cur.fetchall()
    liste_id2=[]
    for chaque in liste_id1:
        liste_id2.append(int(chaque[0]))
    if len(liste_id2)==0:
        newid=1
    else:
        newid=max(liste_id2)+1
    con.close()

    con = lite.connect(cheminbdd)
    con.row_factory = lite.Row
    cur = con.cursor()
    a=0
    d=cur.execute(" SELECT datetime('now')")
    if (num_kite!=""):
        d=cur.execute(" SELECT datetime('now')")
        cur.execute("INSERT INTO production('id', 'kit', 'fini','date') VALUES (?,?,?,?)", [newid ,num_kite ,1, d ])
    #con.commit()#enregistrer la requete de modification.
    cur.execute("SELECT id, kit, fini, date FROM Production;")
    liste = cur.fetchall()
    #
    for chaque in liste:
        contenu += "<br/>"
        contenu += str(chaque[0]) + " "
        contenu += str(chaque[1]) + " "
        contenu += str(chaque[2]) + " "
        contenu += str(chaque[3]) + " "
    con.close()

    return contenu;

@app.route('/Agilog/Encours/Aff_stock', methods=['GET']) #la page pour passer une commande
def commande():

    contenu = ""
    con = lite.connect(cheminbdd) #attention chez toi c'est pas rangé au meme endroit
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT datetime('now')")
    d=str(cur.fetchall()[0][0])
    contenu += d

    cur.execute("SELECT nom FROM piece")
    nom = cur.fetchall()
    liste_nom=liste(nom)
    cur.execute("SELECT quantite FROM piece")
    quantite = cur.fetchall()
    liste_quantite=liste(quantite)
    cur.execute("SELECT seuil_recomp FROM piece")
    seuil = cur.fetchall()
    liste_seuil=liste(seuil)

    seuil_commande (liste_quantite,liste_seuil,liste_nom)

    cur.execute("SELECT a_commander FROM piece")
    commande = cur.fetchall()
    liste_commande=liste(commande)
    for i in range (0,len(liste_commande)):
        print (liste_commande[i])
        print (liste_nom[i])

    con.commit
    con.close

    return contenu


#La page Initialisation
@app.route('/Agilog/Initialisation/')
def initialisation ():
    return render_template('initialisation_alog.html')

@app.route('/Agilog/Initialisation/Ajout_piece', methods=['GET', 'POST'])#recupere 2 variable nom et prnom et les ajoutent a la base de données (a modifier pour mettre piece et quantite)
def ajout_piece():
    #variable message :
    err_quant = ''
    msg=''

    # affichage des pièces présente
    con = lite.connect(cheminbdd) #attention chez toi c'est pas rangé au meme endroit
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT id, nom, quantite FROM piece")
    liste_id = cur.fetchall()

    if not request.method == 'POST':
        con.close()
        return render_template('ajout_piece.html',liste_id=liste_id, err_quant= "", msg="")
    else:
        nome = request.form.get('nome','')
        quantitee = request.form.get('quantitee','')
        ide = request.form.get('ide','')

        #test si le stock est un entier si qlq chose est rentré
        try:
            quantitee=int(quantitee)
            assert quantitee>=0
        except ValueError:
            con.close()
            return render_template('ajout_piece.html',liste_id=liste_id, err_quant= err_quant, msg='le stock doit être un nombre entier')
        except AssertionError :
            con.close()
            return render_template('ajout_piece.html',liste_id=liste_id, err_quant= "", msg="Il faut une quantité positive")

        if (nome!="" and quantitee!="" and ide!="" and quantitee>=0):
            # on ajoute le nom l'id et le stock à la bdd
            cur.execute("SELECT id FROM Piece")
            testnom = cur.fetchall()
            test=[]
            for testnom in testnom:
                test.append(testnom[0]) # une liste pour ensuite voir si la piece demandé n'existe pas deja
            if (ide in test):
                return render_template('ajout_piece.html',liste_id=liste_id, err_quant= err_quant, msg="Cette piece existe deja")
            else : #ajouter un createur d'id apres
                cur.execute("INSERT INTO piece('nom', 'quantite', 'id') VALUES (?,?,?)", (nome,quantitee,ide))
                con.commit()
                con.close()
                msg = ''
                return(redirect(url_for('ajout_piece')))
        else :
            return render_template('ajout_piece.html',liste_id=liste_id, err_quant= err_quant, msg="il faut saisir un nom et un id")
    return render_template('ajout_piece.html', liste_id=liste_id, err_quant= err_quant, msg=msg); # LES PROGRAMMEURS a retoucher / separer  fonctions

@app.route('/Agilog/Initialisation/supp', methods=['GET', 'POST'])
def supprimer_piece() :
    if not request.method == 'POST':
        return render_template('ajout_piece.html',liste_id=liste_id, err_quant= "", msg="",testnom="la methode n'est pas post")
    else :
        nomdele=request.form.get('nomdele','')
        con = lite.connect(cheminbdd) #attention chez toi c'est pas rangé au meme endroit
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute ("DELETE FROM 'piece' WHERE nom=?", [nomdele])
        con.commit()
        con.close()
        return(redirect(url_for('ajout_piece')))
    return(redirect(url_for('ajout_piece')))

@app.route('/Agilog/Initialisation/Gestion_stock', methods=['GET', 'POST'])#recupere 2 variable nom et prnom et les ajoutent a la base de données (a modifier pour mettre piece et quantite)
def gestion_stock():
    #var

    msg =""

    #recupere nom des objets pour le vollet deroulant

    con = lite.connect("AgiWeb_BDD.db")
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT nom FROM piece")
    liste_nom = cur.fetchall()

    nome=request.form.get('nome','')
    seuile=request.form.get('seuile','')
    secue=request.form.get('secue','')
    delaie=request.form.get('delaie','')
    #test si ce sont bien des entiers
    if not request.method == 'POST':
        con.close()
        return render_template('gestion_stock.html', liste_nom=liste_nom, msg = "")
    else :
        if (nome!="" and seuile!="" and secue!="" and delaie!=""):
            try:
                seuile=int(seuile)
                secue=int(secue)
                delaie=int(delaie)
                assert seuile >= 0 and secue>=0 and delaie>=0
            except ValueError:
                con.close()
                return render_template('gestion_stock.html', liste_nom=liste_nom, msg = "attention il faut saisir un entier !")
            except AssertionError:
                con.close()
                return render_template('gestion_stock.html', liste_nom=liste_nom, msg = "attention il faut saisir un entier positif !")
            cur.execute("UPDATE Piece SET seuil_recomp=?, stock_secu=?, delai_reappro=? WHERE nom=?", [seuile,secue,delaie,nome])
            con.commit()
            con.close()
            return redirect(url_for('gestion_stock'))
        else:
            con.close()
            return render_template('gestion_stock.html', liste_nom=liste_nom, msg = "attention vous n'avez rien saisi")

    return render_template('gestion_stock.html', liste_nom=liste_nom, msg = "")

@app.route('/Agilog/Initialisation/Code_kit', methods=['GET', 'POST'])
def code_kit():
    #variable
    contenu=""
    #On crée un kit ou on en choisit un
    kit= recupere_interraction(1,contenu)
    #On choisit un kit existant
    con = lite.connect(cheminbdd)
    con.row_factory = lite.Row
    cur=con.cursor()
    cur.execute("SELECT nom_kit FROM kit;")
    base=cur.fetchall()#variable pour le menu déroulant
    #historique des kit existant
    cur.execute("SELECT id FROM kit;")
    id=cur.fetchall()
    #création dico_kit
    dico_kit=[]
    for base in id :
        cur.execute('SELECT piece, quantite FROM compo_kit WHERE kit=?;',[base[0]])
        dico_kit.append(cur.fetchall())#dico_kit est une liste de dictionnaire ou chaque dictionnaire est un kit
    cur.execute("SELECT nom_kit FROM kit;")
    base=cur.fetchall()
    cur.close()
    return(render_template("Code_kit_init.html", msg="" ,tab_piece=dico_kit ,liste_kit=base ,liste_id=id ))

@app.route('/Agilog/Initialisation/Code_kit/modif_kit', methods=['GET', 'POST'])
def modif_kit():
    #ici y faut que tu mettes les variables dont j'ai besoin pour la page càd "kit_a_modif" le nom du
    #kit à modifier et "piece_du_kit" la liste des piece dans ce kit_a_modif
    con = lite.connect(cheminbdd)
    con.row_factory = lite.Row
    cur=con.cursor()
    cur.execute("SELECT nom FROM piece;")
    pieces=cur.fetchall()
    kit_a_modif = request.form.get('nom_kit_a_modif')
    id_kit_a_modif=3 #a toi de jouer
    piece_du_kit=[{"nom":"a","quantite":3},{"nom":"b","quantite":3},{"nom":"c","quantite":3}]
    #pareil faut que tu la remplisses avec la bdd en faisant une liste de dictionnaire qui contoienne nom et quantité

    #fin recup variable

#J'ai testé la fonction, les fonctionnalités marchent,
	#si tu as un problème, tu peux retrouver dans fonction_test la fonction que j'ai testé qui marche
    #recupération des variables :
    if not request.method == 'POST':
        return render_template('modif_kit_init.html',d=kit_a_modif, id=id_kit_a_modif,pieces = pieces,msg="",piece_du_kit=piece_du_kit)
    else :
        # mets les action sur la bdd ici
        #return request.form.get('nom_kit_a_modif')
        #jusque la
        piece_a_ajouter = request.form.get('saisi_piece')
        option = request.form.get('option')
        quantitee = request.form.get('quantite')
        return render_template('modif_kit_init.html',d=kit_a_modif, id=id_kit_a_modif,pieces = pieces,msg="",piece_du_kit=piece_du_kit)
    #fin de recuperation des variables
    contenu=""
    piece_a_ajouter=[bool,option]#piece=[True/false,nom de la piece à ajouter]
    con = lite.connect(cheminbdd)
    con.row_factory = lite.Row
    cur=con.cursor()
    cur.execute("SELECT nom FROM piece;")
    pieces=cur.fetchall()#variable pour le menu déroulant pour le choix des pieces
    cur.execute("SELECT id FROM kit WHERE nom_kit=?;",[kit_a_modif])#car dans la base compo_kit, kit correspond à des id
    kit_a_modifier=liste(cur.fetchall())#variable pour travailler dans la base compo_kit
    quantite=quantite_bonne(recupere_interraction(1,contenu))#on récupère et vérifie la quantite=[quantite,True/False]
    cur.execute("SELECT piece FROM compo_kit WHERE kit=?;",[kit_a_modifier[0]])
    piece_du_kit=liste(cur.fetchall())#cette liste nous permet de vérifier que la nouvelle pièce à ajouter n'est pas déjà présente
    #Si on veut supprimer une piece du kit
    if piece_a_ajouter[0]:
    	cur.execute("DELETE FROM compo_kit WHERE kit=?,piece=?;",[kit_a_modifier[0],piece_a_ajouter[1]])
    #Si on veut ajouter une piece au kit
    elif piece_a_ajouter not in piece_du_kit and quantite[1]:#la pièce n'est pas présente dans le kit et la quantite est bonne donc on ajoute la piece simplement au kit
    		cur.execute("INSERT INTO compo_kit(kit,piece,quantite) VALUES (?,?,?);",[kit_a_modifier[0],piece_a_ajouter[1],quantite[0]])
    else:#la piece est présente dans le kit, on modifie donc juste la quantite
    	cur.execute("UPDATE compo_kit SET quantite=? WHERE kit=?,piece=?;",[quantite[0],kit_a_modifier[0],piece_a_ajouter[1]])

    return(render_template('modif_kit_init.html',d=kit_a_modif, id=id_kit_amodif,pieces = piece_du_kit,msg="return final"))

#La page pour Agilean
@app.route('/Agilean')
def agilean():
    return render_template('agiLean_accueil.html');

@app.route('/Agilean/Reception')
def receptkit():
    return render_template('recept_stock_alean.html')+"</br> page non faite"



# se lance avec http:

#//localhost:5678
if __name__ == '__main__':
    app.run(debug=True, port=5678)
