# ed-scout
An Elite Dangerous companion app to simplify finding unexpored worlds

## Running The Scout

Simply call `python WebUI.py`, connect to the new web service with your browser pointed at http://127.0.0.1:5000/ and try plotting a new route in Galaxy Map. You should be greeted with something along the following lines:

```
Scout is active; Waiting for next route change...
New route: 
	(G) Charted    Praea Euq QW-W d1-39: value: 2423
	(G) Charted    Praea Euq HT-T c3-5: value: 0
	(TTS) Uncharted! Praea Euq VS-L b8-3: value: None
	(M) Charted    Praea Euq CZ-J b9-0: value: 0
	(K) Uncharted! Praea Euq PZ-R c4-10: value: None
	(M) Uncharted! Praea Euq KF-I b10-3: value: None
	(M) Uncharted! Praea Euq LK-I b10-0: value: None
	(M) Charted    Pro Eurl BI-I b10-2: value: 1205
	(M) Uncharted! Pro Eurl HO-G b11-0: value: None
	(M) Uncharted! NGC 3532 Sector AI-P b7-4: value: None
	(M) Uncharted! NGC 3532 Sector CI-P b7-4: value: None
	(M) Charted    NGC 3532 Sector EI-P b7-4: value: 0
	(M) Uncharted! NGC 3532 Sector DR-U c3-5: value: None
	(M) Uncharted! NGC 3532 Sector RU-L b9-4: value: None
	(F) Uncharted! NGC 3532 Sector CL-X d1-37: value: None
	(G) Charted    NGC 3532 Sector CL-X d1-28: value: 682096
		{'bodyId': 93786802, 'bodyName': 'NGC 3532 Sector CL-X d1-28 4', 'distance': 1888, 'valueMax': 465046}
	(A) Uncharted! NGC 3532 Sector DL-X d1-40: value: Noned
```