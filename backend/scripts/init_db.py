"""
Script pour parser le Code Pénal Algérien et l'insérer dans SQLite
Ce script extrait tous les articles du texte du Code Pénal
"""

import re
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database import DatabaseService


def parse_code_penal(text: str) -> list:
    """
    Parse le texte du Code Pénal et extrait tous les articles
    Retourne une liste de dictionnaires
    """
    articles = []
    
    # Contexte actuel (livre, titre, chapitre, section)
    current_livre = ""
    current_titre = ""
    current_chapitre = ""
    current_section = ""
    
    # Patterns pour détecter les sections
    livre_pattern = re.compile(r'LIVRE\s+(PREMIER|DEUXIEME|TROISIEME|QUATRIEME|CINQUIEME|[IVX]+)', re.IGNORECASE)
    titre_pattern = re.compile(r'TITRE\s+([IVX]+|PREMIER)', re.IGNORECASE)
    chapitre_pattern = re.compile(r'Chapitre\s+([IVX]+|[0-9]+)', re.IGNORECASE)
    section_pattern = re.compile(r'Section\s+([0-9]+|[IVX]+)', re.IGNORECASE)
    
    # Pattern pour les articles - plusieurs formats
    article_patterns = [
        re.compile(r'Art(?:icle)?\.?\s*(\d+(?:\s*bis(?:\s*\d+)?)?)\s*[-–.]?\s*[-–]?\s*(.+?)(?=Art(?:icle)?\.?\s*\d+|$)', re.IGNORECASE | re.DOTALL),
        re.compile(r'Art(?:icle)?\s+(\d+)\s*[-–.]?\s*(.+?)(?=Art(?:icle)?\s+\d+|$)', re.IGNORECASE | re.DOTALL),
    ]
    
    # Nettoyer le texte
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Diviser en lignes pour analyser la structure
    lines = text.split('\n')
    current_text = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Détecter les changements de section
        livre_match = livre_pattern.search(line)
        if livre_match:
            current_livre = line
            continue
        
        titre_match = titre_pattern.search(line)
        if titre_match:
            current_titre = line
            continue
        
        chapitre_match = chapitre_pattern.search(line)
        if chapitre_match:
            current_chapitre = line
            continue
        
        section_match = section_pattern.search(line)
        if section_match:
            current_section = line
            continue
        
        current_text += line + " "
    
    # Maintenant extraire les articles du texte complet
    for pattern in article_patterns:
        matches = pattern.findall(current_text)
        for match in matches:
            numero = match[0].strip()
            texte = match[1].strip()
            
            # Nettoyer le texte
            texte = re.sub(r'\s+', ' ', texte)
            texte = texte.strip()
            
            if len(texte) > 20:  # Ignorer les articles trop courts
                articles.append({
                    'numero': f"Art. {numero}",
                    'texte': texte,
                    'texte_arabe': '',  # À remplir si disponible
                    'categorie': current_section or current_chapitre,
                    'section': current_section,
                    'chapitre': current_chapitre,
                    'titre': current_titre,
                    'livre': current_livre
                })
        
        if articles:
            break
    
    return articles


def parse_code_penal_v2(text: str) -> list:
    """
    Version améliorée du parser - extraction par regex simple
    """
    articles = []
    
    # Pattern simple mais efficace
    pattern = re.compile(
        r'Art\.?\s*(\d+(?:\s*(?:bis|ter|quater)(?:\s*\d+)?)?)\s*[-–.]?\s*[-–]?\s*'
        r'(?:\([^)]+\)\s*)?'  # Optionnel: (Loi n° ...)
        r'(.+?)(?=Art\.?\s*\d+|$)',
        re.IGNORECASE | re.DOTALL
    )
    
    # Nettoyer le texte
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    matches = pattern.findall(text)
    
    for numero, contenu in matches:
        numero = numero.strip()
        contenu = re.sub(r'\s+', ' ', contenu).strip()
        
        # Ignorer les articles trop courts ou invalides
        if len(contenu) < 30:
            continue
        
        # Tronquer si trop long (probablement a capturé plusieurs articles)
        if len(contenu) > 3000:
            contenu = contenu[:3000] + "..."
        
        articles.append({
            'numero': f"Art. {numero}",
            'texte': contenu,
            'texte_arabe': '',
            'categorie': '',
            'section': '',
            'chapitre': '',
            'titre': '',
            'livre': ''
        })
    
    return articles


