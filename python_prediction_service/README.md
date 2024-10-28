# Systeemdossier
##### **Piet-Jan Van Eede en Xander Vermeulen**
##### **Stage Apive 2024**

## Python
Als basis van ons project hebben we gebruikgemaakt van een Flask applicatie waarbij er dus allerlei endpoints zijn die 
vanuit onze Mendix applicatie aangeroepen kunnen worden. Dit is te zien in de file `webservice.py`.
### Data
Om al onze data opgeslagen hebben we een SQLite database aangemaakt, dit hebben we gedaan door ons domein model te gaan 
definiëren in het mapje ```domain``` hierin staan alle klassen die gaan gebruiken bv. 
```python
class Event(db.Model): 
```
Door  db.Model  erbij te schrijven gaat bij het runnen van de applicatie de domeinstructuur automatisch worden aangemaakt 
in onze database. 
### Domain model
Het domein bestaat uit 3 klassen:
- Event
- Fighter
- Fight

Waarbij PastFight overerft van Fight.
### Webscrapers
Om voorspelling te gaan **maken** hebben we natuurlijk enorm veel data nodig, die we niet allemaal handmatig kunnen gaan 
invullen. Daarom hebben we webscrapers geschreven die data gaan ophalen van verschillende websites. In ons geval
`ufcstats.com`. Door volgende api endpoints aan te roepen: 
````http request
GET http://localhost:5001/data/addAllEvents
Accept: application/json
````
````http request
GET http://localhost:5001/data/refreshAllFighters
Accept: application/json
````
````http request
GET http://localhost:5001/data/refreshAllFighters
Accept: application/json
````
gaan de webscrapers live data ophalen en toevoegen aan onze database. Als er natuurlijk veranderingen zijn plaats gevonden
zoals bij de fighters, als hun stats zijn aangepast of bv. als een fights gebeurd is. Dan gaat die van een PastFight naar
een gewone Fight etc.
Ook zijn er endpoints voorzien om data te verwijderen uit de database. 
````http request
GET http://localhost:5001/data/deleteAllFights
Accept: application/json
````
Deze gaan normaal gezien niet moeten opgeroepen worden, maar zijn voorzien voor het geval dat er iets misloopt en we de
database willen resetten.
Al de code voor het gebruik maken van de scraper zit in de map `database_helper` alle code die te structuur van de gescapte
data omzet naar object van onze domeinstructuur zit in de map `webservice_helper_functions`.

### Data ophalen
De endpoints die we gebruiken omdata op te halen zijn:
````http request
GET http://localhost:5001/service/getPastFights
Accept: application/json
````
````http request
GET http://localhost:5001/service/getFightsFromEvent
Accept: application/json
````
````http request
GET http://localhost:5001/service/getEvents
Accept: application/json
````
Al deze endpoints en nog andere voeren queries uit op onze database en geven de data terug in json formaat. Zodat ze via 
object mapping direct gebruikt kunnen worden in onze Mendix applicatie.
### Images
Om de images van de fighters op te halen hebben we een aparte endpoint voorzien:
````http request
GET http://localhost:5001/service/addImages
Accept: application/json
````
Deze endpoint gaat net zoals een scraper de volledige `ufc.com` website gaan scrapen en alle url van fighter images te gaan
ophalen en deze dan gaan toevoegen aan onze database.
## Voorspellingen
Om voorspellingen te gaan maken hebben we gebruik gemaakt van een neuraal netwerk. Dit zijn we gaan trainen op alle fights
die ooit gebeurd zijn in de ufc. De structuur van onze data was als volgt, elke rij bevatte de stats van de 2 fighters die tegen 
elkaar gingen vechten met als target de outcome van de fight. Deze gaf als resultaat:
- W/L
- L/W
- D/D
- NC/NC

