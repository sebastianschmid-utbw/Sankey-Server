# Import von Bibliotheken - Nichts ändern
import plotly.offline as py
import pandas as pd
import numpy as np
import gc

Name_KA = name   # Name muss in Anführungszeichen stehen
EW = ew               #Anzahl EW
Einheit = 't CO2-eq/Jahr' # Ebenfalls in Anführungszeichen, Einheitliche - Gesamt KA oder Bezug auf EW
Abwasser = flow        # [m^3/a]

# Engergie
Energie_BHKW_eigen = gas # [kWh/a]
Energie_fremd = strom       # [kWh/a]


# Zulauf-Parameter
CSB_zu = csb_zu  # [mg/L]
BSB5_zu = bsb_zu  # [mg/L]
N_Ges_zu = tkn_zu # [mg/L]
P_zu = p_zu     # [mg/L]

# Ablauf-Parameter
CSB_ab = csb_ab     # [mg/L]
BSB5_ab = bsb_ab      # [mg/L]
N_Ges_ab = tkn_ab # [mg/L]
P_ab = p_ab       # [mg/L]


# Weitere Indirekte Emissionen - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
CO2eq_Betriebsstoffe = betriebsstoffe             # [t CO2eq/a]
CO2eq_Klaerschlamm_Entsorgung = transport # [t CO2eq/a]
CO2eq_Klaerschlamm_Transport = entsorgung    # [t CO2eq/a]


# Emissionsfaktoren
EF_CH4_Anlage = 230      # [g CH4/(EW*a)]
EF_CH4_Gewaesser = 0.009 # [0,9 % des CSB-Ablauf]
EF_CH4_BHKW = 1.124      # [1,124 g CH4/kWh]

EF_N2O_Anlage = 0.0016   # [1,6 % des Ges-N Zulauf]
EF_N2O_Gewaesser = 0.005 # [0,5 % des Ges-N Ablauf]

EF_CO2_Strommix = 420    # [g CO2/kWh]

# Umrechnungsfaktoren
GWP_N2O = 265
GWP_CH4 = 28
UF_N_zu_N2O = 44/28


# Direkte Emissionen
## Lachgas
N2O_Anlage = N_Ges_zu / 10**9 * Abwasser * 10**3 * EF_N2O_Anlage * UF_N_zu_N2O       # [t N2O/a]
N2O_Gewaesser = N_Ges_ab / 10**9 * Abwasser * 10**3 * EF_N2O_Gewaesser * UF_N_zu_N2O # [t N2O/a]

## Methan
CH4_Anlage = EW * EF_CH4_Anlage / 10**6                              # [t CH4/a]
CH4_Gewaesser = CSB_ab / 10**9 * Abwasser * 10**3 * EF_CH4_Gewaesser # [t CH4/a]
CH4_BHKW = Energie_BHKW_eigen * EF_CH4_BHKW / 10**6                  # [t CH4/a]

## CO2eq
CO2eq_N2O_Anlage = N2O_Anlage * GWP_N2O       # [t CO2eq/a]
CO2eq_N2O_Gewaesser = N2O_Gewaesser * GWP_N2O # [t CO2eq/a]

CO2eq_CH4_Anlage = CH4_Anlage * GWP_CH4       # [t CO2eq/a]
CO2eq_CH4_Gewaesser = CH4_Gewaesser * GWP_CH4 # [t CO2eq/a]
CO2eq_CH4_BHKW = CH4_BHKW * GWP_CH4           # [t CO2eq/a]

CO2eq_Strommix = Energie_fremd * EF_CO2_Strommix / 10**6 # [t CO2eq/a]



Direkte_Emissionen_CO2_Eq = CO2eq_N2O_Anlage + CO2eq_N2O_Gewaesser + CO2eq_CH4_Anlage + CO2eq_CH4_Gewaesser + CO2eq_CH4_BHKW
Indirekte_Emissionen_CO2_Eq = CO2eq_Strommix
Weitere_Indirekte_Emissionen_CO2_Eq = CO2eq_Betriebsstoffe + CO2eq_Klaerschlamm_Entsorgung + CO2eq_Klaerschlamm_Transport
Nutzung_CO2_Eq = Direkte_Emissionen_CO2_Eq + Indirekte_Emissionen_CO2_Eq + Weitere_Indirekte_Emissionen_CO2_Eq
Emissionen_CO2_Eq = Nutzung_CO2_Eq

# Hier Farben über HTML-Codes definieren
hellgelb = '#F9E79F'
blau     = '#3498DB'
gelb     = '#F4D03F'
teal     = '#16A085'
orange   = '#F5B041'
fuchsia  = '#A569BD'
hellrot  = '#F5B7B1'
magenta  = '#FF00E8'
lavendel = '#C39BD3'

link_opacity = 0.4

