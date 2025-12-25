"""
Script pour ajouter des articles supplémentaires au Code Pénal
Ajoute les articles manquants sans supprimer les existants
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.database import DatabaseService


# Articles supplémentaires du Code Pénal Algérien
ARTICLES_SUPPLEMENTAIRES = [
    # PERSONNES MORALES
    {
        'numero': 'Art. 18 bis',
        'texte': "Les peines encourues par la personne morale en matière criminelle et délictuelle sont: 1- L'amende dont le taux est d'une à cinq fois le maximum de l'amende prévue pour les personnes physiques. 2- Une ou plusieurs des peines suivantes: la dissolution de la personne morale; la fermeture de l'établissement pour une durée qui ne peut excéder cinq ans; l'exclusion des marchés publics pour une durée qui ne peut excéder cinq ans.",
        'categorie': 'Peines personnes morales',
        'section': 'Peines applicables aux personnes morales'
    },
    # INTERNEMENT PSYCHIATRIQUE
    {
        'numero': 'Art. 21',
        'texte': "L'internement judiciaire dans un établissement psychiatrique consiste dans le placement en un établissement approprié par une décision de justice, d'un individu en raison du trouble de ses facultés mentales existant au moment de la commission de l'infraction ou survenu postérieurement.",
        'categorie': 'Mesures de sûreté',
        'section': 'Mesures de sûreté'
    },
    {
        'numero': 'Art. 22',
        'texte': "Le placement judiciaire dans un établissement thérapeutique consiste en la mise sous surveillance dans un établissement approprié par décision d'une juridiction de jugement, d'un individu qui lui est déféré, lorsque la criminalité de l'intéressé apparait comme liée à cette intoxication.",
        'categorie': 'Mesures de sûreté',
        'section': 'Mesures de sûreté'
    },
    {
        'numero': 'Art. 23',
        'texte': "L'interdiction d'exercer une profession, une activité ou un art peut être prononcée contre les condamnés pour crime ou délit, lorsque la juridiction constate que l'infraction commise a une relation directe avec l'exercice de la profession. Cette interdiction est prononcée pour une période qui ne peut excéder dix ans.",
        'categorie': 'Mesures de sûreté',
        'section': 'Mesures de sûreté'
    },
    {
        'numero': 'Art. 24',
        'texte': "Lorsqu'une juridiction prononce contre un ascendant une condamnation pour crime ou pour délit commis sur la personne d'un de ses enfants mineurs et qu'elle déclare que le comportement habituel du condamné met ses enfants mineurs en danger physique ou moral, elle peut prononcer la déchéance de la puissance paternelle.",
        'categorie': 'Déchéance parentale',
        'section': 'Mesures de sûreté'
    },
    # CONCOURS D'INFRACTIONS
    {
        'numero': 'Art. 32',
        'texte': "Le fait unique susceptible de plusieurs qualifications doit être apprécié selon la plus grave d'entre elles.",
        'categorie': 'Concours d\'infractions',
        'section': 'L\'infraction'
    },
    {
        'numero': 'Art. 33',
        'texte': "L'accomplissement simultané ou successif de plusieurs infractions non séparées par une condamnation irrévocable, constitue le concours d'infractions.",
        'categorie': 'Concours d\'infractions',
        'section': 'L\'infraction'
    },
    {
        'numero': 'Art. 34',
        'texte': "En cas de concours de plusieurs crimes ou délits déférés simultanément à la même juridiction, il est prononcé une seule peine privative de liberté dont la durée ne peut dépasser le maximum de celle édictée par la loi pour la répression de l'infraction la plus grave.",
        'categorie': 'Concours d\'infractions',
        'section': 'L\'infraction'
    },
    # RECIDIVE
    {
        'numero': 'Art. 55',
        'texte': "Quiconque ayant été condamné pour crime à une peine supérieure ou égale à une année d'emprisonnement a, dans un délai de cinq années après l'expiration de cette peine, commis un délit ou un crime qui doit être puni de la peine d'emprisonnement, est condamné au maximum de la peine portée par la loi, et cette peine peut être élevée jusqu'au double.",
        'categorie': 'Récidive',
        'section': 'Individualisation de la peine'
    },
    {
        'numero': 'Art. 56',
        'texte': "Ceux qui, ayant été antérieurement condamnés à une peine d'emprisonnement de moindre durée, commettent le même délit dans les mêmes conditions de temps, sont condamnés à une peine d'emprisonnement qui ne peut être inférieure au double de celle précédemment prononcée.",
        'categorie': 'Récidive',
        'section': 'Individualisation de la peine'
    },
    # CRIMES D'ETAT - SUITE
    {
        'numero': 'Art. 62',
        'texte': "Est coupable de trahison et puni de mort, tout Algérien qui en temps de guerre: 1° Provoque des militaires ou des marins à passer au service d'une puissance étrangère; 2° Entretient des intelligences avec une puissance étrangère; 3° Entrave la circulation de matériel militaire; 4° Participe à une entreprise de démoralisation de l'armée.",
        'categorie': 'Trahison',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 63',
        'texte': "Est coupable de trahison et puni de mort, tout Algérien qui: 1° Livre à une puissance étrangère un renseignement, objet, document ou procédé qui doit être tenu secret dans l'intérêt de la défense nationale; 2° S'assure la possession d'un tel renseignement en vue de le livrer à une puissance étrangère.",
        'categorie': 'Trahison',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 65',
        'texte': "Est puni de la réclusion perpétuelle, quiconque, dans l'intention de les livrer à une puissance étrangère, rassemble des renseignements, objets, documents ou procédés dont la réunion et l'exploitation sont de nature à nuire à la défense nationale ou à l'économie nationale.",
        'categorie': 'Atteinte à la défense nationale',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 77',
        'texte': "L'attentat, dont le but a été, soit de détruire ou de changer le régime, soit d'exciter les citoyens ou habitants à s'armer contre l'autorité de l'Etat ou s'armer les uns contre les autres, soit à porter atteinte à l'intégrité du territoire national, est puni de la peine de mort.",
        'categorie': 'Attentat contre l\'Etat',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 78',
        'texte': "Le complot ayant pour but les crimes mentionnés à l'article 77, s'il a été suivi d'un acte commis ou commencé pour en préparer l'exécution, est puni de la réclusion à temps de dix à vingt ans. Si le complot n'a pas été suivi d'un acte, la peine est la réclusion de cinq à dix ans.",
        'categorie': 'Complot',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 80',
        'texte': "Ceux qui ont levé ou fait lever des troupes armées, engagé ou enrôlé des soldats ou leur ont fourni des armes ou munitions, sans ordre ou autorisation du pouvoir légitime, sont punis de la peine de mort.",
        'categorie': 'Troupes armées illégales',
        'section': 'Crimes contre la sûreté de l\'Etat'
    },
    {
        'numero': 'Art. 84',
        'texte': "Ceux qui ont commis un attentat dont le but a été de porter le massacre ou la dévastation dans une ou plusieurs communes, sont punis de mort.",
        'categorie': 'Massacre',
        'section': 'Crimes contre l\'Etat'
    },
    # TERRORISME - SUITE
    {
        'numero': 'Art. 87 bis 1',
        'texte': "Pour les actes terroristes, la peine encourue est: la peine de mort lorsque la peine prévue est la réclusion perpétuelle; la réclusion perpétuelle lorsque la peine prévue est la réclusion de dix à vingt ans; portée au double pour les autres peines.",
        'categorie': 'Terrorisme',
        'section': 'Crimes qualifiés d\'actes terroristes'
    },
    {
        'numero': 'Art. 87 bis 4',
        'texte': "Quiconque fait l'apologie, encourage ou finance, par quelque moyen que ce soit, des actes terroristes, est puni d'une peine de réclusion à temps de cinq à dix ans et d'une amende de 100.000 DA à 500.000 DA.",
        'categorie': 'Financement terrorisme',
        'section': 'Crimes qualifiés d\'actes terroristes'
    },
    {
        'numero': 'Art. 87 bis 7',
        'texte': "Quiconque détient, porte, commercialise, importe, exporte, fabrique ou utilise sans autorisation des armes prohibées ou des munitions est puni d'une peine de réclusion de dix à vingt ans et d'une amende de 500.000 DA à 1.000.000 DA.",
        'categorie': 'Armes prohibées',
        'section': 'Crimes qualifiés d\'actes terroristes'
    },
    # ATTROUPEMENTS
    {
        'numero': 'Art. 98',
        'texte': "Est punie d'un emprisonnement de deux mois à un an, toute personne non armée qui, faisant partie d'un attroupement armé ou non armé, ne l'a pas abandonné après la première sommation.",
        'categorie': 'Attroupements',
        'section': 'Crimes contre la paix publique'
    },
    {
        'numero': 'Art. 99',
        'texte': "Est puni d'un emprisonnement de six mois à trois ans quiconque, dans un attroupement ou au cours d'une manifestation, a été trouvé porteur d'une arme apparente ou cachée.",
        'categorie': 'Attroupements',
        'section': 'Crimes contre la paix publique'
    },
    {
        'numero': 'Art. 100',
        'texte': "Toute provocation directe à un attroupement non armé soit par discours proférés publiquement, soit par écrits ou imprimés affichés ou distribués, est punie d'un emprisonnement de deux mois à un an.",
        'categorie': 'Provocation',
        'section': 'Crimes contre la paix publique'
    },
    # ELECTIONS
    {
        'numero': 'Art. 102',
        'texte': "Lorsque par attroupement, voies de fait ou menaces, on a empêché un ou plusieurs citoyens d'exercer leurs droits électoraux, chacun des coupables est puni d'un emprisonnement de six mois à deux ans, et de l'interdiction du droit de voter et d'être éligible pendant un an à cinq ans.",
        'categorie': 'Fraude électorale',
        'section': 'Infractions électorales'
    },
    {
        'numero': 'Art. 104',
        'texte': "Est puni de la réclusion de cinq à dix ans, tout citoyen chargé dans un scrutin du dépouillement des bulletins qui falsifie ces bulletins, ou en soustrait, ou y ajoute, ou inscrit sur les bulletins des noms autres que ceux déclarés.",
        'categorie': 'Fraude électorale',
        'section': 'Infractions électorales'
    },
    {
        'numero': 'Art. 106',
        'texte': "Tout citoyen qui, à l'occasion des élections, a acheté ou vendu un suffrage à un prix quelconque, est puni d'interdiction des droits de citoyen et de toute fonction publique pendant un an à cinq ans.",
        'categorie': 'Achat de voix',
        'section': 'Infractions électorales'
    },
    # ATTEINTE AUX LIBERTES
    {
        'numero': 'Art. 107',
        'texte': "Lorsqu'un fonctionnaire a ordonné ou commis un acte arbitraire ou attentatoire à la liberté individuelle ou aux droits civiques d'un citoyen, il encourt une peine de réclusion de cinq à dix ans.",
        'categorie': 'Atteinte aux libertés',
        'section': 'Attentat à la liberté'
    },
    {
        'numero': 'Art. 110',
        'texte': "Tout agent d'établissement pénitentiaire qui a reçu un prisonnier sans titre régulier de détention ou a refusé de présenter ce prisonnier aux personnes habilitées, est coupable de détention arbitraire et puni d'un emprisonnement de six mois à deux ans.",
        'categorie': 'Détention arbitraire',
        'section': 'Attentat à la liberté'
    },
    # COALITION DE FONCTIONNAIRES
    {
        'numero': 'Art. 112',
        'texte': "Lorsque des mesures contraires aux lois ont été concertées par une réunion d'individus dépositaires de l'autorité publique, les coupables sont punis d'un emprisonnement d'un à six mois.",
        'categorie': 'Coalition fonctionnaires',
        'section': 'Coalition de fonctionnaires'
    },
    {
        'numero': 'Art. 115',
        'texte': "Tous magistrats et fonctionnaires qui ont, par délibération, arrêté de donner leur démission dans le but d'empêcher l'administration de la justice ou le fonctionnement d'un service public, sont punis d'un emprisonnement de six mois à trois ans.",
        'categorie': 'Démission concertée',
        'section': 'Coalition de fonctionnaires'
    },
    # EMPIETTEMENT
    {
        'numero': 'Art. 116',
        'texte': "Sont coupables de forfaiture et punis de la réclusion de cinq à dix ans: les magistrats qui se sont immiscés dans l'exercice de la fonction législative, soit par des règlements contenant des dispositions législatives, soit en arrêtant l'exécution des lois.",
        'categorie': 'Forfaiture',
        'section': 'Empiètement des autorités'
    },
    # CONCUSSION
    {
        'numero': 'Art. 121',
        'texte': "Tout fonctionnaire qui aura reçu, exigé ou ordonné de percevoir ce qu'il savait n'être pas dû ou excéder ce qui était dû pour droits, taxes, contributions, deniers ou salaires, est puni d'un emprisonnement de un à cinq ans et d'une amende de 50.000 à 200.000 DA.",
        'categorie': 'Concussion',
        'section': 'Détournements et concussions'
    },
    # TRAFIC D'INFLUENCE
    {
        'numero': 'Art. 128',
        'texte': "Est puni de la réclusion de deux à dix ans et d'une amende, quiconque, sans droit, reçoit des dons ou présents, sous prétexte de faire obtenir ou de tenter de faire obtenir des décorations, médailles ou distinctions.",
        'categorie': 'Trafic d\'influence',
        'section': 'Corruption et trafic d\'influence'
    },
    {
        'numero': 'Art. 129',
        'texte': "Est puni de la réclusion de cinq à dix ans, quiconque, sans droit, prend ou donne le titre d'intermédiaire pour la conclusion de marchés au profit d'une entreprise avec un établissement public.",
        'categorie': 'Marchés publics',
        'section': 'Corruption et trafic d\'influence'
    },
    # USURPATION DE FONCTION
    {
        'numero': 'Art. 141',
        'texte': "Quiconque s'est immiscé sans titre dans des fonctions publiques, civiles ou militaires, ou a fait les actes d'une de ces fonctions, est puni d'un emprisonnement de un à cinq ans et d'une amende de 10.000 à 50.000 DA.",
        'categorie': 'Usurpation de fonction',
        'section': 'Usurpation de fonctions'
    },
    {
        'numero': 'Art. 142',
        'texte': "Quiconque a publiquement porté un costume ou un uniforme officiel ou une décoration qui ne lui appartient pas, est puni d'un emprisonnement de six mois à deux ans.",
        'categorie': 'Port illégal d\'uniforme',
        'section': 'Usurpation de fonctions'
    },
    # ATTEINTE A L'AUTORITE DE LA JUSTICE
    {
        'numero': 'Art. 144',
        'texte': "Quiconque a outragé un magistrat, un fonctionnaire, un officier public ou un commandant de la force publique dans l'exercice de ses fonctions, est puni d'un emprisonnement de deux mois à deux ans et d'une amende de 10.000 à 100.000 DA.",
        'categorie': 'Outrage',
        'section': 'Atteinte à l\'autorité de la justice'
    },
    {
        'numero': 'Art. 148',
        'texte': "Toute personne qui a porté un coup ou a commis un acte de violence contre un magistrat, un juré, un avocat, un officier public dans l'exercice de ses fonctions, est punie d'un emprisonnement de deux à cinq ans.",
        'categorie': 'Violence sur magistrat',
        'section': 'Atteinte à l\'autorité de la justice'
    },
    # EVASION
    {
        'numero': 'Art. 188',
        'texte': "Tout individu qui, étant arrêté ou détenu légalement, s'évade ou tente de s'évader, est puni d'un emprisonnement de deux mois à trois ans.",
        'categorie': 'Évasion',
        'section': 'Évasion de détenus'
    },
    {
        'numero': 'Art. 189',
        'texte': "Lorsque l'évasion ou la tentative d'évasion a été effectuée avec violence ou menace ou bris de prison, la peine est un emprisonnement de deux à cinq ans.",
        'categorie': 'Évasion avec violence',
        'section': 'Évasion de détenus'
    },
    # FAUX EN ECRITURES
    {
        'numero': 'Art. 215',
        'texte': "Tout particulier qui a commis un faux en écriture authentique ou de commerce par l'un des moyens prévus à l'article 214, est puni de la réclusion à temps de cinq à dix ans.",
        'categorie': 'Faux en écritures',
        'section': 'Faux et usage de faux'
    },
    {
        'numero': 'Art. 216',
        'texte': "Quiconque, dans un document délivré par une administration publique aux fins de constater un droit, une identité ou une qualité, a falsifié cette pièce ou fait usage de cette pièce falsifiée, est puni d'un emprisonnement de six mois à trois ans.",
        'categorie': 'Falsification de documents',
        'section': 'Faux et usage de faux'
    },
    {
        'numero': 'Art. 218',
        'texte': "Est puni d'un emprisonnement de un à cinq ans et d'une amende de 20.000 à 100.000 DA, quiconque fait usage d'un acte ou d'une pièce qu'il sait fausse.",
        'categorie': 'Usage de faux',
        'section': 'Faux et usage de faux'
    },
    {
        'numero': 'Art. 219',
        'texte': "Est puni d'un emprisonnement de six mois à deux ans et d'une amende de 10.000 à 50.000 DA, quiconque s'est fait délivrer indûment un document administratif en faisant usage de fausses déclarations.",
        'categorie': 'Fausse déclaration',
        'section': 'Faux et usage de faux'
    },
    # FAUSSE MONNAIE
    {
        'numero': 'Art. 223',
        'texte': "Quiconque a participé sciemment à l'émission, la mise en circulation, la distribution de monnaies contrefaites, est puni de la réclusion à temps de cinq à vingt ans.",
        'categorie': 'Circulation fausse monnaie',
        'section': 'Fausse monnaie'
    },
    {
        'numero': 'Art. 226',
        'texte': "Quiconque a contrefait ou falsifié des timbres-poste ou des timbres fiscaux ou a fait usage de ces timbres, est puni d'un emprisonnement de deux à cinq ans et d'une amende de 20.000 à 100.000 DA.",
        'categorie': 'Faux timbres',
        'section': 'Fausse monnaie'
    },
    # FAUX SERMENT
    {
        'numero': 'Art. 231',
        'texte': "Quiconque a fait un faux serment en matière civile ou commerciale, est puni d'un emprisonnement de un à cinq ans et d'une amende de 10.000 à 50.000 DA.",
        'categorie': 'Faux serment',
        'section': 'Faux témoignage et faux serment'
    },
    # DENONCIATION CALOMNIEUSE
    {
        'numero': 'Art. 300',
        'texte': "Quiconque a, par quelque moyen que ce soit, fait une dénonciation calomnieuse contre un ou plusieurs individus aux officiers de police judiciaire ou à une autorité ayant le pouvoir d'y donner suite, est puni d'un emprisonnement de six mois à cinq ans et d'une amende de 10.000 à 50.000 DA.",
        'categorie': 'Dénonciation calomnieuse',
        'section': 'Atteintes à l\'honneur'
    },
    # NON-REPRESENTATION D'ENFANT
    {
        'numero': 'Art. 328',
        'texte': "Quiconque, étant condamné à payer une pension alimentaire à son conjoint, à ses ascendants ou descendants, sera demeuré plus de deux mois sans acquitter les termes de cette pension, sera puni d'un emprisonnement de six mois à trois ans.",
        'categorie': 'Abandon de famille',
        'section': 'Abandon de famille'
    },
    {
        'numero': 'Art. 329',
        'texte': "Est puni d'un emprisonnement de un mois à un an et d'une amende de 5.000 à 50.000 DA, le père ou la mère qui abandonne, sans motif grave, pendant plus de deux mois, la résidence familiale et se soustrait à tout ou partie de ses obligations.",
        'categorie': 'Abandon de famille',
        'section': 'Abandon de famille'
    },
    {
        'numero': 'Art. 330',
        'texte': "Le père ou la mère de famille qui expose ses enfants mineurs à des mauvais traitements habituel compromettant leur santé ou leur moralité, est puni d'un emprisonnement de un à trois ans.",
        'categorie': 'Mauvais traitements',
        'section': 'Abandon de famille'
    },
    # ENLEVEMENT
    {
        'numero': 'Art. 293',
        'texte': "Est puni de la réclusion à temps de dix à vingt ans, quiconque, par violence, menace ou fraude, enlève ou fait enlever, arrête ou fait arrêter, détient ou fait détenir une personne quelconque.",
        'categorie': 'Enlèvement',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 293 bis',
        'texte': "Est puni de la réclusion perpétuelle, quiconque demande, pour la libération de la personne enlevée, arrêtée ou détenue, une rançon ou l'exécution d'un ordre ou d'une condition.",
        'categorie': 'Enlèvement avec rançon',
        'section': 'Atteintes aux personnes'
    },
    {
        'numero': 'Art. 294',
        'texte': "Si la personne enlevée, arrêtée ou détenue a été soumise à des tortures corporelles, la peine est la réclusion perpétuelle. Si l'enlèvement a été suivi de mort, la peine est la mort.",
        'categorie': 'Enlèvement avec torture',
        'section': 'Atteintes aux personnes'
    },
    # ENLÈVEMENT DE MINEURS
    {
        'numero': 'Art. 326',
        'texte': "Quiconque, par fraude ou violence, enlève ou fait enlever des mineurs de moins de dix-huit ans, des lieux où ils étaient placés par ceux à l'autorité desquels ils étaient soumis, est puni de la réclusion à temps de cinq à dix ans.",
        'categorie': 'Enlèvement de mineur',
        'section': 'Atteintes aux mineurs'
    },
    {
        'numero': 'Art. 327',
        'texte': "Si le mineur enlevé a moins de dix-huit ans et a été enlevé ou détourné, même sans violence ni menace, il sera applicable la réclusion à temps de dix à vingt ans.",
        'categorie': 'Enlèvement de mineur',
        'section': 'Atteintes aux mineurs'
    },
    # ATTEINTES AUX MOEURS - SUITE  
    {
        'numero': 'Art. 337',
        'texte': "Si le viol a été commis par plusieurs personnes, par un ascendant, par une personne ayant autorité, ou avec usage d'une arme, la peine est la réclusion perpétuelle.",
        'categorie': 'Viol aggravé',
        'section': 'Atteintes aux mœurs'
    },
    {
        'numero': 'Art. 338',
        'texte': "Tout acte d'homosexualité est puni d'un emprisonnement de deux mois à deux ans.",
        'categorie': 'Homosexualité',
        'section': 'Atteintes aux mœurs'
    },
    {
        'numero': 'Art. 339',
        'texte': "L'adultère est puni d'un emprisonnement de un à deux ans. La poursuite n'a lieu que sur plainte du conjoint offensé.",
        'categorie': 'Adultère',
        'section': 'Atteintes aux mœurs'
    },
    # PROSTITUTION
    {
        'numero': 'Art. 343',
        'texte': "Est puni d'un emprisonnement de deux à cinq ans et d'une amende de 10.000 à 100.000 DA, quiconque, habituellement, excite, favorise ou facilite la débauche ou la corruption des mineurs de l'un ou l'autre sexe.",
        'categorie': 'Corruption de mineurs',
        'section': 'Prostitution'
    },
    {
        'numero': 'Art. 344',
        'texte': "Est puni d'un emprisonnement de deux à cinq ans et d'une amende de 10.000 à 100.000 DA, quiconque aide, assiste ou protège la prostitution d'autrui.",
        'categorie': 'Proxénétisme',
        'section': 'Prostitution'
    },
    {
        'numero': 'Art. 346',
        'texte': "Quiconque a, en vue de la prostitution d'autrui, embauchée, entraînée ou détournée une personne, est puni d'un emprisonnement de un à cinq ans et d'une amende de 5.000 à 50.000 DA.",
        'categorie': 'Traite des personnes',
        'section': 'Prostitution'
    },
    # JEUX DE HASARD
    {
        'numero': 'Art. 355',
        'texte': "Quiconque aura tenu une maison de jeux de hasard et y aura admis le public, est puni d'un emprisonnement de deux mois à un an et d'une amende de 5.000 à 100.000 DA.",
        'categorie': 'Jeux de hasard',
        'section': 'Atteintes aux biens'
    },
    # VOL - SUITE
    {
        'numero': 'Art. 352',
        'texte': "Le vol est puni de la réclusion à temps de dix à vingt ans lorsqu'il a été commis avec deux ou plusieurs des circonstances prévues aux articles 351 et 353, ou la nuit dans un lieu habité.",
        'categorie': 'Vol très aggravé',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 356',
        'texte': "Quiconque a détruit, supprimé, diverti ou falsifié des lettres confiées à la poste, ou a facilité la soustraction desdites lettres, est puni d'un emprisonnement de trois mois à cinq ans.",
        'categorie': 'Vol de courrier',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 361',
        'texte': "Le vol commis par un domestique ou un salarié au préjudice de son maître ou patron, est puni d'un emprisonnement de deux à cinq ans.",
        'categorie': 'Vol domestique',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 362',
        'texte': "Le vol commis dans un hôtel, dans une voiture ou par un voiturier est puni d'un emprisonnement de deux à cinq ans.",
        'categorie': 'Vol hôtel/transport',
        'section': 'Atteintes aux biens'
    },
    # EXTORSION
    {
        'numero': 'Art. 370',
        'texte': "Quiconque a extorqué par force, violence ou contrainte, la signature ou la remise d'un écrit, d'un acte, d'un titre, d'une pièce quelconque contenant ou opérant obligation, disposition ou décharge, est puni de la réclusion à temps de cinq à dix ans.",
        'categorie': 'Extorsion',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 371',
        'texte': "Quiconque a extorqué de la même manière des fonds ou valeurs, est puni de la réclusion à temps de dix à vingt ans.",
        'categorie': 'Extorsion de fonds',
        'section': 'Atteintes aux biens'
    },
    # CHANTAGE
    {
        'numero': 'Art. 373',
        'texte': "Est puni d'un emprisonnement de un à cinq ans et d'une amende de 10.000 à 100.000 DA, quiconque a, par écrit anonyme ou signé, par menace verbale ou révélation, extorqué ou tenté d'extorquer des fonds ou valeurs.",
        'categorie': 'Chantage',
        'section': 'Atteintes aux biens'
    },
    # BANQUEROUTE
    {
        'numero': 'Art. 383',
        'texte': "Tout commerçant en état de cessation de paiements qui s'est rendu coupable de banqueroute frauduleuse, est puni de la réclusion à temps de cinq à dix ans.",
        'categorie': 'Banqueroute',
        'section': 'Atteintes aux biens'
    },
    # DESTRUCTION
    {
        'numero': 'Art. 396',
        'texte': "La peine est la réclusion perpétuelle si l'incendie a été commis dans des lieux habités ou servant à l'habitation. La peine est de mort si l'incendie a causé la mort d'une personne.",
        'categorie': 'Incendie aggravé',
        'section': 'Destructions'
    },
    {
        'numero': 'Art. 400',
        'texte': "Quiconque a volontairement détruit ou endommagé, par tout moyen, les biens mobiliers ou immobiliers d'autrui est puni d'un emprisonnement d'un à cinq ans et d'une amende de 20.000 à 100.000 DA.",
        'categorie': 'Destruction de biens',
        'section': 'Destructions'
    },
    {
        'numero': 'Art. 401',
        'texte': "Quiconque a détruit, abattu, mutilé ou dégradé des monuments, statues et autres objets destinés à l'utilité ou à la décoration publique, est puni d'un emprisonnement de un mois à deux ans.",
        'categorie': 'Destruction monuments',
        'section': 'Destructions'
    },
    # CRUAUTE ENVERS LES ANIMAUX
    {
        'numero': 'Art. 449',
        'texte': "Quiconque aura publiquement exercé de mauvais traitements envers un animal domestique ou apprivoisé, est puni d'une amende de 500 à 1.000 DA et d'un emprisonnement de dix jours à deux mois.",
        'categorie': 'Cruauté animaux',
        'section': 'Contraventions'
    },
    # VAGABONDAGE
    {
        'numero': 'Art. 195',
        'texte': "Le vagabondage est puni d'un emprisonnement de un à six mois. Sont réputés vagabonds ceux qui n'ont ni domicile certain ni moyens de subsistance et qui n'exercent habituellement ni métier ni profession.",
        'categorie': 'Vagabondage',
        'section': 'Vagabondage et mendicité'
    },
    {
        'numero': 'Art. 197',
        'texte': "Toute personne valide qui aura été trouvée mendiant sera punie d'un emprisonnement de un à six mois.",
        'categorie': 'Mendicité',
        'section': 'Vagabondage et mendicité'
    },
    # STUPEFIANTS
    {
        'numero': 'Art. 241',
        'texte': "Sont punis de la réclusion à temps de dix à vingt ans et d'une amende de 5.000.000 à 50.000.000 DA, ceux qui ont contrevenu aux dispositions législatives et réglementaires concernant la production, la fabrication, le commerce, la distribution de substances ou de plantes vénéneuses ou de stupéfiants.",
        'categorie': 'Trafic de stupéfiants',
        'section': 'Stupéfiants'
    },
    {
        'numero': 'Art. 243',
        'texte': "Quiconque aura facilité à autrui l'usage de substances ou de plantes vénéneuses classées comme stupéfiants, est puni d'un emprisonnement de deux à dix ans.",
        'categorie': 'Facilitation usage stupéfiants',
        'section': 'Stupéfiants'
    },
    {
        'numero': 'Art. 248',
        'texte': "Est punie d'un emprisonnement de deux mois à un an, toute personne qui aura fait usage de manière illicite de l'une des substances ou plantes classées comme stupéfiants.",
        'categorie': 'Usage de stupéfiants',
        'section': 'Stupéfiants'
    },
    # EXERCICE ILLEGAL DE LA MEDECINE
    {
        'numero': 'Art. 243 bis',
        'texte': "Est puni d'un emprisonnement de un à cinq ans et d'une amende, quiconque, sans être titulaire d'un diplôme requis pour l'exercice de la médecine, se livre habituellement à des actes de diagnostic ou de traitement médical.",
        'categorie': 'Exercice illégal médecine',
        'section': 'Exercice illégal professions'
    },
    # ATTEINTE A LA VIE PRIVEE
    {
        'numero': 'Art. 303',
        'texte': "Est puni d'un emprisonnement de six mois à trois ans et d'une amende de 50.000 à 300.000 DA, quiconque, volontairement, porte atteinte à l'intimité de la vie privée d'autrui.",
        'categorie': 'Atteinte vie privée',
        'section': 'Atteintes à la vie privée'
    },
    {
        'numero': 'Art. 303 bis',
        'texte': "Est puni d'un emprisonnement de six mois à trois ans et d'une amende de 50.000 à 300.000 DA, quiconque enregistre ou transmet, sans consentement, des paroles ou images d'une personne dans un lieu privé.",
        'categorie': 'Enregistrement illégal',
        'section': 'Atteintes à la vie privée'
    },
    # VIOLATION DE DOMICILE
    {
        'numero': 'Art. 295',
        'texte': "Tout individu qui s'introduit à l'aide de menaces ou de voies de fait, dans le domicile d'un citoyen, est puni d'un emprisonnement de un à cinq ans.",
        'categorie': 'Violation de domicile',
        'section': 'Atteintes aux personnes'
    },
    # SECRET PROFESSIONNEL
    {
        'numero': 'Art. 301',
        'texte': "Les médecins, chirurgiens et autres officiers de santé, ainsi que les pharmaciens, les sages-femmes et toutes autres personnes dépositaires, par état ou profession, des secrets qu'on leur confie, qui, hors le cas où la loi les oblige à se porter dénonciateurs, ont révélé ces secrets, sont punis d'un emprisonnement de un à six mois et d'une amende de 5.000 à 50.000 DA.",
        'categorie': 'Secret professionnel',
        'section': 'Secret professionnel'
    },
    # CHEQUES SANS PROVISION
    {
        'numero': 'Art. 374',
        'texte': "Est puni d'un emprisonnement de un à cinq ans et d'une amende égale au montant du chèque ou de l'insuffisance de la provision, quiconque, de mauvaise foi, a émis un chèque sans provision préalable et disponible.",
        'categorie': 'Chèque sans provision',
        'section': 'Atteintes aux biens'
    },
    {
        'numero': 'Art. 375',
        'texte': "Est puni des mêmes peines, quiconque, après avoir émis un chèque, a, de mauvaise foi, retiré tout ou partie de la provision ou fait défense au tiré de payer.",
        'categorie': 'Opposition frauduleuse',
        'section': 'Atteintes aux biens'
    },
]


async def main():
    """Ajoute les articles supplémentaires à la base de données"""
    print("🚀 Ajout d'articles supplémentaires au Code Pénal")
    print("=" * 60)
    
    db = DatabaseService()
    await db.initialize()
    
    # Compter les articles existants
    count_before = await db.get_article_count()
    print(f"📊 Articles actuels: {count_before}")
    
    # Insérer les nouveaux articles
    print(f"\n📥 Ajout de {len(ARTICLES_SUPPLEMENTAIRES)} nouveaux articles...")
    
    inserted = 0
    for article in ARTICLES_SUPPLEMENTAIRES:
        await db.insert_article(article)
        inserted += 1
        if inserted % 20 == 0:
            print(f"  ✓ {inserted} articles ajoutés...")
    
    # Afficher le total
    count_after = await db.get_article_count()
    print(f"\n✅ {inserted} articles ajoutés!")
    print(f"📊 Total maintenant: {count_after} articles")
    
    await db.close()
    print("\n🎉 Base de données mise à jour!")


if __name__ == "__main__":
    asyncio.run(main())
