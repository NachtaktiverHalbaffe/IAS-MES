# IAS MES
A MES system designed in my Bachelor Thesis. It was used to integrate a [situational risk assessment](https://github.com/NachtaktiverHalbaffe/Robotino-Situational-Risk-Assessment) into a CP facotry model process.
It uses two TCP sockets to communicate with an proprietary TCP/IP protocoll of the Festo CP Factory machines.

## Structure
### Backend
Steuerung des MES und Datenverwaltung. Entwicklet mit den Django-Framework, Celery Framework und damit verbudnene Packages wie Django Rest Framework. Aufgeteilt in 2 Apps: mesapi (API) und mesbackend(Steuerung)

### Frontend
Benutzerschnittstelle. Nicht zwingend notwenig, da die API für alle Schnittstellen auch die nötigen Weboberflächen bereitstellt. Geplant mit React-Framework. Keine hohe Priorisierung

# License
Copyright 2023 NachtaktiverHalbaffe

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