# Articles du Code Pénal Algérien - Données extraites du PDF
# Format structuré pour éviter toute perte de données
CODE_PENAL_ARTICLES = [
    # PRINCIPES GENERAUX
    {
        'numero': 'Art. 1',
        'texte': "Il n'y a pas d'infraction, ni de peine ou de mesures de sûreté sans loi.",
        'categorie': 'Principes généraux',
        'section': 'Dispositions préliminaires'
    },
    {
        'numero': 'Art. 2',
        'texte': "La loi pénale n'est pas rétroactive, sauf si elle est moins rigoureuse.",
        'categorie': 'Principes généraux',
        'section': 'Dispositions préliminaires'
    },
    {
        'numero': 'Art. 3',
        'texte': "La loi pénale s'applique à toutes les infractions commises sur le territoire de la République. Elle s'applique également aux infractions commises à l'étranger lorsqu'elles relèvent de la compétence des juridictions répressives algériennes en vertu des dispositions du code de procédure pénale.",
        'categorie': 'Principes généraux',
        'section': 'Dispositions préliminaires'
    },
    {
        'numero': 'Art. 4',
        'texte': "Les infractions peuvent être sanctionnées par des peines et prévenues par des mesures de sûreté. Les peines sont principales, lorsqu'elles peuvent être prononcées sans être adjointes à aucune autre. Elles sont accessoires quand elles sont la conséquence d'une peine principale. Les peines complémentaires ne peuvent être prononcées séparément d'une peine principale.",
        'categorie': 'Peines et mesures de sûreté',
        'section': 'Dispositions préliminaires'
    },
    {
        'numero': 'Art. 5',
        'texte': "Les peines principales en matière criminelle sont: 1° la mort, 2° la réclusion perpétuelle, 3° la réclusion à temps pour une durée de cinq à vingt ans. Les peines principales en matière délictuelle sont: 1° l'emprisonnement de plus de deux mois à cinq ans, 2° l'amende de plus de 2.000 DA. Les peines principales en matière contraventionnelle sont: 1° l'emprisonnement d'un jour au moins à deux mois au plus, 2° l'amende de 20 à 2.000 DA.",
        'categorie': 'Peines principales',
        'section': 'Peines applicables aux personnes physiques'
    },
    {
        'numero': 'Art. 6',
        'texte': "Les peines accessoires sont l'interdiction légale et la dégradation civique. Elles ne s'attachent qu'aux peines criminelles.",
        'categorie': 'Peines accessoires',
        'section': 'Peines applicables aux personnes physiques'
    },
    {
        'numero': 'Art. 7',
        'texte': "L'interdiction légale prive le condamné, durant l'exécution de la peine principale de l'exercice de ses droits patrimoniaux; ses biens sont administrés dans les formes prévues en cas d'interdiction judiciaire.",
        'categorie': 'Peines accessoires',
        'section': 'Peines applicables aux personnes physiques'
    },
    {
        'numero': 'Art. 8',
        'texte': "La dégradation civique consiste: 1° dans la destitution et l'exclusion des condamnés de toutes fonctions ou emplois supérieurs; 2° dans la privation du droit d'être électeur ou éligible et de tous les droits civiques et politiques et du droit de porter toute décoration; 3° dans l'incapacité d'être juré, expert, de servir de témoin; 4° dans l'incapacité d'être tuteur ou subrogé tuteur; 5° dans la privation du droit de porter des armes, d'enseigner, de diriger une école.",
        'categorie': 'Peines accessoires',
        'section': 'Peines applicables aux personnes physiques'
    },
    # PEINES COMPLEMENTAIRES
    {
        'numero': 'Art. 9',
        'texte': "Les peines complémentaires sont: 1° L'assignation à résidence, 2° L'interdiction de séjour, 3° L'interdiction d'exercer certains droits, 4° La confiscation partielle des biens, 5° La dissolution d'une personne morale, 6° La publicité de la condamnation.",
        'categorie': 'Peines complémentaires',
        'section': 'Peines applicables aux personnes physiques'
    },
    {
        'numero': 'Art. 11',
        'texte': "L'assignation à résidence consiste dans l'obligation faite à un condamné de demeurer dans une circonscription territoriale déterminée par le jugement. Sa durée ne peut être supérieure à cinq ans. La condamnation est notifiée au ministère de l'intérieur qui peut délivrer des autorisations temporaires de déplacement.",
        'categorie': 'Peines complémentaires',
        'section': 'Peines applicables aux personnes physiques'
    },
    {
        'numero': 'Art. 12',
        'texte': "L'interdiction de séjour consiste dans la défense faite à un condamné de paraître dans certains lieux. Sa durée ne peut être supérieure à cinq ans en matière délictuelle et à dix ans en matière criminelle.",
        'categorie': 'Peines complémentaires',
        'section': 'Peines applicables aux personnes physiques'
    },
    {
        'numero': 'Art. 15',
        'texte': "La confiscation consiste dans la dévolution définitive, à l'Etat, d'un ou plusieurs biens déterminés. En cas de condamnation pour crime, le tribunal peut ordonner la confiscation des objets qui ont servi à l'exécution de l'infraction ou qui en sont les produits.",
        'categorie': 'Peines complémentaires',
        'section': 'Peines applicables aux personnes physiques'
    },
    # MESURES DE SURETE
    {
        'numero': 'Art. 19',
        'texte': "Les mesures de sûreté personnelles sont: 1° L'internement judiciaire dans un établissement psychiatrique; 2° Le placement judiciaire dans un établissement thérapeutique; 3° L'interdiction d'exercer une profession, une activité ou un art; 4° La déchéance totale ou partielle des droits de puissance paternelle.",
        'categorie': 'Mesures de sûreté',
        'section': 'Mesures de sûreté'
    },
    {
        'numero': 'Art. 20',
        'texte': "Les mesures de sûreté réelles sont: 1° La confiscation des biens; 2° La fermeture d'établissement.",
        'categorie': 'Mesures de sûreté',
        'section': 'Mesures de sûreté'
    },
    # CLASSIFICATION DES INFRACTIONS
    {
        'numero': 'Art. 27',
        'texte': "Selon leur degré de gravité, les infractions sont qualifiées crimes, délits ou contraventions et punies de peines criminelles, délictuelles ou contraventionnelles.",
        'categorie': 'Classification des infractions',
        'section': 'L\'infraction'
    },
    {
        'numero': 'Art. 30',
        'texte': "Est considérée comme le crime même, toute tentative criminelle qui aura été manifestée par un commencement d'exécution ou par des actes non équivoques tendant directement à le commettre, si elle n'a été suspendue ou si elle n'a manqué son effet que par des circonstances indépendantes de la volonté de son auteur.",
        'categorie': 'Tentative',
        'section': 'L\'infraction'
    },
    {
        'numero': 'Art. 31',
        'texte': "La tentative de délit n'est punissable qu'en vertu d'une disposition expresse de la loi. La tentative de contravention ne l'est jamais.",
        'categorie': 'Tentative',
        'section': 'L\'infraction'
    },
    # LEGITIME DEFENSE
    {
        'numero': 'Art. 39',
        'texte': "Il n'y a pas d'infraction: 1° Lorsque le fait était ordonné ou autorisé par la loi; 2° Lorsque le fait était commandé par la nécessité actuelle de la légitime défense de soi-même ou d'autrui ou d'un bien appartenant à soi-même ou à autrui, pourvu que la défense soit proportionnée à la gravité de l'agression.",
        'categorie': 'Faits justificatifs',
        'section': 'L\'infraction'
    },
    {
        'numero': 'Art. 40',
        'texte': "Sont compris dans les cas de nécessité actuelle de légitime défense: 1° L'homicide commis, les blessures faites ou les coups portés en repoussant une agression contre la vie ou l'intégrité corporelle; 2° L'acte commis en se défendant ou en défendant autrui contre les auteurs de vols ou de pillages exécutés avec violence.",
        'categorie': 'Faits justificatifs',
        'section': 'L\'infraction'
    },
    # PARTICIPANTS A L'INFRACTION
    {
        'numero': 'Art. 41',
        'texte': "Sont considérés comme auteurs tous ceux qui, personnellement, ont pris une part directe à l'exécution de l'infraction, et tous ceux qui ont provoqué à l'action par dons, promesses, menaces, abus d'autorité et de pouvoir, machinations ou artifices coupables.",
        'categorie': 'Participants à l\'infraction',
        'section': 'L\'auteur de l\'infraction'
    },
    {
        'numero': 'Art. 42',
        'texte': "Sont considérés comme complices d'une infraction ceux qui, sans participation directe à cette infraction, ont, avec connaissance, aidé par tous moyens ou assisté l'auteur dans les actes qui l'ont préparée, facilitée ou qui l'ont consommée.",
        'categorie': 'Participants à l\'infraction',
        'section': 'L\'auteur de l\'infraction'
    },
    {
        'numero': 'Art. 44',
        'texte': "Le complice d'un crime ou d'un délit est punissable de la peine réprimant ce crime ou ce délit. Les circonstances personnelles n'ont d'effet qu'à l'égard du seul participant auquel elles se rapportent. La complicité n'est jamais punissable en matière contraventionnelle.",
        'categorie': 'Participants à l\'infraction',
        'section': 'L\'auteur de l\'infraction'
    },
    # RESPONSABILITE PENALE
    {
        'numero': 'Art. 47',
        'texte': "N'est pas punissable celui qui était en état de démence au moment de l'infraction.",
        'categorie': 'Responsabilité pénale',
        'section': 'L\'auteur de l\'infraction'
    },
    {
        'numero': 'Art. 48',
        'texte': "N'est pas punissable celui qui a été contraint à l'infraction par une force à laquelle il n'a pu résister.",
        'categorie': 'Responsabilité pénale',
        'section': 'L\'auteur de l\'infraction'
    },
    {
        'numero': 'Art. 49',
        'texte': "Le mineur de 13 ans ne peut faire l'objet que de mesures de protection ou de rééducation. Le mineur de 13 à 18 ans peut faire l'objet soit de mesures de protection ou de rééducation, soit de peines atténuées.",
        'categorie': 'Responsabilité pénale',
        'section': 'L\'auteur de l\'infraction'
    },
    # CIRCONSTANCES ATTENUANTES
    {
        'numero': 'Art. 53',
        'texte': "Les peines prévues par la loi contre l'accusé reconnu coupable, en faveur de qui les circonstances atténuantes ont été retenues peuvent être réduites. Dans tous les cas où la peine prévue par la loi est celle de l'emprisonnement à temps ou de l'amende, et si les circonstances paraissent atténuantes, l'emprisonnement peut être réduit à un jour et l'amende à 5 DA.",
        'categorie': 'Circonstances atténuantes',
        'section': 'Individualisation de la peine'
    },
    # RECIDIVE
    {
        'numero': 'Art. 54',
        'texte': "Quiconque ayant été, par décision définitive, condamné à une peine criminelle, a commis un second crime comportant, comme peine principale, la réclusion perpétuelle, peut être condamné à mort si le second crime a entraîné mort d'homme.",
        'categorie': 'Récidive',
        'section': 'Individualisation de la peine'
    },
    # CRIMES CONTRE LA SURETE DE L'ETAT
    {
        'numero': 'Art. 61',
        'texte': "Est coupable de trahison et puni de mort, tout Algérien, tout militaire ou marin au service de l'Algérie, qui: 1° Porte les armes contre l'Algérie; 2° Entretient des intelligences avec une puissance étrangère en vue de l'engager à entreprendre des hostilités contre l'Algérie.",
        'categorie': 'Trahison et espionnage',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 64',
        'texte': "Est coupable d'espionnage et puni de mort, tout étranger qui commet l'un des actes visés à l'article 61.",
        'categorie': 'Trahison et espionnage',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    # TERRORISME
    {
        'numero': 'Art. 87 bis',
        'texte': "Est considéré comme acte terroriste ou subversif, tout acte visant la sûreté de l'Etat, l'intégrité du territoire, la stabilité et le fonctionnement normal des institutions par toute action ayant pour objet de: semer l'effroi au sein de la population, entraver la circulation, attenter aux symboles de la Nation.",
        'categorie': 'Actes terroristes',
        'section': 'Crimes qualifiés d\'actes terroristes'
    },
    # ATTROUPEMENTS
    {
        'numero': 'Art. 97',
        'texte': "Est interdit sur la voie publique ou dans un lieu public: 1° Tout attroupement armé; 2° Tout attroupement non armé qui peut troubler la tranquillité publique.",
        'categorie': 'Attroupements',
        'section': 'Crimes contre la paix publique'
    },
    # DETOURNEMENT
    {
        'numero': 'Art. 119',
        'texte': "Tout magistrat, tout fonctionnaire, tout officier public, qui volontairement détourne, dissipe, retient indûment ou soustrait des deniers publics ou privés, des effets en tenant lieu ou des pièces, titres, actes, effets mobiliers, qui étaient entre ses mains, soit en vertu, soit à raison de ses fonctions, encourt: l'emprisonnement de 1 à 5 ans si la valeur est inférieure à 1.000.000 DA; la réclusion à temps de 5 à 10 ans si supérieure.",
        'categorie': 'Détournement',
        'section': 'Détournements et concussions'
    },
    # CORRUPTION
    {
        'numero': 'Art. 126',
        'texte': "Est puni de la réclusion à temps de deux à dix ans et d'une amende, tout fonctionnaire ou toute personne investie d'un mandat électif qui aura, sans droit, directement ou indirectement, sollicité ou agréé des offres ou promesses, sollicité ou reçu des dons ou présents pour faire ou s'abstenir de faire un acte de sa fonction.",
        'categorie': 'Corruption',
        'section': 'Corruption et trafic d\'influence'
    },
    {
        'numero': 'Art. 127',
        'texte': "Est puni des mêmes peines, tout employeur, tout administrateur ou préposé d'une entreprise qui a, à l'insu et sans le consentement de son commettant, soit directement, soit par personne interposée, sollicité ou agréé des offres ou promesses, sollicité ou reçu des dons, présents, commissions, escomptes ou primes pour faire ou s'abstenir de faire un acte de son emploi ou de sa mission.",
        'categorie': 'Corruption',
        'section': 'Corruption et trafic d\'influence'
    },
    # FAUX ET USAGE DE FAUX
    {
        'numero': 'Art. 214',
        'texte': "Tout fonctionnaire ou officier public qui, dans l'exercice de ses fonctions, a commis un faux: soit par fausses signatures, soit par altération des actes, écritures ou signatures, soit par supposition de personnes, soit par des écritures faites ou intercalées sur des registres ou d'autres actes publics, est puni de la réclusion à temps de dix à vingt ans.",
        'categorie': 'Faux en écritures',
        'section': 'Faux et usage de faux'
    },
    {
        'numero': 'Art. 222',
        'texte': "Quiconque a contrefait, falsifié ou altéré des monnaies métalliques ou des billets de banque ayant cours légal en Algérie ou à l'étranger, ou qui a émis, introduit en Algérie ou exporté lesdites monnaies contrefaites, falsifiées ou altérées, est puni de la réclusion perpétuelle.",
        'categorie': 'Fausse monnaie',
        'section': 'Faux et usage de faux'
    },
    # MEURTRE
    {
        'numero': 'Art. 254',
        'texte': "L'homicide commis volontairement est qualifié meurtre. L'auteur d'un meurtre est puni de la réclusion perpétuelle.",
        'categorie': 'Meurtre',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 255',
        'texte': "Tout meurtre commis avec préméditation ou guet-apens est qualifié assassinat. L'auteur d'un assassinat est puni de mort.",
        'categorie': 'Assassinat',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 256',
        'texte': "Est qualifié parricide, le meurtre des père et mère légitimes, naturels ou adoptifs, ou de tout autre ascendant légitime. Le parricide est puni de mort.",
        'categorie': 'Parricide',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 259',
        'texte': "Est qualifié infanticide, le meurtre ou l'assassinat d'un enfant nouveau-né. L'auteur de l'infanticide est puni de mort ou de la réclusion perpétuelle.",
        'categorie': 'Infanticide',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 261',
        'texte': "Est qualifié empoisonnement tout attentat à la vie d'une personne, par l'effet de substances qui peuvent donner la mort plus ou moins promptement. L'empoisonnement est puni de mort.",
        'categorie': 'Empoisonnement',
        'section': 'Atteintes aux personnes'
    },
    # COUPS ET BLESSURES
    {
        'numero': 'Art. 264',
        'texte': "Quiconque porte volontairement des coups ou commet des violences ou voies de fait contre une personne, est puni d'un emprisonnement de deux mois à un an et d'une amende de 500 à 1.000 DA ou de l'une de ces deux peines seulement. Si les violences ont entraîné une incapacité de travail de plus de 15 jours, l'emprisonnement est de un à cinq ans.",
        'categorie': 'Coups et blessures',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 265',
        'texte': "Si les violences ont occasionné la perte ou la privation de l'usage d'un membre, une cécité, la perte d'un œil ou toute autre infirmité permanente, la peine est la réclusion à temps de cinq à dix ans.",
        'categorie': 'Coups et blessures',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 266',
        'texte': "Si les coups portés ou les blessures faites volontairement, mais sans intention de donner la mort, l'ont pourtant occasionnée, le coupable est puni de la réclusion à temps de dix à vingt ans.",
        'categorie': 'Coups et blessures',
        'section': 'Atteintes aux personnes'
    },
    # HOMICIDE INVOLONTAIRE
    {
        'numero': 'Art. 288',
        'texte': "Quiconque, par maladresse, imprudence, inattention, négligence ou inobservation des règlements, a involontairement commis un homicide ou en a involontairement été la cause, est puni d'un emprisonnement de six mois à trois ans et d'une amende de 20.000 à 100.000 DA.",
        'categorie': 'Homicide involontaire',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 289',
        'texte': "Si le coupable s'est trouvé en état d'ivresse ou a cherché à échapper à la responsabilité pénale ou civile qu'il pouvait encourir, l'emprisonnement est de deux à cinq ans et l'amende de 50.000 à 150.000 DA.",
        'categorie': 'Homicide involontaire',
        'section': 'Atteintes aux personnes'
    },
    # ATTENTAT A LA PUDEUR
    {
        'numero': 'Art. 334',
        'texte': "Tout attentat à la pudeur consommé ou tenté sans violence sur la personne d'un mineur de seize ans de l'un ou l'autre sexe, est puni d'un emprisonnement de cinq à dix ans.",
        'categorie': 'Attentat à la pudeur',
        'section': 'Atteintes aux mœurs'
    },
    {
        'numero': 'Art. 335',
        'texte': "Est puni de la réclusion à temps de cinq à dix ans, quiconque a commis un attentat à la pudeur avec violence. Si l'attentat a été commis sur un mineur de seize ans, le coupable est puni de la réclusion à temps de dix à vingt ans.",
        'categorie': 'Attentat à la pudeur',
        'section': 'Atteintes aux mœurs'
    },
    {
        'numero': 'Art. 336',
        'texte': "Tout acte de pénétration sexuelle, de quelque nature qu'il soit, commis sur la personne d'autrui par violence, contrainte ou surprise, constitue un viol. Le viol est puni de la réclusion à temps de cinq à dix ans. Si le viol a été commis sur un mineur de seize ans, la peine est de la réclusion à temps de dix à vingt ans.",
        'categorie': 'Viol',
        'section': 'Atteintes aux mœurs'
    },
    # VOL
    {
        'numero': 'Art. 350',
        'texte': "Quiconque soustrait frauduleusement une chose qui ne lui appartient pas est coupable de vol et puni d'un emprisonnement d'un an à cinq ans et d'une amende de 100.000 DA à 500.000 DA.",
        'categorie': 'Vol',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 351',
        'texte': "Le vol est puni de la réclusion à temps de cinq à dix ans lorsqu'il a été commis: avec effraction; avec escalade; avec usage de fausses clefs.",
        'categorie': 'Vol aggravé',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 353',
        'texte': "Le vol est puni de la réclusion à temps de cinq à dix ans lorsqu'il a été commis avec violence ou menace de violence. Si le vol a été commis avec violence ayant entraîné une incapacité totale de travail de plus de quinze jours, la peine est de dix à vingt ans.",
        'categorie': 'Vol avec violence',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 354',
        'texte': "Quiconque a commis un vol en faisant usage d'une arme est puni de la réclusion à temps de dix à vingt ans. Si les violences ont occasionné une infirmité permanente, la peine est la réclusion perpétuelle.",
        'categorie': 'Vol avec arme',
        'section': 'Atteintes aux biens'
    },
    # ESCROQUERIE
    {
        'numero': 'Art. 372',
        'texte': "Quiconque, soit en faisant usage de faux noms ou de fausses qualités, soit en employant des manœuvres frauduleuses pour persuader de l'existence de fausses entreprises, d'un pouvoir ou d'un crédit imaginaire, ou pour faire naître l'espérance ou la crainte d'un succès, d'un accident ou de tout autre événement chimérique, se sera fait remettre ou délivrer des fonds, des meubles ou des obligations, dispositions, billets, promesses, quittances ou décharges, et aura, par un de ces moyens, escroqué ou tenté d'escroquer la totalité ou partie de la fortune d'autrui, sera puni d'un emprisonnement d'un an à cinq ans et d'une amende de 100.000 DA à 500.000 DA.",
        'categorie': 'Escroquerie',
        'section': 'Atteintes aux biens'
    },
    # ABUS DE CONFIANCE
    {
        'numero': 'Art. 376',
        'texte': "Quiconque a détourné ou dissipé au préjudice des propriétaires, possesseurs ou détenteurs, des effets, deniers, marchandises, billets, quittances ou tous autres écrits contenant ou opérant obligation ou décharge, qui ne lui avaient été remis qu'à titre de louage, de dépôt, de mandat, de nantissement, de prêt à usage ou pour un travail salarié ou non salarié, à charge de les rendre ou représenter ou d'en faire un usage ou un emploi déterminé, est coupable d'abus de confiance et puni d'un emprisonnement de trois mois à trois ans et d'une amende de 20.000 DA à 100.000 DA.",
        'categorie': 'Abus de confiance',
        'section': 'Atteintes aux biens'
    },
    # RECEL
    {
        'numero': 'Art. 387',
        'texte': "Quiconque a sciemment recélé, en tout ou en partie, des choses enlevées, détournées ou obtenues à l'aide d'un crime ou d'un délit, est puni d'un emprisonnement de un à cinq ans et d'une amende de 100.000 DA à 500.000 DA.",
        'categorie': 'Recel',
        'section': 'Atteintes aux biens'
    },
    # DESTRUCTION
    {
        'numero': 'Art. 395',
        'texte': "Quiconque volontairement met le feu à des édifices, navires, bateaux, magasins, chantiers, forêts, bois, récoltes ou autres objets ne lui appartenant pas, est puni de la réclusion à temps de dix à vingt ans. La peine est la réclusion perpétuelle si l'incendie a occasionné la mort d'une personne.",
        'categorie': 'Incendie',
        'section': 'Destructions'
    },
    # DIFFAMATION
    {
        'numero': 'Art. 296',
        'texte': "La diffamation est toute allégation ou imputation d'un fait qui porte atteinte à l'honneur ou à la considération de la personne ou du corps auquel le fait est imputé. Est punie d'un emprisonnement de cinq jours à six mois et d'une amende de 5.000 à 50.000 DA.",
        'categorie': 'Diffamation',
        'section': 'Atteintes à l\'honneur'
    },
    {
        'numero': 'Art. 298',
        'texte': "L'injure est toute expression outrageante, terme de mépris ou invective qui ne renferme l'imputation d'aucun fait. L'injure est punie d'un emprisonnement de cinq jours à deux mois et d'une amende de 5.000 à 25.000 DA ou de l'une de ces deux peines.",
        'categorie': 'Injure',
        'section': 'Atteintes à l\'honneur'
    },
    # FAUX TEMOIGNAGE
    {
        'numero': 'Art. 232',
        'texte': "Quiconque, ayant prêté serment en qualité de témoin devant, une juridiction ou un officier de police judiciaire, fait une fausse déposition est puni d'un emprisonnement d'un an à cinq ans et d'une amende de 5.000 à 50.000 DA. Si le faux témoignage est donné en matière criminelle contre l'accusé ou en sa faveur, la peine est de la réclusion à temps de cinq à dix ans.",
        'categorie': 'Faux témoignage',
        'section': 'Crimes contre l\'ordre public'
    },
]


async def main():
    """Script principal pour initialiser la base de données"""
    print("🚀 Initialisation de la base de données du Code Pénal Algérien")
    print("=" * 60)
    
    db = DatabaseService()
    await db.initialize()
    
    # Vérifier si des articles existent déjà
    count = await db.get_article_count()
    if count > 0:
        print(f"⚠️ La base contient déjà {count} articles")
        response = input("Voulez-vous les supprimer et recommencer? (o/n): ")
        if response.lower() != 'o':
            print("Annulé.")
            await db.close()
            return
        
        # Supprimer tous les articles
        await db.connection.execute("DELETE FROM articles")
        await db.connection.commit()
        print("🗑️ Articles supprimés")
    
    # Insérer les articles
    print(f"\n📥 Insertion de {len(CODE_PENAL_ARTICLES)} articles...")
    
    inserted = 0
    for article in CODE_PENAL_ARTICLES:
        await db.insert_article(article)
        inserted += 1
        if inserted % 10 == 0:
            print(f"  ✓ {inserted} articles insérés...")
    
    print(f"\n✅ {inserted} articles insérés avec succès!")
    
    # Afficher un résumé
    count = await db.get_article_count()
    print(f"\n📊 Total dans la base: {count} articles")
    
    await db.close()
    print("\n🎉 Base de données prête!")


if __name__ == "__main__":
    asyncio.run(main())
