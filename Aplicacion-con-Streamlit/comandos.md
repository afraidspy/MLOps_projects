## Paso 0
gcloud init

## Paso 1 Activar la API de Artifact Registry
gcloud artifacts repositories create repo-streamlit-datapath --repository-format docker --project  mlops-14-fast-api-jessica-san --location us-central1

## Paso 2: Construye la Imagen en mi PC y después lo lleva a Artifact Registry Repository
gcloud builds submit --config=cloudbuild.yaml --project mlops-14-fast-api-jessica-san

## Paso 3: Colocamos en servicio la aplicación
gcloud run services replace service.yaml --region us-central1 --project mlops-14-fast-api-jessica-san

## Paso 4: Se ejecuta una sola vez para modificar los permisos (IAM)
gcloud run services set-iam-policy mlops-14-streamlit4-jessica-san gcr-service-policy.yaml --region us-central1 --project mlops-14-fast-api-jessica-san

