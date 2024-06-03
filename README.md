# Federation API

/!\ Ce projet est en cours de développement /!\

Ce projet vise à construire un framework fédératif pour les plateformes de données de santé.

Il est développé dans le contexte de l'Entrepôt de Données de Santé des Hôpitaux de Paris (AP-HP).

Ce framework fédératif peut être challengé et toute personne souhaitant contribuer peut le faire dans les issues de ce projet.

Ce framework fédératif vient avec une implémentation de référence sein de ce même projet Github.

## Description

Cas d'utilisation identifiés :

* La communication d'informations entre plateformes de données de santé. Ont été identifiés comme pertinents pour le moment les informations suivantes :
  * Un référentiel des plateformes connectées à cette instance 
  * Un référentiel des projet partagés entre les plateformes connectées et des détails à leur propos, par ex. leurs membres, le cadre réglementaire du projet, les entités liées à ce projet
  * Un référentiel des demandes d'export de jeux de données de plateforme à plateforme

Contraintes imposées : 

* La décentralisation : Une plateforme de données de santé peut se connecter à plusieurs instances de cette API de fédération pour échanger avec diverses plateformes de données de santé et limiter les informations partagées selon les besoins de chaque collaboration.
* Sécurité des informations échangées :
  * Cette API n'interagissant pas avec des données sensibles non chiffrées, elle peut être installée dans un endroit moins contraignant réglementairement (cloud non certifié HDS par ex.)
  * Toute information potentiellement sensible est chiffrée à l'aide d'un système similaire à mTLS : seules les plateformes clientes de cette API peuvent chiffrer et déchiffrer des informations sensibles contenues dans cette API. Cette API ne dispose d'aucune clé de chiffrement de la donnée stockée.
  * L'API est sécurisée au moyen d'un système d'authentification et chaque plateforme y accédant dispose de droits spécifiques
  * L'administrateur de l'API est le seul en capacité de délivrer à des plateformes des accès à cette API

