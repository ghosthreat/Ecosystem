# ENTITES : Chenilles + Souris + Vipères
# ACTIVITE : C{erre}, S{chasse C, se reproduit si nourri, meurt sans nourriture}, V{chasse S, se reproduit si nourri, meurt sans nourriture}
# GRAPHE : OUI
# CREDITS : Copyright (c) 2026 ghosthreat 
# LICENSE : MIT


import pygame
import sys
from random import*
import numpy as np
import matplotlib.pyplot as plt

# Initialisation
pygame.init()

# Création de la fenêtre
l, h= 700, 700
ecran = pygame.display.set_mode((l, h))
pygame.display.set_caption("écosystème")

## Création des entités
class Chenilles:
    def __init__(self, x, y):
        self.dir=0
        self.x=x
        self.y=y
        self.v=2
        self.couleur=(111, 200, 219)
        self.vie=True

    def update(self):

        # rencontre d'un mur : va dans l'autre sens + change de direction
        if self.x<0:
            self.x+=self.v
            self.dir=(self.dir+180)%360
        if self.x>l-5:
            self.x-=self.v
            self.dir=(self.dir+180)%360
        if self.y<0:
            self.y+=self.v
            self.dir=(self.dir+180)%360
        if self.y>h-5:
            self.y-=self.v
            self.dir=(self.dir+180)%360

        # non rencontre d'un mur : tourne de 10° et avance d'une distance v
        else :
            self.dir=(self.dir+randint(-1,1)*10)%360
            self.x+=int(np.cos(np.deg2rad(self.dir))*self.v)
            self.y+=int(np.sin(np.deg2rad(self.dir))*self.v)


    def draw(self,ecran):
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, 5, 5))


class Souris:
    def __init__(self, x, y):
        self.dir=0
        self.x=x
        self.y=y
        self.v=2
        self.couleur=(128, 128, 128)
        self.vie=True
        self.nourri=0
        self.attente=0          # attente avant de chasser
        self.modif_proies=0
        self.modif_semblables=0
        self.lim_vie=-500       # meurt en dessous de cette limite de nourriture
        self.energie_reprod=300 # énergie pour se reproduire
        self.gain_energie=500   # énergie gagnée en mangeant


    def update(self, PROIES, SEMBLABLES):
        # remise à 0 des compteurs:
        self.modif_semblables=0
        self.modif_proies=0

        self.nourri-=1
        if self.nourri<self.lim_vie:
            self.vie=False
            self.modif_semblables-=1

        # === REPRODUCTION ===
        # si nourri et pas seul => cherche à se reproduire
        if self.nourri>0 and len(SEMBLABLES)>1 and self.attente==0:
            # trouver le partenaire le plus proche
            part_plus_proche = None
            distance_min = float('inf')

            for part in SEMBLABLES:
                if part.vie and part.nourri>0:# le partenaire doit être vivant + nourri
                    # calcul de la distance au partenaire
                    dx = part.x - self.x
                    dy = part.y - self.y
                    distance = (dx**2+dy**2)**0.5

                    if distance < distance_min and distance > 0:
                        distance_min = distance
                        part_plus_proche = part

            # si on a trouvé un partenaire : on se dirige vers lui
            if part_plus_proche:
                dx = part_plus_proche.x - self.x    # dx = distance horizontale
                dy = part_plus_proche.y - self.y    # dy = distance verticale
                distance = (dx**2+dy**2)**0.5

                if distance > 5:
                    dx /= distance
                    dy /= distance
                    self.x += dx * self.v
                    self.y += dy * self.v
                elif distance < 5:  # partenaire à portée => reproduction
                    self.modif_semblables+=1
                    self.nourri-=self.energie_reprod        # utilise son énergie
                    self.attente+=randint(50,100)           # attend avant de chasser

            else:       # si aucun semblable n'est nourri
                # rencontre d'un mur : va dans l'autre sens + change de direction
                if self.x<0:
                    self.x+=self.v
                    self.dir=(self.dir+180)%360
                if self.x>l-5:
                    self.x-=self.v
                    self.dir=(self.dir+180)%360
                if self.y<0:
                    self.y+=self.v
                    self.dir=(self.dir+180)%360
                if self.y>h-5:
                    self.y-=self.v
                    self.dir=(self.dir+180)%360

                # non rencontre d'un mur : tourne de 10° et avance d'une distance v
                else :
                    self.dir=(self.dir+randint(-1,1)*10)%360
                    self.x+=int(np.cos(np.deg2rad(self.dir))*self.v)
                    self.y+=int(np.sin(np.deg2rad(self.dir))*self.v)

        # === CHASSE ===
        elif self.nourri<=0 and self.attente==0 and len(PROIES)>0:

            # trouver la cible la plus proche
            cible_la_plus_proche = None
            distance_min = float('inf')

            for cible in PROIES:
                if cible.vie:        # la cible doit être vivante
                    # calcul de la distance à la cible
                    dx = cible.x - self.x
                    dy = cible.y - self.y
                    distance = (dx**2+dy**2)**0.5

                    if distance < distance_min and distance > 0:
                        distance_min = distance
                        cible_la_plus_proche = cible

            # si on a trouvé une cible : on se dirige vers elle
            if cible_la_plus_proche:
                dx = cible_la_plus_proche.x - self.x    # dx = distance horizontale
                dy = cible_la_plus_proche.y - self.y    # dy = distance verticale
                distance = (dx**2+dy**2)**0.5

                if distance > 5:
                    dx /= distance
                    dy /= distance
                    self.x += dx * self.v
                    self.y += dy * self.v
                elif distance < 5:  # cible à portée = on la mange
                    self.modif_proies-=1
                    cible_la_plus_proche.vie=False  # tue l'autre entité
                    self.nourri+=self.gain_energie  # se nourrit

        # === ERRANCE ===
        else:
            self.attente-=1         # on se rapproche d'à nouveau chasser
            # rencontre d'un mur : va dans l'autre sens + change de direction
            if self.x<0:
                self.x+=self.v
                self.dir=(self.dir+180)%360
            if self.x>l-5:
                self.x-=self.v
                self.dir=(self.dir+180)%360
            if self.y<0:
                self.y+=self.v
                self.dir=(self.dir+180)%360
            if self.y>h-5:
                self.y-=self.v
                self.dir=(self.dir+180)%360

            # non rencontre d'un mur : tourne de 10° et avance d'une distance v
            else :
                self.dir=(self.dir+randint(-1,1)*10)%360
                self.x+=int(np.cos(np.deg2rad(self.dir))*self.v)
                self.y+=int(np.sin(np.deg2rad(self.dir))*self.v)

    def draw(self,ecran):
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, 5, 5))


