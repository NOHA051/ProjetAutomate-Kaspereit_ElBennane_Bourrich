#!/usr/bin/env python3
"""
Programme de traitement des automates finis :
  - Lecture depuis fichier texte
  - Affichage en tableau
  - Standardisation
  - Déterminisation (subset construction)
  - Minimisation (algorithme de Moore / partition refinement)
  - Gestion des epsilon-transitions (ε-fermeture)
"""

import sys
import os
from collections import defaultdict, deque
from itertools import combinations


# ─────────────────────────────────────────────
# 1. LECTURE DU FICHIER
# ─────────────────────────────────────────────


def lire_automate(chemin):
    """
    Format du fichier :
      ligne 1 : alphabet  (ex: a b)
      ligne 2 : nb états  (ex: 3)
      ligne 3 : états initiaux séparés par espaces (ex: 0 1)
      ligne 4 : états terminaux séparés par espaces (ex: 2)
      lignes suivantes : transitions  (ex: 0a1  ou  0e1 pour ε)
    """
    with open(chemin, encoding='utf-8') as f:
        lignes = [l.strip() for l in f if l.strip()]

    alphabet   = lignes[0].split()
    nb_etats   = int(lignes[1])
    initiaux   = list(map(int, lignes[2].split()))
    terminaux  = list(map(int, lignes[3].split()))

    transitions = defaultdict(lambda: defaultdict(set))
    for ligne in lignes[4:]:
        ligne = ligne.strip()
        if not ligne:
            continue
        # format : <état_src><lettre><état_dst>
        # La lettre peut être 'e' ou 'ε' pour epsilon
        src = ""
        i = 0
        while i < len(ligne) and ligne[i].isdigit():
            src += ligne[i]
            i += 1
        lettre = ligne[i]
        dst = ligne[i+1:]
        src = int(src)
        dst = int(dst)
        if lettre in ('e', 'ε', 'eps'):
            lettre = 'ε'
        transitions[src][lettre].add(dst)

    etats = list(range(nb_etats))
    return {
        'alphabet':    alphabet,
        'etats':       etats,
        'initiaux':    initiaux,
        'terminaux':   terminaux,
        'transitions': transitions,
        'nb_etats':    nb_etats,
    }







# ─────────────────────────────────────────────
# 2. AFFICHAGE EN TABLEAU
# ─────────────────────────────────────────────


def afficher_tableau(automate, titre="Automate"):
    """Affiche l'automate sous forme de tableau de transitions."""
    alphabet  = automate['alphabet']
    etats     = automate['etats']
    initiaux  = set(automate['initiaux'])
    terminaux = set(automate['terminaux'])
    trans     = automate['transitions']

    # inclure ε si des transitions epsilon existent
    has_eps = any('ε' in trans[s] for s in etats)
    colonnes = (['ε'] if has_eps else []) + alphabet

    # largeurs de colonnes
    larg_etat = max(len(str(e)) + 2 for e in etats)
    larg_etat = max(larg_etat, 6)
    larg_col  = max((len(c) for c in colonnes), default=3)
    larg_col  = max(larg_col, 5)

    sep = "+" + "-" * larg_etat + "+" + (("─" * larg_col + "+") * len(colonnes))

    print(f"\n{'═'*60}")
    print(f"  {titre}")
    print(f"{'═'*60}")

    # en-tête
    print("+" + "-" * larg_etat + "+" + (("-" * larg_col + "+") * len(colonnes)))
    entete = "|" + "État".center(larg_etat) + "|"
    for c in colonnes:
        entete += c.center(larg_col) + "|"
    print(entete)
    print("+" + "=" * larg_etat + "+" + (("=" * larg_col + "+") * len(colonnes)))

    # lignes
    for e in etats:
        marqueur = ""
        if e in initiaux and e in terminaux:
            marqueur = "→*"
        elif e in initiaux:
            marqueur = "→ "
        elif e in terminaux:
            marqueur = " *"
        else:
            marqueur = "  "
        cell_etat = (marqueur + str(e)).center(larg_etat)
        ligne = "|" + cell_etat + "|"
        for c in colonnes:
            dests = trans[e].get(c, set())
            if dests:
                cell = "{" + ",".join(str(d) for d in sorted(dests)) + "}"
            else:
                cell = "∅"
            ligne += cell.center(larg_col) + "|"
        print(ligne)
        print("+" + "-" * larg_etat + "+" + (("-" * larg_col + "+") * len(colonnes)))

    print(f"  Initiaux  : {sorted(initiaux)}")
    print(f"  Terminaux : {sorted(terminaux)}")
    print(f"  Alphabet  : {alphabet}")