nodecolors = [blau, # CH4 Schlamm
              blau, # Direkte Emissionen
              blau, # CH4 Abwasser
              blau, # N2O (gesamt)
              blau, # Stromverbrauch
              blau, # Indirekte Emissionen
              blau, # Energieverbrauch
              blau, # Abfall (Transport)
              blau, # Weitere indirekte Emissionen
              blau, # Abfall (Entsorgung)
              blau, # Betriebsstoffe
              blau, # Nutzung
              blau, # Emissionen
              ]

# Definition der stream-Klasse - Nichts ändern
class stream:
    def __init__(self, source, target, value, color):
        global labels, streams
        self.source = source
        self.target = target
        self.value  = value
        self.color  = color
        labels.append(self.source)
        labels.append(self.target)
    
    def makeindex(self):
        global labels
        self.source = labels.index(self.source)
        self.target = labels.index(self.target)
        
    def appendDataframe(self):
        global df
        df_add = [[self.source, self.target, self.value, self.color]]
        df_add = pd.DataFrame(df_add, columns = ['Source', 'Target', 'Value', 'Color']) 
        df = pd.concat([df, df_add], ignore_index=True, sort=False)

def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))

def add_opacity(rgb, opacity):
    #stuff_in_string = "Shepherd %s is %d years old." % (shepherd, age)
    colorcode = str(rgb).replace(')', ', %s)' % (opacity)).replace('(', 'rgba(')
    return colorcode

def create_stream_dict(name, target, value, color):
  d = {
  "Name": name,
  "Ziel": target,
  "Wert": value,
  "Farbe": blau,
  }
  return d 

dir_em = "Direkte Emissionen"
indir_em = "Indirekte Emissionen"
wei_indir_em = "Weitere Indirekte Emissionen"
nu = "Nutzung"
em = "Emission"

# Clear Data Reset - Jedes mal ausführen, wenn Daten geändert wurden. Setzt Daten zurück. Nichts ändern
df = pd.DataFrame({'Source' : [], 'Target' : [], 'Value' : [], 'Color' : []})
labels = []
streams = []

streams.append(create_stream_dict("N<sub>2</sub>O Anlage", dir_em, CO2eq_N2O_Anlage, blau))
streams.append(create_stream_dict("N<sub>2</sub>O Gewässer", dir_em, CO2eq_N2O_Gewaesser, blau))

streams.append(create_stream_dict("CH<sub>4</sub> Anlage", dir_em, CO2eq_CH4_Anlage, blau))
streams.append(create_stream_dict("CH<sub>4</sub> Gewässer", dir_em, CO2eq_CH4_Gewaesser, blau))
streams.append(create_stream_dict("CH<sub>4</sub> BHKW", dir_em, CO2eq_CH4_BHKW, blau))

streams.append(create_stream_dict("Strommix", indir_em, CO2eq_Strommix, blau))
streams.append(create_stream_dict("Betriebsstoffe", wei_indir_em, CO2eq_Betriebsstoffe, blau))
streams.append(create_stream_dict("Klärschlamm Entsorgung", wei_indir_em, CO2eq_Klaerschlamm_Entsorgung, blau))
streams.append(create_stream_dict("Klärschlamm Transport", wei_indir_em, CO2eq_Klaerschlamm_Transport, blau))

streams.append(create_stream_dict(dir_em, nu, Direkte_Emissionen_CO2_Eq, blau))
streams.append(create_stream_dict(indir_em, nu, Indirekte_Emissionen_CO2_Eq, blau))
streams.append(create_stream_dict(wei_indir_em, nu, Weitere_Indirekte_Emissionen_CO2_Eq, blau))

streams.append(create_stream_dict(nu, em, Emissionen_CO2_Eq, blau))

p = [stream(x["Name"], x["Ziel"], x["Wert"], x["Farbe"]) for x in streams] # Concat all streams

labels = list(dict.fromkeys(labels))

for obj in gc.get_objects():
    if isinstance(obj, stream):
        obj.makeindex()
        obj.appendDataframe()  

df['Color'] = df['Color'].apply(hex_to_rgb).apply(add_opacity, opacity = link_opacity)


import plotly.graph_objects as go

Titel = "Kläranlage {} ({} EW)<br>Treibhausgasemissionen [{}] ".format(Name_KA, EW, Einheit)


fig = go.Figure(data=[go.Sankey(
    arrangement = "snap", # Snap verschiebt die Nodes automatisch, damit das padding eingehalten wird. Andere Möglichkeiten: ( "snap" | "perpendicular" | "freeform" | "fixed" )
    node = dict(
      pad = 25, # Abstand der Nodes
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = nodecolors
    ),
    textfont = dict(
        family = 'Arial',
        size = 14,
        color = 'black'),
    hoverinfo = None,
    link = dict(
      source = df['Source'].dropna(axis=0, how='any'),
      target = df['Target'].dropna(axis=0, how='any'),
      value = df['Value'].dropna(axis=0, how='any'),
      color = df['Color'].dropna(axis=0, how='any'),
          ))])

fig.update_layout(title_text=Titel, font_size=12)
fig.show()