class Viperes:
    def __init__(self, x, y):
        self.dir=0
        self.x=x
        self.y=y
        self.v=2
        self.couleur=(196, 129, 54)
        self.vie=True
        self.nourri=0
        self.attente=0          # attente avant de chasser
        self.modif_proies=0
        self.modif_semblables=0
        self.lim_vie=-500       # meurt en dessous de cette limite de nourriture
        self.energie_reprod=300 # énergie pour se reproduire
        self.gain_energie=500   # énergie gagnée en mangeant

    def update(self, PROIES, SEMBLABLES):
        # remise à 0 des compteurs:
        self.modif_semblables=0
        self.modif_proies=0

        self.nourri-=1
        if self.nourri<self.lim_vie:
            self.vie=False
            self.modif_semblables-=1

        # === REPRODUCTION ===
        # si nourri et pas seul => cherche à se reproduire
        if self.nourri>0 and len(SEMBLABLES)>1 and self.attente==0:
            # trouver le partenaire le plus proche
            part_plus_proche = None
            distance_min = float('inf')

            for part in SEMBLABLES:
                if part.vie and part.nourri>0:# le partenaire doit être vivant + nourri
                    # calcul de la distance au partenaire
                    dx = part.x - self.x
                    dy = part.y - self.y
                    distance = (dx**2+dy**2)**0.5

                    if distance < distance_min and distance > 0:
                        distance_min = distance
                        part_plus_proche = part

            # si on a trouvé un partenaire : on se dirige vers lui
            if part_plus_proche:
                dx = part_plus_proche.x - self.x    # dx = distance horizontale
                dy = part_plus_proche.y - self.y    # dy = distance verticale
                distance = (dx**2+dy**2)**0.5

                if distance > 5:
                    dx /= distance
                    dy /= distance
                    self.x += dx * self.v
                    self.y += dy * self.v
                elif distance < 5:  # partenaire à portée => reproduction
                    self.modif_semblables+=1
                    self.nourri-=self.energie_reprod        # utilise son énergie
                    self.attente+=randint(50,100)           # attend avant de chasser

            else:       # si aucun semblable n'est nourri
                # rencontre d'un mur : va dans l'autre sens + change de direction
                if self.x<0:
                    self.x+=self.v
                    self.dir=(self.dir+180)%360
                if self.x>l-5:
                    self.x-=self.v
                    self.dir=(self.dir+180)%360
                if self.y<0:
                    self.y+=self.v
                    self.dir=(self.dir+180)%360
                if self.y>h-5:
                    self.y-=self.v
                    self.dir=(self.dir+180)%360

                # non rencontre d'un mur : tourne de 10° et avance d'une distance v
                else :
                    self.dir=(self.dir+randint(-1,1)*10)%360
                    self.x+=int(np.cos(np.deg2rad(self.dir))*self.v)
                    self.y+=int(np.sin(np.deg2rad(self.dir))*self.v)

        # === CHASSE ===
        elif self.nourri<=0 and self.attente==0 and len(PROIES)>0:

            # trouver la cible la plus proche
            cible_la_plus_proche = None
            distance_min = float('inf')

            for cible in PROIES:
                if cible.vie:        # la cible doit être vivante
                    # calcul de la distance à la cible
                    dx = cible.x - self.x
                    dy = cible.y - self.y
                    distance = (dx**2+dy**2)**0.5

                    if distance < distance_min and distance > 0:
                        distance_min = distance
                        cible_la_plus_proche = cible

            # si on a trouvé une cible : on se dirige vers elle
            if cible_la_plus_proche:
                dx = cible_la_plus_proche.x - self.x    # dx = distance horizontale
                dy = cible_la_plus_proche.y - self.y    # dy = distance verticale
                distance = (dx**2+dy**2)**0.5

                if distance > 5:
                    dx /= distance
                    dy /= distance
                    self.x += dx * self.v
                    self.y += dy * self.v
                elif distance < 5:  # cible à portée = on la mange
                    self.modif_proies-=1
                    cible_la_plus_proche.vie=False  # tue l'autre entité
                    self.nourri+=self.gain_energie  # se nourrit

        # === ERRANCE ===
        else:
            self.attente-=1         # on se rapproche d'à nouveau chasser
            # rencontre d'un mur : va dans l'autre sens + change de direction
            if self.x<0:
                self.x+=self.v
                self.dir=(self.dir+180)%360
            if self.x>l-5:
                self.x-=self.v
                self.dir=(self.dir+180)%360
            if self.y<0:
                self.y+=self.v
                self.dir=(self.dir+180)%360
            if self.y>h-5:
                self.y-=self.v
                self.dir=(self.dir+180)%360

            # non rencontre d'un mur : tourne de 10° et avance d'une distance v
            else :
                self.dir=(self.dir+randint(-1,1)*10)%360
                self.x+=int(np.cos(np.deg2rad(self.dir))*self.v)
                self.y+=int(np.sin(np.deg2rad(self.dir))*self.v)

    def draw(self,ecran):
        pygame.draw.rect(ecran, self.couleur, (self.x, self.y, 5, 5))

