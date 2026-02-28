#!/usr/bin/env python3
"""Generate the complete questions + flashcards data for PSY0 Training App V2."""
import json, re

# --- PARSE EXISTING TEX FILES ---
def parse_answers(content):
    answers = {}
    for m in re.finditer(r'(\d+)\s*&\s*([abcd])', content):
        answers[int(m.group(1))] = m.group(2)
    return answers

def parse_questions(content, answers):
    questions = []
    items = re.split(r'\\item\s+', content)
    q_counter = 1
    for item in items[1:]:
        if '\\\\ a)' in item or '\\\\a)' in item or '\n a)' in item:
            q_match = re.search(r'^(.*?)(?:\\\\|\n)\s*a\)', item, re.DOTALL)
            if q_match:
                qt = q_match.group(1).strip().replace('\\textbf{','').replace('}','').replace('\\quad','').strip()
                opts = {}
                for letter in 'abcd':
                    nxt = chr(ord(letter)+1) if letter != 'd' else None
                    if nxt:
                        m = re.search(fr'{letter}\)\s*(.*?)(?:\s*\\quad\s*{nxt}\)|\s*{nxt}\))', item)
                    else:
                        m = re.search(fr'{letter}\)\s*(.*?)(?:\n|$)', item)
                    if m:
                        opts[letter] = m.group(1).strip().replace('\\quad','').strip()
                if len(opts)==4 and q_counter in answers:
                    questions.append({"id":q_counter,"question":qt,
                        "options":[{"id":l,"text":opts[l]} for l in 'abcd'],
                        "answer":answers[q_counter],"explanation":"","category":""})
                    q_counter += 1
    return questions

# Parse main QCM
with open("/Users/maximeleboeuf/Cadet AF/qcm_psy0.tex",'r') as f: c1=f.read()
a1 = parse_answers(c1)
q1 = parse_questions(c1, a1)

# Parse supplement
with open("/Users/maximeleboeuf/Cadet AF/supplement_psy0.tex",'r') as f: c2=f.read()
a2 = parse_answers(c2)
q2 = parse_questions(c2, a2)

all_q = q1 + q2

# --- ASSIGN CATEGORIES ---
cat_map = {
    range(1,21): "Histoire",
    range(21,41): "Air France & Flotte",
    range(41,61): "Technique de Vol",
    range(61,81): "Navigation & Météo",
    range(81,101): "Divers & Approfondissement",
    range(101,121): "ETOPS, CRM & Systèmes",
}
for q in all_q:
    for r, cat in cat_map.items():
        if q["id"] in r:
            q["category"] = cat
            break

# --- ADD EXPLANATIONS TO KEY QUESTIONS ---
explanations = {
    1: "Clément Ader a réalisé le premier décollage motorisé avec l'Éole en 1890 (~50m, non contrôlé). Il a inventé le mot « avion ».",
    2: "Air France a été créée le 7 octobre 1933 par fusion de 5 compagnies : Air Orient, Air Union, CIDNA, Lignes Farman (SGTA) et Aéropostale.",
    3: "Louis Blériot a traversé la Manche le 25 juillet 1909 en 37 minutes avec le Blériot XI.",
    5: "Jean Mermoz a disparu en 1936 à bord du Latécoère 300 « Croix du Sud » au-dessus de l'Atlantique Sud.",
    7: "Le Concorde a effectué son premier vol le 2 mars 1969 à Toulouse. Programme franco-britannique.",
    8: "Charles Lindbergh a réalisé la première traversée solo de l'Atlantique Nord sans escale en 1927 (NY → Paris, Spirit of St. Louis, 33h30).",
    12: "La Convention de Chicago de 1944 a créé l'OACI (Organisation de l'Aviation Civile Internationale).",
    21: "Benjamin Smith est DG du Groupe AF-KLM depuis août 2018. Anne Rigail est DG d'Air France (première femme au poste).",
    22: "L'emblème d'Air France est l'hippocampe ailé (surnommé « la crevette »), hérité d'Air Orient.",
    25: "Le B777 est équipé du GE90, le moteur le plus puissant au monde (115 000 lb de poussée pour la version -115B).",
    34: "Le Concorde volait à Mach 2.02 (~2 180 km/h), plafond 18 300m. Paris-NY en 3h30.",
    37: "CFM International est une joint-venture entre GE (USA) et Safran (France). Le CFM56 est le moteur le plus vendu au monde (+35 000 exemplaires).",
    42: "Le décrochage se produit toujours à la même incidence critique (~15-18°), indépendamment de la vitesse, du poids ou de l'altitude.",
    44: "ASSIETTE = PENTE + INCIDENCE. L'assiette est l'angle entre l'axe de l'avion et l'horizontale.",
    47: "7500 = Détournement (hijack). Mnémo : « 75 = someone's taken alive ». 7600 = panne radio. 7700 = urgence.",
    49: "Turboréacteur : Fan → Compresseur → Chambre de Combustion → Turbine → Tuyère.",
    52: "L'A320 vole en croisière à Mach 0.78 (828 km/h). C'est le premier avion civil fly-by-wire d'Airbus (1988).",
    55: "Prise statique bouchée : l'altimètre se bloque, le variomètre se bloque à zéro, le badin sous-estime en montée et surestime en descente.",
    63: "ISA au niveau de la mer : 15°C, 1013.25 hPa. Gradient : -2°C par 1000 ft.",
    65: "Gradient ISA = -2°C / 1000 ft. À 10 000 ft → -5°C, à 36 000 ft → -56.5°C (tropopause).",
    67: "L'ILS fournit un guidage horizontal (Localizer, VHF) ET vertical (Glide Slope, UHF, pente de 3°).",
    83: "Le vol NY→Paris est plus rapide grâce au jet stream (courant de 150-300 kt à la tropopause, d'ouest en est).",
    101: "ETOPS-180 (3h sur 1 moteur) couvre ~95% du globe. L'A350 est certifié ETOPS-370 (6h10).",
    105: "Le CRM a été développé après l'accident de Tenerife en 1977 (583 morts, le plus meurtrier de l'histoire).",
    106: "Le modèle de Reason (fromage suisse) : un accident survient quand les trous de toutes les couches de défense s'alignent.",
    110: "Numéro de piste = cap magnétique arrondi à la dizaine, divisé par 10. Cap 270° → piste 27.",
    111: "PAPI : 4 rouges = trop bas (danger!). 4 blancs = trop haut. 2 rouges + 2 blancs = correct (plan 3°).",
    113: "MAYDAY (×3) = détresse vitale. PAN PAN (×3) = urgence non vitale. Ne jamais dire « repeat » → dire « say again ».",
}
for q in all_q:
    if q["id"] in explanations:
        q["explanation"] = explanations[q["id"]]

