from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


# Modèle pour la requête de génération de rapport (inchangé)
class GenerateReportRequest(BaseModel):
    dataset_id: int  # On passe à un int puisque l'ID sera généré par la DB
    template: str


# Modèle pour un Dataset (ce qui sera stocké dans la table 'datasets')
class Dataset(BaseModel):
    id: int
    filename: str
    file_path: str
    # Ou List[Dict[str, Any]] si les colonnes ont plus de détails
    columns: List[str]
    created_at: datetime

    # Permet à Pydantic de créer un modèle à partir des données de la base de données
    # Cela est utile si les noms de colonnes SQL ne correspondent pas exactement aux noms de champs Pydantic
    class Config:
        # Ancien alias_generator = to_camel, permet de mapper les snake_case de la DB aux camelCase du code Python si besoin
        from_attributes = True


# Modèle pour un Report (ce qui sera stocké dans la table 'reports')
class Report(BaseModel):
    id: int
    dataset_id: int
    template: str
    title: str
    content: str
    status: str = "completed"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Modèle pour la liste des rapports (une version allégée pour l'affichage dans l'historique)
class ReportListItem(BaseModel):
    id: int
    title: str
    template: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