| fighter1          | fighter1_index | height1 | weight_kg1 | avg_kd1       | avg_sub_att1  | avg_td_percentage1 | avg_significant_strike_percentage1 | avg_total_str1 | avg_round1 | avg_ctrl_seconds1 | total_wins1 | total_losses1 | total_draws1 | win_percentage1 | reach_conv1 | fighter2          | fighter2_index | height2 | weight_kg2 | avg_kd2       | avg_sub_att2  | avg_td_percentage2 | avg_significant_strike_percentage2 | avg_total_str2 | avg_round2 | avg_ctrl_seconds2 | total_wins2 | total_losses2 | total_draws2 | win_percentage2 | reach_conv2 | outcome |
|-------------------|----------------|---------|------------|---------------|---------------|---------------------|-------------------------------------|----------------|------------|-------------------|-------------|---------------|--------------|----------------|-------------|-------------------|----------------|---------|------------|---------------|---------------|---------------------|-------------------------------------|----------------|------------|-------------------|-------------|---------------|--------------|----------------|-------------|---------|
| Matt Van Buren    | 1608.0         | 195.58  | 92.98636   | 0.0           | 0.0           | 33.6                | 40.0                                | 44.25          | 1.75       | 6.5               | 0.0         | 2.0           | 0.0          | 0.0            | 75.8        | Sean O'Connell    | 2097.0         | 185.42  | 92.98636   | 0.21429       | 0.14286       | 0.0                 | 48.64                               | 45.04          | 1.71       | 58.21             | 2.0         | 5.0           | 0.0          | 28.57          | 74.0        | L/W     |
| Jamie Varner      | 1015.0         | 172.72  | 70.30676   | 0.11111       | 0.33333       | 59.21               | 34.22                               | 32.25          | 1.72       | 67.67             | 3.0         | 6.0           | 0.0          | 33.33          | 71.0        | Jason Gilliam     | 1037.0         | 182.88  | 77.11064   | 0.0           | 0.0           | 0.0                 | 21.0                                | 4.5            | 1.0        | 2.5               | 0.0         | 2.0           | 0.0          | 0.0            | 74.4        | W/L     |

Dit is de structuur van onze data (voor de training hebben we nog wel de figher1 en fighet2 columns verwijderd).
Met deze data hebben we een neuraal netwerk getraind en deze heeft een nauwkeurigheid van 80%. Zo konden we dus met onze
scraper via de upcoming fights gaan zien welke fights er nog gaan gebeuren en door de stats van de fighters mee te geven aan ons model
konden die ineens voorspellingen gaan maken over de outcome met een bepaalde zekerheid. 
De parameters van ons model hebben we bepaald met hyperparameter tuning:
````python
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV

pipeline = Pipeline([
    ('mlp', MLPClassifier())
])
param_grid = {
    'mlp__hidden_layer_sizes': [(5,5), (1, 1), (2,), (50, 50)],
    'mlp__activation': ['logistic', 'identity', 'tanh', 'relu'],
    'mlp__solver': ['adam', 'sgd'],
    'mlp__max_iter': [10000, 20000],
    'mlp__learning_rate': ['constant', 'adaptive'],
    'mlp__learning_rate_init': [0.001, 0.01, 0.1]
}
random_search = RandomizedSearchCV(pipeline, param_distributions=param_grid, n_iter=10, cv=3, n_jobs=-1, random_state=42)
model = random_search.best_estimator_
````
Dit gaf volgend resultaat:
````
Best parameters: {'mlp__solver': 'adam', 'mlp__max_iter': 20000, 'mlp__learning_rate_init': 0.01, 'mlp__learning_rate': 'adaptive', 'mlp__hidden_layer_sizes': (5, 5), 'mlp__activation': 'identity'}
````
Dit model hebben we met joblib opgeslagen zodat we het kunnen gebruiken in onze Flask applicatie. 
````python
import joblib
joblib.dump(model, '../models/ufc_mlpclassifier_model.pkl')
````
Door het model opteslagen kunnen we dus live predictions maken met ons model, als er bv. een nieuwe fight is aan gekondigd
dan worden deze gegevens opgehaald met de scraper en dan gaat ons model live een voorspelling maken over de outcome van de
fight. Deze code staat ook in de map `webservice_helper_functions`.

### Fantasy Fight
Ook voor onze feature Fantasy Fight hebben we gebruik gemaakt van ons model. Hierbij gaat de gebruiker via de mendix app
2 fighters kiezen en dan gaat ons model een voorspelling maken over de outcome van de fight. Ook al zou dit gevecht in de 
realiteit nooit kunnen gebeuren. Het endpoint dat hiervoor gebruikt wordt is:
````http request
GET http://localhost:5001/service/predictFight
Accept: application/json
````