# --- ADD 80 NEW QUESTIONS FROM REVISION GUIDE ---
new_questions = [
    {"id":121,"question":"Qui a inventé le manche à balai et les ailerons ?","options":[{"id":"a","text":"Blériot"},{"id":"b","text":"Esnault-Pelterie"},{"id":"c","text":"Ader"},{"id":"d","text":"Wright"}],"answer":"b","category":"Histoire","explanation":"Robert Esnault-Pelterie invente le manche à balai et les ailerons en 1905."},
    {"id":122,"question":"Premier vol autonome (décollage sans rampe) ?","options":[{"id":"a","text":"Ader"},{"id":"b","text":"Wright"},{"id":"c","text":"Vuia"},{"id":"d","text":"Santos-Dumont"}],"answer":"c","category":"Histoire","explanation":"Traian Vuia a réalisé le premier vol autonome en 1906."},
    {"id":123,"question":"Premier looping en avion ?","options":[{"id":"a","text":"Garros"},{"id":"b","text":"Pégoud"},{"id":"c","text":"Blériot"},{"id":"d","text":"Guynemer"}],"answer":"b","category":"Histoire","explanation":"Adolphe Pégoud a réalisé le premier looping en avion en 1913."},
    {"id":124,"question":"As français aux 75 victoires en WWI ?","options":[{"id":"a","text":"Guynemer"},{"id":"b","text":"Fonck"},{"id":"c","text":"Garros"},{"id":"d","text":"Richthofen"}],"answer":"b","category":"Histoire","explanation":"René Fonck est le top as allié avec 75 victoires. Guynemer en a 54."},
    {"id":125,"question":"Plus ancienne compagnie aérienne encore en activité ?","options":[{"id":"a","text":"Air France"},{"id":"b","text":"Lufthansa"},{"id":"c","text":"KLM"},{"id":"d","text":"Qantas"}],"answer":"c","category":"Histoire","explanation":"KLM a été créée le 7 octobre 1919."},
    {"id":126,"question":"Première traversée Atlantique Nord sans escale (1919) ?","options":[{"id":"a","text":"Lindbergh"},{"id":"b","text":"Alcock & Brown"},{"id":"c","text":"Mermoz"},{"id":"d","text":"Earhart"}],"answer":"b","category":"Histoire","explanation":"Alcock & Brown : Terre-Neuve → Irlande en 1919 (pas en solo)."},
    {"id":127,"question":"Catastrophe du dirigeable Hindenburg ?","options":[{"id":"a","text":"1933"},{"id":"b","text":"1935"},{"id":"c","text":"1937"},{"id":"d","text":"1939"}],"answer":"c","category":"Histoire","explanation":"1937 à Lakehurst (USA), fin de l'ère des dirigeables."},
    {"id":128,"question":"Premier vol à réaction (1939) ?","options":[{"id":"a","text":"Me 262"},{"id":"b","text":"Heinkel He 178"},{"id":"c","text":"Gloster Meteor"},{"id":"d","text":"Bell X-1"}],"answer":"b","category":"Histoire","explanation":"Heinkel He 178, turboréacteur Von Ohain, Allemagne."},
    {"id":129,"question":"Création de la NASA ?","options":[{"id":"a","text":"1945"},{"id":"b","text":"1952"},{"id":"c","text":"1958"},{"id":"d","text":"1961"}],"answer":"c","category":"Histoire","explanation":"La NASA a été créée en 1958."},
    {"id":130,"question":"Record d'altitude du X-15 ?","options":[{"id":"a","text":"50 000 m"},{"id":"b","text":"85 000 m"},{"id":"c","text":"107 960 m"},{"id":"d","text":"150 000 m"}],"answer":"c","category":"Histoire","explanation":"Le X-15 a atteint 107 960 m et Mach 6.72."},
    {"id":131,"question":"Siège social d'Air France ?","options":[{"id":"a","text":"Paris 8e"},{"id":"b","text":"Tremblay-en-France"},{"id":"c","text":"Roissy-ville"},{"id":"d","text":"Orly"}],"answer":"b","category":"Air France & Flotte","explanation":"Le siège est à Tremblay-en-France (Roissy-CDG)."},
    {"id":132,"question":"Code IATA d'Air France ?","options":[{"id":"a","text":"AFR"},{"id":"b","text":"AF"},{"id":"c","text":"AIF"},{"id":"d","text":"FRA"}],"answer":"b","category":"Air France & Flotte","explanation":"AF = code IATA. AFR = code OACI."},
    {"id":133,"question":"Indicatif radio d'Air France ?","options":[{"id":"a","text":"AIR FRANCE"},{"id":"b","text":"SPEEDBIRD"},{"id":"c","text":"FRENCH AIR"},{"id":"d","text":"AIRFRANS"}],"answer":"a","category":"Air France & Flotte","explanation":"L'indicatif radio est simplement « AIR FRANCE »."},
    {"id":134,"question":"Slogan 'France is in the Air' créé par ?","options":[{"id":"a","text":"Publicis"},{"id":"b","text":"BETC"},{"id":"c","text":"Havas"},{"id":"d","text":"Ogilvy"}],"answer":"b","category":"Air France & Flotte","explanation":"Le slogan « France is in the Air » (2014-2022) a été créé par l'agence BETC."},
    {"id":135,"question":"Qui a créé le Hub CDG en 1996 ?","options":[{"id":"a","text":"Spinetta"},{"id":"b","text":"Smith"},{"id":"c","text":"Christian Blanc"},{"id":"d","text":"De Juniac"}],"answer":"c","category":"Air France & Flotte","explanation":"Christian Blanc, président de 1993 à 1997, a créé le Hub CDG."},
    {"id":136,"question":"Coût des grèves sous Janaillac ?","options":[{"id":"a","text":"100 M€"},{"id":"b","text":"200 M€"},{"id":"c","text":"335 M€"},{"id":"d","text":"500 M€"}],"answer":"c","category":"Air France & Flotte","explanation":"335 M€. Janaillac a démissionné après rejet du plan salarial."},
    {"id":137,"question":"Motoriste du Trent XWB (A350) ?","options":[{"id":"a","text":"GE"},{"id":"b","text":"Rolls-Royce"},{"id":"c","text":"P&W"},{"id":"d","text":"Safran"}],"answer":"b","category":"Air France & Flotte","explanation":"Le Trent XWB est fabriqué par Rolls-Royce (🇬🇧)."},
    {"id":138,"question":"Moteur de l'A220-300 ?","options":[{"id":"a","text":"CFM56"},{"id":"b","text":"LEAP-1A"},{"id":"c","text":"PW1500G"},{"id":"d","text":"GE90"}],"answer":"c","category":"Air France & Flotte","explanation":"L'A220 est équipé du Pratt & Whitney PW1500G."},
    {"id":139,"question":"Ancien nom de l'A220 ?","options":[{"id":"a","text":"Fokker 100"},{"id":"b","text":"Bombardier CSeries"},{"id":"c","text":"BAe 146"},{"id":"d","text":"Embraer E2"}],"answer":"b","category":"Air France & Flotte","explanation":"L'A220 s'appelait le Bombardier CSeries avant le rachat par Airbus."},
    {"id":140,"question":"Autonomie de l'A350-900 ?","options":[{"id":"a","text":"10 000 km"},{"id":"b","text":"13 000 km"},{"id":"c","text":"15 000 km"},{"id":"d","text":"18 000 km"}],"answer":"c","category":"Air France & Flotte","explanation":"15 000 km. Fuselage en carbone (53%), -25% conso vs A340."},
    {"id":141,"question":"En vol stabilisé en palier, Portance = ?","options":[{"id":"a","text":"Poussée"},{"id":"b","text":"Traînée"},{"id":"c","text":"Poids"},{"id":"d","text":"Portance + Traînée"}],"answer":"c","category":"Technique de Vol","explanation":"En palier stabilisé : Portance = Poids ET Poussée = Traînée."},
    {"id":142,"question":"L'axe longitudinal correspond au mouvement de ?","options":[{"id":"a","text":"Tangage"},{"id":"b","text":"Roulis"},{"id":"c","text":"Lacet"},{"id":"d","text":"Translation"}],"answer":"b","category":"Technique de Vol","explanation":"Axe longitudinal = Roulis (Roll) = Ailerons."},
    {"id":143,"question":"Quel instrument n'est PAS affecté si le tube Pitot est bouché ?","options":[{"id":"a","text":"Anémomètre"},{"id":"b","text":"Altimètre"},{"id":"c","text":"Badin"},{"id":"d","text":"Aucun"}],"answer":"b","category":"Technique de Vol","explanation":"Pitot bouché : seul le Badin est affecté. Altimètre et variomètre restent OK (ils utilisent la pression statique)."},
    {"id":144,"question":"GPWS signifie ?","options":[{"id":"a","text":"Ground Power Warning System"},{"id":"b","text":"Ground Proximity Warning System"},{"id":"c","text":"General Pilot Warning System"},{"id":"d","text":"GPS Warning System"}],"answer":"b","category":"Technique de Vol","explanation":"GPWS = Ground Proximity Warning System. Alerte : « TERRAIN, TERRAIN, PULL UP! »"},
    {"id":145,"question":"Limitations structurales d'un avion de ligne ?","options":[{"id":"a","text":"+1.5g / -0.5g"},{"id":"b","text":"+2.5g / -1g"},{"id":"c","text":"+3g / -1.5g"},{"id":"d","text":"+4g / -2g"}],"answer":"b","category":"Technique de Vol","explanation":"Avion de ligne : +2.5g / -1g. En virage à 60° : facteur de charge = 2g."},
    {"id":146,"question":"Le trim (compensateur) sert à ?","options":[{"id":"a","text":"Freiner"},{"id":"b","text":"Compenser l'effort sur le manche"},{"id":"c","text":"Augmenter la portance"},{"id":"d","text":"Inverser la poussée"}],"answer":"b","category":"Technique de Vol","explanation":"Le trim compense l'effort sur le manche pour maintenir l'assiette sans effort permanent."},
    {"id":147,"question":"VR est toujours ?","options":[{"id":"a","text":"< V1"},{"id":"b","text":"= V1"},{"id":"c","text":"≥ V1"},{"id":"d","text":"= V2"}],"answer":"c","category":"Technique de Vol","explanation":"VR (rotation) ≥ V1 (décision). V2 (sécurité) est atteinte au plus tard à 35 ft."},
    {"id":148,"question":"Vref = ?","options":[{"id":"a","text":"1.1 × Vs"},{"id":"b","text":"1.2 × Vs"},{"id":"c","text":"1.3 × Vs"},{"id":"d","text":"1.5 × Vs"}],"answer":"c","category":"Technique de Vol","explanation":"Vref (vitesse de référence atterrissage) = 1.3 × Vs en configuration atterrissage."},
    {"id":149,"question":"IAS vs TAS : à même IAS, la TAS en altitude ?","options":[{"id":"a","text":"Diminue"},{"id":"b","text":"Reste identique"},{"id":"c","text":"Augmente"},{"id":"d","text":"Dépend du vent"}],"answer":"c","category":"Technique de Vol","explanation":"À même IAS, la TAS augmente avec l'altitude (air moins dense → on va plus vite en vrai)."},
    {"id":150,"question":"Le nombre de Mach est utilisé au-dessus de ?","options":[{"id":"a","text":"FL100"},{"id":"b","text":"FL200"},{"id":"c","text":"FL250"},{"id":"d","text":"FL350"}],"answer":"c","category":"Technique de Vol","explanation":"Le nombre de Mach est utilisé au-dessus du FL250. Avions de ligne : Mach 0.74 à 0.90."},
    {"id":151,"question":"Le NDB utilise quelle bande ?","options":[{"id":"a","text":"VHF"},{"id":"b","text":"MF"},{"id":"c","text":"UHF"},{"id":"d","text":"SHF"}],"answer":"b","category":"Navigation & Météo","explanation":"NDB = MF (190-1750 kHz). Portée ~200 NM, peu précis, sensible aux parasites."},
    {"id":152,"question":"Le DME mesure ?","options":[{"id":"a","text":"Le cap"},{"id":"b","text":"La distance oblique"},{"id":"c","text":"L'altitude"},{"id":"d","text":"La vitesse sol"}],"answer":"b","category":"Navigation & Météo","explanation":"DME = distance oblique en NM. Souvent couplé au VOR pour donner un fix (position exacte)."},
    {"id":153,"question":"Catégorie ILS la plus restrictive (aucun minimum) ?","options":[{"id":"a","text":"Cat I"},{"id":"b","text":"Cat II"},{"id":"c","text":"Cat IIIB"},{"id":"d","text":"Cat IIIC"}],"answer":"d","category":"Navigation & Météo","explanation":"Cat IIIC = aucun minimum de DH ni de RVR (atterrissage automatique total)."},
    {"id":154,"question":"Minimum de satellites pour une position 3D (GPS) ?","options":[{"id":"a","text":"2"},{"id":"b","text":"3"},{"id":"c","text":"4"},{"id":"d","text":"6"}],"answer":"c","category":"Navigation & Météo","explanation":"4 satellites minimum pour une position 3D (latitude, longitude, altitude)."},
    {"id":155,"question":"Galileo est le GNSS de quel pays/région ?","options":[{"id":"a","text":"USA"},{"id":"b","text":"Russie"},{"id":"c","text":"Union Européenne"},{"id":"d","text":"Chine"}],"answer":"c","category":"Navigation & Météo","explanation":"GPS (USA), Galileo (UE), GLONASS (Russie), BeiDou (Chine)."},
    {"id":156,"question":"Routes NAT tracks sont révisées ?","options":[{"id":"a","text":"1×/semaine"},{"id":"b","text":"2×/jour"},{"id":"c","text":"1×/mois"},{"id":"d","text":"Jamais"}],"answer":"b","category":"Navigation & Météo","explanation":"Les NAT tracks sont révisées 2×/jour selon le jet stream."},
    {"id":157,"question":"La classe G est ?","options":[{"id":"a","text":"Contrôlée"},{"id":"b","text":"Interdite"},{"id":"c","text":"Non contrôlée"},{"id":"d","text":"Militaire"}],"answer":"c","category":"Navigation & Météo","explanation":"Classe G = espace non contrôlé. Aucune séparation, radio non obligatoire."},
    {"id":158,"question":"Route Est (000-179°) → FL ?","options":[{"id":"a","text":"Pairs"},{"id":"b","text":"Impairs"},{"id":"c","text":"Tous"},{"id":"d","text":"Aucun"}],"answer":"b","category":"Navigation & Météo","explanation":"Est = FL impairs (310, 330, 350...). Ouest = FL pairs (320, 340, 360...)."},
    {"id":159,"question":"1 hPa ≈ combien de ft ?","options":[{"id":"a","text":"10 ft"},{"id":"b","text":"28 ft"},{"id":"c","text":"50 ft"},{"id":"d","text":"100 ft"}],"answer":"b","category":"Navigation & Météo","explanation":"1 hPa ≈ 28 ft. « High to low, look out below! »"},
    {"id":160,"question":"Température ISA à 10 000 ft ?","options":[{"id":"a","text":"+5°C"},{"id":"b","text":"0°C"},{"id":"c","text":"-5°C"},{"id":"d","text":"-15°C"}],"answer":"c","category":"Navigation & Météo","explanation":"15°C - (10 × 2°C) = -5°C."},
    {"id":161,"question":"FEW en couverture nuageuse = ?","options":[{"id":"a","text":"0/8"},{"id":"b","text":"1-2/8"},{"id":"c","text":"3-4/8"},{"id":"d","text":"5-7/8"}],"answer":"b","category":"Navigation & Météo","explanation":"FEW=1-2/8, SCT=3-4/8, BKN=5-7/8, OVC=8/8."},
    {"id":162,"question":"Le front froid est caractérisé par ?","options":[{"id":"a","text":"Pluie continue, stratus"},{"id":"b","text":"Cumulus, averses, orages"},{"id":"c","text":"Beau temps"},{"id":"d","text":"Brouillard"}],"answer":"b","category":"Navigation & Météo","explanation":"Front froid = air froid pousse sous air chaud → Cumulus/Cb, averses, orages."},
    {"id":163,"question":"CAT signifie ?","options":[{"id":"a","text":"Clear Air Traffic"},{"id":"b","text":"Clear Air Turbulence"},{"id":"c","text":"Controlled Air Turbulence"},{"id":"d","text":"Cloud Air Turbulence"}],"answer":"b","category":"Navigation & Météo","explanation":"CAT = Turbulence en air clair, invisible (pas de nuages), souvent près du jet stream."},
    {"id":164,"question":"Code OACI d'Orly ?","options":[{"id":"a","text":"LFPG"},{"id":"b","text":"LFPO"},{"id":"c","text":"LFBO"},{"id":"d","text":"LFML"}],"answer":"b","category":"Navigation & Météo","explanation":"LFPO = Orly. LFPG = CDG. LFBO = Toulouse."},
    {"id":165,"question":"Couvre-feu à Orly ?","options":[{"id":"a","text":"22h-05h"},{"id":"b","text":"23h30-06h"},{"id":"c","text":"00h-06h"},{"id":"d","text":"Pas de couvre-feu"}],"answer":"b","category":"Navigation & Météo","explanation":"Orly : couvre-feu de 23h30 à 06h00."},
    {"id":166,"question":"Plus grand aéroport d'Europe en passagers ?","options":[{"id":"a","text":"CDG"},{"id":"b","text":"Frankfurt"},{"id":"c","text":"Heathrow"},{"id":"d","text":"Schiphol"}],"answer":"c","category":"Navigation & Météo","explanation":"London Heathrow est le plus fréquenté en Europe. CDG est 2e."},
    {"id":167,"question":"Hub de KLM ?","options":[{"id":"a","text":"Bruxelles"},{"id":"b","text":"Amsterdam-Schiphol"},{"id":"c","text":"Rotterdam"},{"id":"d","text":"Utrecht"}],"answer":"b","category":"Navigation & Météo","explanation":"KLM a son hub à Amsterdam-Schiphol (6 pistes)."},
    {"id":168,"question":"Star Alliance fondée en ?","options":[{"id":"a","text":"1995"},{"id":"b","text":"1997"},{"id":"c","text":"1999"},{"id":"d","text":"2001"}],"answer":"b","category":"Divers & Approfondissement","explanation":"Star Alliance (1997), SkyTeam (2000), Oneworld (1999)."},
    {"id":169,"question":"British Airways est dans ?","options":[{"id":"a","text":"Star Alliance"},{"id":"b","text":"SkyTeam"},{"id":"c","text":"Oneworld"},{"id":"d","text":"Aucune"}],"answer":"c","category":"Divers & Approfondissement","explanation":"Oneworld : BA, American, Qantas, JAL, Iberia, Cathay Pacific."},
    {"id":170,"question":"Niveaux Flying Blue : après Silver ?","options":[{"id":"a","text":"Platinum"},{"id":"b","text":"Gold"},{"id":"c","text":"Diamond"},{"id":"d","text":"Ultimate"}],"answer":"b","category":"Divers & Approfondissement","explanation":"Explorer → Silver → Gold → Platinum → Ultimate."},
    {"id":171,"question":"AF8969 : intervention de quel groupe ?","options":[{"id":"a","text":"RAID"},{"id":"b","text":"GIGN"},{"id":"c","text":"BRI"},{"id":"d","text":"CRS"}],"answer":"b","category":"Divers & Approfondissement","explanation":"Le GIGN est intervenu à Marseille-Marignane lors du détournement de l'AF8969 en 1994."},
    {"id":172,"question":"Cause du crash du Concorde à Gonesse ?","options":[{"id":"a","text":"Panne moteur"},{"id":"b","text":"Erreur humaine"},{"id":"c","text":"Débris pneu perçant le réservoir"},{"id":"d","text":"Météo"}],"answer":"c","category":"Divers & Approfondissement","explanation":"Débris de pneu + lame métallique sur piste → percement réservoir → incendie."},
    {"id":173,"question":"Système défaillant des B737 MAX ?","options":[{"id":"a","text":"TCAS"},{"id":"b","text":"MCAS"},{"id":"c","text":"EGPWS"},{"id":"d","text":"FMS"}],"answer":"b","category":"Divers & Approfondissement","explanation":"Le système MCAS défaillant a causé 2 crashes (Lion Air + Ethiopian), 346 morts. Cloué au sol 20 mois."},
    {"id":174,"question":"EASA créée en ?","options":[{"id":"a","text":"1990"},{"id":"b","text":"1996"},{"id":"c","text":"2002"},{"id":"d","text":"2010"}],"answer":"c","category":"Divers & Approfondissement","explanation":"EASA = European Union Aviation Safety Agency, créée en 2002."},
    {"id":175,"question":"BEA signifie ?","options":[{"id":"a","text":"Bureau des Explications Aériennes"},{"id":"b","text":"Bureau d'Enquêtes et d'Analyses"},{"id":"c","text":"Bureau Européen de l'Aviation"},{"id":"d","text":"Bureau d'Études Aéronautiques"}],"answer":"b","category":"Divers & Approfondissement","explanation":"BEA = Bureau d'Enquêtes et d'Analyses pour la sécurité de l'aviation civile (France)."},
    {"id":176,"question":"1 mille terrestre (statute mile) = ?","options":[{"id":"a","text":"1 000 m"},{"id":"b","text":"1 609 m"},{"id":"c","text":"1 852 m"},{"id":"d","text":"2 000 m"}],"answer":"b","category":"Divers & Approfondissement","explanation":"1 statute mile = 1 609 m. 1 NM = 1 852 m (ne pas confondre !)."},
    {"id":177,"question":"1 kg ≈ combien de livres (lbs) ?","options":[{"id":"a","text":"1.5 lbs"},{"id":"b","text":"2.205 lbs"},{"id":"c","text":"3 lbs"},{"id":"d","text":"0.45 lbs"}],"answer":"b","category":"Divers & Approfondissement","explanation":"1 kg ≈ 2.205 lbs."},
    {"id":178,"question":"Plus long vol commercial au monde ?","options":[{"id":"a","text":"Dubai-Auckland"},{"id":"b","text":"Singapore-JFK"},{"id":"c","text":"Paris-Sydney"},{"id":"d","text":"London-Perth"}],"answer":"b","category":"Divers & Approfondissement","explanation":"Singapore Airlines SIN-JFK : ~18h45, 15 349 km (A350-900ULR)."},
    {"id":179,"question":"CVR enregistre au minimum ?","options":[{"id":"a","text":"30 min"},{"id":"b","text":"1h"},{"id":"c","text":"2h"},{"id":"d","text":"25h"}],"answer":"c","category":"Divers & Approfondissement","explanation":"CVR (Cockpit Voice Recorder) = min 2h. FDR (Flight Data Recorder) = min 25h."},
    {"id":180,"question":"Radio-altimètre précis en dessous de ?","options":[{"id":"a","text":"500 ft"},{"id":"b","text":"1 000 ft"},{"id":"c","text":"2 500 ft"},{"id":"d","text":"5 000 ft"}],"answer":"c","category":"Divers & Approfondissement","explanation":"Le radio-altimètre mesure la hauteur vraie au-dessus du sol par radar, précis < 2 500 ft."},
    {"id":181,"question":"Taux de dilution du LEAP ?","options":[{"id":"a","text":"~3"},{"id":"b","text":"~6"},{"id":"c","text":"~11"},{"id":"d","text":"~15"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"LEAP ~11, CFM56 ~6, Militaire ~0.5. Plus élevé = plus silencieux et économique."},
    {"id":182,"question":"Point d'éclair du Jet A-1 ?","options":[{"id":"a","text":"> 0°C"},{"id":"b","text":"> 20°C"},{"id":"c","text":"> 38°C"},{"id":"d","text":"> 50°C"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"Point d'éclair > 38°C (sécurité incendie). Point de congélation ≤ -47°C."},
    {"id":183,"question":"Objectif SAF d'Air France d'ici 2030 ?","options":[{"id":"a","text":"5%"},{"id":"b","text":"10%"},{"id":"c","text":"20%"},{"id":"d","text":"50%"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"Objectif AF : 10% de SAF d'ici 2030. SAF = Sustainable Aviation Fuel."},
    {"id":184,"question":"Couleur des 3 circuits hydrauliques Airbus ?","options":[{"id":"a","text":"Rouge/Bleu/Jaune"},{"id":"b","text":"Vert/Bleu/Jaune"},{"id":"c","text":"Vert/Rouge/Blanc"},{"id":"d","text":"A/B/C"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"Airbus : 3 circuits hydrauliques Vert, Bleu et Jaune."},
    {"id":185,"question":"La pressurisation cabine est assurée par ?","options":[{"id":"a","text":"Hydraulique"},{"id":"b","text":"Électrique"},{"id":"c","text":"Pneumatique (bleed air)"},{"id":"d","text":"Carburant"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"Le système pneumatique (prélèvement d'air moteurs = bleed air) assure la pressurisation, l'antigivrage et le démarrage moteurs."},
    {"id":186,"question":"Altitude cabine max certifiée ?","options":[{"id":"a","text":"4 000 ft"},{"id":"b","text":"6 000 ft"},{"id":"c","text":"8 000 ft"},{"id":"d","text":"10 000 ft"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"Altitude cabine max : 8 000 ft (2 438 m). Au-dessus de 10 000 ft cabine : risque d'hypoxie."},
    {"id":187,"question":"RAT signifie ?","options":[{"id":"a","text":"Radio Altimeter Transmitter"},{"id":"b","text":"Ram Air Turbine"},{"id":"c","text":"Radar Air Tracker"},{"id":"d","text":"Remote Air Terminal"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"RAT = Ram Air Turbine = éolienne de secours déployée pour fournir de l'électricité hydraulique en cas de perte totale."},
    {"id":188,"question":"Les masques passagers utilisent ?","options":[{"id":"a","text":"Bouteilles d'O₂"},{"id":"b","text":"Générateurs chimiques"},{"id":"c","text":"Air comprimé"},{"id":"d","text":"Air extérieur"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"Passagers : générateurs chimiques. Équipage : bouteilles d'oxygène."},
    {"id":189,"question":"Feux de fin de piste = couleur ?","options":[{"id":"a","text":"Blancs"},{"id":"b","text":"Verts"},{"id":"c","text":"Rouges"},{"id":"d","text":"Jaunes"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"Seuil = Verts. Fin de piste = Rouges. Bord de piste = Blancs (jaunes derniers 600m)."},
    {"id":190,"question":"Point d'arrêt avant piste (taxiway) = ?","options":[{"id":"a","text":"2 lignes blanches"},{"id":"b","text":"2 lignes continues + 2 tiretées jaunes"},{"id":"c","text":"1 ligne rouge"},{"id":"d","text":"Feux clignotants"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"Ne JAMAIS franchir sans clairance ATC ! 2 lignes jaunes continues + 2 tiretées."},
    {"id":191,"question":"PAN PAN signifie ?","options":[{"id":"a","text":"Détresse vitale"},{"id":"b","text":"Urgence non vitale"},{"id":"c","text":"Panne radio"},{"id":"d","text":"Demande d'information"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"PAN PAN (×3) = urgence non vitale. MAYDAY (×3) = détresse vitale."},
    {"id":192,"question":"SQUAWK signifie ?","options":[{"id":"a","text":"Monter"},{"id":"b","text":"Tourner"},{"id":"c","text":"Afficher un code transpondeur"},{"id":"d","text":"Atterrir immédiatement"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"« Squawk 7700 » = afficher le code 7700 (urgence) sur le transpondeur."},
    {"id":193,"question":"Carburant avions à pistons ?","options":[{"id":"a","text":"Jet A-1"},{"id":"b","text":"Avgas 100LL"},{"id":"c","text":"Diesel"},{"id":"d","text":"SP98"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"Avgas 100LL = essence aviation pour moteurs à pistons, contient du plomb (coloration bleue), 100 octanes."},
    {"id":194,"question":"Éco-pilotage : technique de descente optimale ?","options":[{"id":"a","text":"Descente par paliers"},{"id":"b","text":"Descente continue"},{"id":"c","text":"Descente rapide"},{"id":"d","text":"Descente en spirale"}],"answer":"b","category":"ETOPS, CRM & Systèmes","explanation":"Éco-pilotage AF ACT : montée continue, descente continue, roulage un moteur."},
    {"id":195,"question":"Objectif flotte nouvelle génération AF d'ici 2030 ?","options":[{"id":"a","text":"30%"},{"id":"b","text":"50%"},{"id":"c","text":"70%"},{"id":"d","text":"100%"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"70% de flotte nouvelle génération d'ici 2030 (A220, A350, A320neo)."},
    {"id":196,"question":"Crash de Tenerife (1977) : nombre de morts ?","options":[{"id":"a","text":"271"},{"id":"b","text":"346"},{"id":"c","text":"583"},{"id":"d","text":"630"}],"answer":"c","category":"ETOPS, CRM & Systèmes","explanation":"583 morts, le plus meurtrier de l'histoire de l'aviation. A conduit au développement du CRM."},
    {"id":197,"question":"Distance Paris-Tokyo ?","options":[{"id":"a","text":"~5 850 km"},{"id":"b","text":"~8 750 km"},{"id":"c","text":"~9 700 km"},{"id":"d","text":"~12 000 km"}],"answer":"c","category":"Divers & Approfondissement","explanation":"Paris-Tokyo ~9 700 km (~11-12h), la plus éloignée parmi les grandes destinations."},
    {"id":198,"question":"Route orthodromique = ?","options":[{"id":"a","text":"La plus courte sur une sphère"},{"id":"b","text":"La ligne droite sur la carte"},{"id":"c","text":"La route en ligne droite"},{"id":"d","text":"La route loxodromique"}],"answer":"a","category":"Divers & Approfondissement","explanation":"Route orthodromique (grand cercle) = plus court chemin sur une sphère. Apparaît courbée sur une carte Mercator."},
    {"id":199,"question":"Plus grande envergure au monde ?","options":[{"id":"a","text":"A380 (79.75m)"},{"id":"b","text":"An-225 (88.4m)"},{"id":"c","text":"Stratolaunch (117m)"},{"id":"d","text":"B747-8 (68.4m)"}],"answer":"c","category":"Divers & Approfondissement","explanation":"Stratolaunch = 117m d'envergure. L'An-225 Mriya (détruit en 2022) avait la plus grande MTOW (640t)."},
    {"id":200,"question":"Code VFR standard en Europe ?","options":[{"id":"a","text":"2000"},{"id":"b","text":"7000"},{"id":"c","text":"7500"},{"id":"d","text":"7700"}],"answer":"b","category":"Divers & Approfondissement","explanation":"7000 = code VFR standard (Europe). 2000 = IFR par défaut si pas assigné."},
]

all_q.extend(new_questions)
print(f"Total questions: {len(all_q)}")

# --- FLASHCARDS ---
flashcards = [
    {"id":1,"front":"Date de création d'Air France ?","back":"7 octobre 1933 – Fusion de 5 compagnies : Air Orient, Air Union, CIDNA, Lignes Farman (SGTA), Aéropostale","category":"Dates Clés"},
    {"id":2,"front":"Premier vol motorisé contrôlé ?","back":"Frères Wright, 1903, Kitty Hawk (USA), 12s, 36m, Wright Flyer","category":"Dates Clés"},
    {"id":3,"front":"Premier décollage motorisé (France) ?","back":"Clément Ader, 1890, Éole, ~50m non contrôlé. Invente le mot « avion »","category":"Dates Clés"},
    {"id":4,"front":"Première traversée de la Manche ?","back":"Louis Blériot, 25 juillet 1909, Blériot XI, 37 min","category":"Dates Clés"},
    {"id":5,"front":"Première traversée solo Atlantique Nord ?","back":"Charles Lindbergh, 1927, Spirit of St. Louis, NY→Paris (Le Bourget), 33h30","category":"Dates Clés"},
    {"id":6,"front":"Premier vol du Concorde ?","back":"2 mars 1969, Toulouse. Programme franco-britannique. Mach 2.02","category":"Dates Clés"},
    {"id":7,"front":"Convention de Chicago ?","back":"1944 – Création de l'OACI (Organisation de l'Aviation Civile Internationale)","category":"Dates Clés"},
    {"id":8,"front":"Premier vol supersonique ?","back":"Chuck Yeager, 1947, Bell X-1 « Glamorous Glennis », Mach 1.06","category":"Dates Clés"},
    {"id":9,"front":"Création d'Airbus ?","back":"18 décembre 1970, consortium européen (Aérospatiale 🇫🇷 + Deutsche Airbus 🇩🇪)","category":"Dates Clés"},
    {"id":10,"front":"Hub CDG inauguré ?","back":"1996, sous Christian Blanc","category":"Dates Clés"},
    {"id":11,"front":"Alliance SkyTeam fondée ?","back":"22 juin 2000. Fondateurs : AF, Delta, AeroMéxico, Korean Air. Siège : Amsterdam","category":"Dates Clés"},
    {"id":12,"front":"Groupe Air France-KLM créé ?","back":"2004 – Fusion","category":"Dates Clés"},
    {"id":13,"front":"A350-900 en service chez AF ?","back":"Septembre 2019. Remplace A340/A330/B777-200","category":"Dates Clés"},
    {"id":14,"front":"Retrait de l'A380 chez AF ?","back":"2020 – Covid accélère la décision","category":"Dates Clés"},
    {"id":15,"front":"A320 en service chez AF ?","back":"1988 – Premier avion civil fly-by-wire Airbus","category":"Dates Clés"},
    {"id":16,"front":"Emblème d'Air France ?","back":"Hippocampe ailé (surnommé « la crevette »), hérité d'Air Orient","category":"Air France"},
    {"id":17,"front":"Slogan actuel AF (depuis 2022) ?","back":"« S'envoler en toute élégance »","category":"Air France"},
    {"id":18,"front":"DG Groupe AF-KLM ?","back":"Benjamin Smith (depuis août 2018). Piliers : Confiance, Respect, Transparence, Confidentialité","category":"Air France"},
    {"id":19,"front":"DG Air France ?","back":"Anne Rigail (depuis déc 2018) – Première femme au poste","category":"Air France"},
    {"id":20,"front":"Flotte Air France ?","back":"~228 avions. ~200 destinations dans ~90 pays. ~50 millions pax/an. ~43 000 employés","category":"Air France"},
    {"id":21,"front":"Code OACI / IATA d'Air France ?","back":"AFR / AF. Indicatif radio : « AIR FRANCE »","category":"Air France"},
    {"id":22,"front":"Moteur de l'A350 ?","back":"2× Rolls-Royce Trent XWB","category":"Flotte"},
    {"id":23,"front":"Moteur du B777 ?","back":"2× GE90 (General Electric) – Le plus puissant au monde (115 000 lb)","category":"Flotte"},
    {"id":24,"front":"Moteur de l'A220 ?","back":"2× Pratt & Whitney PW1500G","category":"Flotte"},
    {"id":25,"front":"Moteur de l'A320 ?","back":"2× CFM56-5. CFM International = GE (USA) + Safran (France)","category":"Flotte"},
    {"id":26,"front":"Vitesse croisière A320 ?","back":"Mach 0.78 (828 km/h). Plafond FL410","category":"Flotte"},
    {"id":27,"front":"Vitesse croisière A350 ?","back":"Mach 0.85 (~910 km/h). Autonomie 15 000 km","category":"Flotte"},
    {"id":28,"front":"Concorde – chiffres clés ?","back":"Mach 2.02, plafond 18 300m (60 000ft), 100 pax, Paris-NY 3h30, 4× Olympus 593. Service AF : 1976-2003","category":"Flotte"},
    {"id":29,"front":"Les 4 forces du vol ?","back":"Portance (↑) / Poids (↓) / Poussée (→) / Traînée (←). En palier : Portance=Poids ET Poussée=Traînée","category":"Technique"},
    {"id":30,"front":"ASSIETTE = ?","back":"PENTE + INCIDENCE","category":"Technique"},
    {"id":31,"front":"Les 3 axes et gouvernes ?","back":"Roulis=Ailerons (longitudinal) / Tangage=Profondeur (latéral) / Lacet=Direction (vertical+palonnier)","category":"Technique"},
    {"id":32,"front":"Le décrochage se produit à ?","back":"Toujours à la même incidence critique (~15-18°), indépendamment de la vitesse/poids/altitude","category":"Technique"},
    {"id":33,"front":"V1 / VR / V2 ?","back":"V1=décision (stop ou go) / VR=rotation (lever le nez) / V2=sécurité (monter avec 1 moteur en panne)","category":"Technique"},
    {"id":34,"front":"Codes transpondeur d'urgence ?","back":"7500=Détournement / 7600=Panne radio / 7700=Urgence. Mnémo : 75=alive, 76=fix, 77=heaven","category":"Technique"},
    {"id":35,"front":"Turboréacteur – ordre ?","back":"Fan → Compresseur → Chambre de Combustion → Turbine → Tuyère","category":"Technique"},
    {"id":36,"front":"ISA au niveau de la mer ?","back":"15°C, 1013.25 hPa. Gradient : -2°C / 1000 ft. Tropopause : 36 000 ft, -56.5°C","category":"Météo"},
    {"id":37,"front":"Calages altimétriques ?","back":"QNH = Altitude / QFE = Hauteur / 1013.25 = Niveau de vol. « High to low, look out below! »","category":"Météo"},
    {"id":38,"front":"Nuage le plus dangereux ?","back":"Cumulonimbus (Cb) : 0.5-15 km, orages, grêle, foudre, cisaillement, turbulences","category":"Météo"},
    {"id":39,"front":"Jet stream ?","back":"Courant de 150-300 kt à la tropopause, d'ouest en est. NY→Paris plus rapide","category":"Météo"},
    {"id":40,"front":"1 NM = ? / 1 kt = ?","back":"1 NM = 1 852 m (1 minute d'arc de latitude). 1 kt = 1 NM/h = 1.852 km/h","category":"Unités"},
    {"id":41,"front":"ILS – composants ?","back":"Localizer (horizontal, VHF) + Glide Slope (vertical 3°, UHF) + Marker beacons","category":"Navigation"},
    {"id":42,"front":"GNSS – 4 systèmes ?","back":"GPS (USA) / Galileo (UE) / GLONASS (Russie) / BeiDou (Chine). Min 4 satellites pour position 3D","category":"Navigation"},
    {"id":43,"front":"Pistes CDG ?","back":"4 pistes : 08L/26R (4142m), 08R/26L (2700m), 09L/27R (2700m), 09R/27L (4200m). Orientation Est-Ouest","category":"Navigation"},
    {"id":44,"front":"Prise statique bouchée → ?","back":"Altimètre bloqué, Variomètre bloqué à 0, Badin sous-estime en montée / surestime en descente","category":"Technique"},
    {"id":45,"front":"Tube Pitot bouché → ?","back":"Badin erroné (se comporte comme un altimètre). Altimètre et variomètre restent OK","category":"Technique"},
    {"id":46,"front":"ETOPS ?","back":"Extended-range Twin-engine Ops. ETOPS-180 = 95% du globe. A350 : ETOPS-370 (6h10)","category":"Technique"},
    {"id":47,"front":"CRM ?","back":"Crew Resource Management. Après Tenerife 1977 (583 morts). 80% des accidents liés aux facteurs humains","category":"Technique"},
    {"id":48,"front":"Modèle de Reason ?","back":"« Fromage suisse » : accident quand les trous de toutes les couches de défense s'alignent","category":"Technique"},
    {"id":49,"front":"PAPI ?","back":"4 rouges = trop bas ⚠️ / 4 blancs = trop haut / 2 rouges + 2 blancs = correct (plan 3°)","category":"Navigation"},
    {"id":50,"front":"MAYDAY vs PAN PAN ?","back":"MAYDAY (×3) = détresse vitale. PAN PAN (×3) = urgence non vitale. Ne jamais dire « repeat » → « say again »","category":"Technique"},
]

# --- WRITE OUTPUT ---
out = "// PSY0 Training Data - V2 - Auto-generated\n"
out += f"// {len(all_q)} questions + {len(flashcards)} flashcards\n\n"
out += "const qcmData = " + json.dumps(all_q, indent=2, ensure_ascii=False) + ";\n\n"
out += "const flashcardData = " + json.dumps(flashcards, indent=2, ensure_ascii=False) + ";\n"

with open("/Users/maximeleboeuf/Cadet AF/PSY0_Training/data/questions.js", 'w', encoding='utf-8') as f:
    f.write(out)

print(f"✅ Generated {len(all_q)} questions and {len(flashcards)} flashcards")