# ─────────────────────────────────────────────
# 3. EPSILON-FERMETURE
# ─────────────────────────────────────────────

















# ─────────────────────────────────────────────
# 4. VÉRIFICATIONS
# ─────────────────────────────────────────────
/////////////VERIFICATIONS /////////
def est_standard(automate):
    """Un automate est standard s'il a un unique état initial
    et qu'aucune transition ne pointe vers cet état initial."""
    initiaux = automate['initiaux']
    if len(initiaux) != 1:
        return False
    i0 = initiaux[0]
    trans = automate['transitions']
    for src in automate['etats']:
        for lettre, dests in trans[src].items():
            if i0 in dests:
                return False
    return True


def est_deterministe(automate):
    """Un AFD a un seul initial et au plus une destination par (état, lettre)."""
    if len(automate['initiaux']) != 1:
        return False
    trans = automate['transitions']
    for src in automate['etats']:
        for lettre, dests in trans[src].items():
            if lettre == 'ε':
                return False
            if len(dests) > 1:
                return False
    return True


def est_complet(automate):
    """Vérifie si chaque (état, lettre) a exactement une transition."""
    if not est_deterministe(automate):
        return False
    trans    = automate['transitions']
    alphabet = automate['alphabet']
    for e in automate['etats']:
        for lettre in alphabet:
            if len(trans[e].get(lettre, set())) != 1:
                return False
    return True
# ─────────────────────────────────────────────
# 5. STANDARDISATION
# ─────────────────────────────────────────────

























# ─────────────────────────────────────────────
# 6. DÉTERMINISATION (subset construction)
# ─────────────────────────────────────────────

def determiniser(automate):
    """
    Déterminisation par construction des sous-ensembles.
    Renvoie un AFD complet (avec puits si nécessaire).
    """
    # Supprimer les ε d'abord
    aut = supprimer_epsilon(automate)
    if est_deterministe(aut):
        print("  → L'automate est déjà déterministe.")
        # compléter si nécessaire
        return completer(aut)

    trans    = aut['transitions']
    alphabet = aut['alphabet']
    terminaux = set(aut['terminaux'])

    # état initial = ε-fermeture de l'ensemble des initiaux
    init_set = frozenset(aut['initiaux'])

    etats_map   = {}   # frozenset -> int
    new_trans   = defaultdict(lambda: defaultdict(set))
    new_terminaux = set()
    file        = deque()

    def get_id(fs):
        if fs not in etats_map:
            etats_map[fs] = len(etats_map)
            file.append(fs)
        return etats_map[fs]

    get_id(init_set)

    while file:
        current_set = file.popleft()
        src_id = etats_map[current_set]

        if current_set & terminaux:
            new_terminaux.add(src_id)

        for lettre in alphabet:
            dest_set = set()
            for e in current_set:
                dest_set |= trans[e].get(lettre, set())
            dest_fs = frozenset(dest_set)
            if dest_fs:
                dst_id = get_id(dest_fs)
                new_trans[src_id][lettre] = {dst_id}

    new_etats = list(range(len(etats_map)))

    afd = {
        'alphabet':    alphabet,
        'etats':       new_etats,
        'initiaux':    [0],
        'terminaux':   sorted(new_terminaux),
        'transitions': new_trans,
        'nb_etats':    len(new_etats),
        '_etats_map':  {v: sorted(k) for k, v in etats_map.items()},
    }
    return completer(afd)


def completer(automate):
    """Ajoute un état puits si l'AFD n'est pas complet."""
    trans    = automate['transitions']
    alphabet = automate['alphabet']
    etats    = automate['etats']

    manque = False
    for e in etats:
        for lettre in alphabet:
            if not trans[e].get(lettre):
                manque = True
                break

    if not manque:
        return automate

    puits = max(etats) + 1
    new_trans = defaultdict(lambda: defaultdict(set))
    for e in etats:
        for lettre in alphabet:
            dests = trans[e].get(lettre, set())
            if dests:
                new_trans[e][lettre] = set(dests)
            else:
                new_trans[e][lettre] = {puits}
    # puits → puits pour toutes les lettres
    for lettre in alphabet:
        new_trans[puits][lettre] = {puits}

    return {
        'alphabet':    alphabet,
        'etats':       etats + [puits],
        'initiaux':    automate['initiaux'],
        'terminaux':   automate['terminaux'],
        'transitions': new_trans,
        'nb_etats':    len(etats) + 1,
    }


# ─────────────────────────────────────────────
# 7. MINIMISATION (algorithme de Moore)
# ─────────────────────────────────────────────



