nb_c=int(input("nb de chenilles = "))
nb_s=int(input("nb de souris = "))
nb_v=int(input("nb de vipères = "))
C=[Chenilles(randint(0,l),randint(0,h)) for c in range(nb_c)]    # liste des chenilles
S=[Souris(randint(0,l),randint(0,h)) for s in range(nb_s)]       # liste des souris
V=[Viperes(randint(0,l),randint(0,h)) for v in range(nb_v)]      # liste des vipères

# Horloge pour contrôler le FPS
clock = pygame.time.Clock()

## Boucle principale de la simulation

t=0
T=[]
C_val=[]
S_val=[]
V_val=[]

running = True
while running:
    # Données pour le tracé
    T+=[t]
    C_val+=[nb_c]
    S_val+=[nb_s]
    V_val+=[nb_v]

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mise à jour des entités
    for chenille in C:
        chenille.update()

    for souris in S:
        souris.update(C,S)
        nb_c+=souris.modif_proies       # modification du nb de proies
        nb_s+=souris.modif_semblables   # modification du nb de semblables
        if souris.modif_semblables>0:
            for i in range(souris.modif_semblables):
                S+=[Souris(souris.x,souris.y)]     # nouvel individu

    for vipère in V:
        vipère.update(S,V)
        nb_s+=vipère.modif_proies       # modification du nb de proies
        nb_v+=vipère.modif_semblables   # modification du nb de semblables
        if vipère.modif_semblables>0:
            for i in range(vipère.modif_semblables):
                V+=[Viperes(vipère.x,vipère.y)]     # nouvel individu

    # Suppression des cadavres
    C=[chenille for chenille in C if chenille.vie]
    S=[souris for souris in S if souris.vie]
    V=[vipère for vipère in V if vipère.vie]

    # Dessin de la carte
    ecran.fill((0, 100, 0))

    # Dessin des entités
    for chenille in C:
        if chenille.vie:
            chenille.draw(ecran)

    for souris in S:
        if souris.vie:
            souris.draw(ecran)

    for vipère in V:
        if vipère.vie:
            vipère.draw(ecran)

    t+=1
    pygame.display.flip()   # Rafraîchir l'écran

    clock.tick(60)  # 60 FPS

    if nb_c + nb_s + nb_v == 0 or t>=3000:
        running=False

plt.plot(T,C_val,color=(111/255, 200/255, 219/255),label='chenilles')
plt.plot(T,S_val,color=(128/255, 128/255, 128/255),label='souris')
plt.plot(T,V_val,color=(196/255, 129/255, 54/255),label='vipères')
plt.xlabel('temps')
plt.ylabel('populations')
plt.legend()
plt.title("évolutions de l'écosystème")
plt.show()

pygame.quit()
