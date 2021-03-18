# Business rules voor Recommendation Engine
Beau Dekker - 1778763
Uitwerking opdracht business rules, met gekregen data via https://canvas.hu.nl/courses/22629/pages/backup-data-voor-opdracht-3
Mijn uitwerking is helemaal binnen de file: ruleset.py
Voor deze opdracht heb ik twee filtering systems gebruikt met mijn eigen regels. 
### Collaborative filtering
Deze filtering werkt op basis van andere users aanbevelingen maken. Ik heb van previously viewed tabel alle producten in een array gestopt en ze gegroepeert aan een gebruiker. Dan kan het algoritme met een gegeven productid kijken in welke arrays die voorkomt en dan kiest die een willekeurige id uit de arrays waar die in voor komt. Een betere versie zou kunnen zijn of er 1 product in meerdere arrays voorkomt, dan zou de het een betere predict kunnen maken.
### Content-Based filtering
Deze filter is op basis van bepaalde specificaties die overeenkomen tussen producten naar aangegeven regels. Ik heb voor alle specificaties die voorkomen bij producten een row aangemaakt met een array in een column met alle producten waarbij die specificatie voorkomt. Dus met een gegeven product id gaat die kijken in welke arrays die voorkomt, en hij sorteert al de gevonde rows op de lengte van de arrays. Zodat het algoritme makkelijk de kleinste array kan pakken, dit doe ik express want ik denk dat de kleinste overeenkomende specificaties meeste kans is op een soort gelijk product. Een betere versie zou kunnen zijn om te kijken of er een product is die in meerdere arrays zit waarbij het gegeven product ook zit, dit zou een betere predict kunnen geven.