# ─────────────────────────────────────────────
# 8. MENU PRINCIPAL
# ─────────────────────────────────────────────
def afficher_infos(automate):
    print(f"  Standard      : {'Oui' if est_standard(automate) else 'Non'}")
    print(f"  Déterministe  : {'Oui' if est_deterministe(automate) else 'Non'}")
    print(f"  Complet       : {'Oui' if est_complet(automate) else 'Non'}")


def menu(automate_original, nom_fichier):
    automate_courant = automate_original
    while True:
        print(f"\n{'─'*60}")
        print(f"  Fichier : {nom_fichier}")
        afficher_infos(automate_courant)
        print(f"{'─'*60}")
        print("  1. Afficher le tableau")
        print("  2. Standardiser")
        print("  3. Déterminiser")
        print("  4. Minimiser")
        print("  5. Pipeline complet (Standard → Déterministe → Minimal)")
        print("  6. Réinitialiser (automate original)")
        print("  0. Quitter / changer de fichier")
        choix = input("  Votre choix : ").strip()

        if choix == '1':
            afficher_tableau(automate_courant, f"Automate courant ({nom_fichier})")

        elif choix == '2':
            a = standardiser(automate_courant)
            afficher_tableau(a, "Automate standardisé")
            automate_courant = a

        elif choix == '3':
            a = determiniser(automate_courant)
            if '_etats_map' in a:
                print("\n  Correspondance sous-ensembles → états :")
                for k, v in sorted(a['_etats_map'].items()):
                    print(f"    État {k} ← {{{','.join(map(str, v))}}}")
            afficher_tableau(a, "Automate déterminisé (complet)")
            automate_courant = {k: v for k, v in a.items() if k != '_etats_map'}

        elif choix == '4':
            a = minimiser(automate_courant)
            afficher_tableau(a, "Automate minimisé")
            automate_courant = a

        elif choix == '5':
            print("\n  ── Étape 1 : Standardisation ──")
            a = standardiser(automate_original)
            afficher_tableau(a, "1. Standardisé")
            print("\n  ── Étape 2 : Déterminisation ──")
            a = determiniser(a)
            if '_etats_map' in a:
                print("\n  Correspondance sous-ensembles → états :")
                for k, v in sorted(a['_etats_map'].items()):
                    print(f"    État {k} ← {{{','.join(map(str, v))}}}")
            afficher_tableau(a, "2. Déterminisé")
            a = {k: v for k, v in a.items() if k != '_etats_map'}
            print("\n  ── Étape 3 : Minimisation ──")
            a = minimiser(a)
            afficher_tableau(a, "3. Minimisé")
            automate_courant = a

        elif choix == '6':
            automate_courant = automate_original
            print("  → Automate réinitialisé.")

        elif choix == '0':
            break
        else:
            print("  Choix invalide.")


def choisir_fichier(dossier="automates_txt"):
    """Liste les fichiers .txt du dossier et permet d'en choisir un."""
    if not os.path.isdir(dossier):
        print(f"Dossier '{dossier}' introuvable.")
        return None

    fichiers = sorted([f for f in os.listdir(dossier) if f.endswith('.txt')])
    if not fichiers:
        print(f"Aucun fichier .txt trouvé dans '{dossier}'.")
        return None

    print(f"\n{'═'*60}")
    print("  Automates disponibles :")
    print(f"{'═'*60}")
    for i, f in enumerate(fichiers, 1):
        print(f"  {i:3}. {f}")
    print("   0. Quitter")

    choix = input("\n  Numéro de l'automate : ").strip()
    if choix == '0':
        return None
    try:
        idx = int(choix) - 1
        if 0 <= idx < len(fichiers):
            return os.path.join(dossier, fichiers[idx])
    except ValueError:
        pass
    print("  Choix invalide.")
    return None


def main():
    dossier = "automates_txt"
    if len(sys.argv) > 1:
        # fichier passé en argument
        chemin = sys.argv[1]
        try:
            a = lire_automate(chemin)
            afficher_tableau(a, f"Automate original ({os.path.basename(chemin)})")
            menu(a, os.path.basename(chemin))
        except Exception as ex:
            print(f"Erreur : {ex}")
        return

    while True:
        chemin = choisir_fichier(dossier)
        if chemin is None:
            print("Au revoir.")
            break
        try:
            a = lire_automate(chemin)
            afficher_tableau(a, f"Automate original ({os.path.basename(chemin)})")
            menu(a, os.path.basename(chemin))
        except Exception as ex:
            print(f"Erreur lors du chargement : {ex}")


if __name__ == "__main__":
    main()
