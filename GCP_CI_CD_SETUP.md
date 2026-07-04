# Google Cloud CI/CD Setup Guide

## Overview
This project is configured for automated testing and deployment using:
- **Google Cloud Source Repositories** - Version control
- **Google Cloud Build** - CI/CD automation

## Prerequisites
- Google Cloud Project with billing enabled
- `gcloud` CLI installed
- Appropriate IAM permissions (Cloud Build Editor, Source Repository Admin)

## Step 1: Set Up Cloud Source Repository

### 1.1 Initialize the repository (one-time setup)

```bash
gcloud init  # If not already authenticated

# Create the repository in your project
gcloud source repos create ronin-concierge --project=YOUR_PROJECT_ID

# Add the Cloud Source Repo as a remote
git remote add google \
  https://source.developers.google.com/p/YOUR_PROJECT_ID/r/ronin-concierge
```

### 1.2 Configure Git authentication

```bash
gcloud auth application-default login
gcloud auth configure-docker
```

### 1.3 Push to Cloud Source Repository

```bash
git push google main
```

## Step 2: Set Up Cloud Build

### 2.1 Enable the Cloud Build API

```bash
gcloud services enable cloudbuild.googleapis.com \
  --project=YOUR_PROJECT_ID
```

### 2.2 Grant Cloud Build permissions

```bash
# Get your Cloud Build service account
PROJECT_ID=$(gcloud config get-value project)
CLOUD_BUILD_SA="${PROJECT_ID}@cloudbuild.gserviceaccount.com"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$CLOUD_BUILD_SA \
  --role=roles/cloudbuild.builds.editor
```

### 2.3 Create a Cloud Build trigger

```bash
gcloud builds triggers create github \
  --name="ronin-agents-test" \
  --repo-name=YOUR_GITHUB_REPO_NAME \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --project=YOUR_PROJECT_ID
```

**OR** for Cloud Source Repository:

```bash
gcloud builds triggers create cloud-source-repositories \
  --name="ronin-agents-test" \
  --repo=ronin-concierge \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --project=YOUR_PROJECT_ID
```

## Step 3: Verify Cloud Build Configuration

### 3.1 Check triggers

```bash
gcloud builds triggers list --project=YOUR_PROJECT_ID
```

### 3.2 Manually trigger a build

```bash
gcloud builds submit . \
  --config=cloudbuild.yaml \
  --project=YOUR_PROJECT_ID
```

### 3.3 View build logs

```bash
# List recent builds
gcloud builds log LATEST --project=YOUR_PROJECT_ID

# Watch a specific build
gcloud builds log BUILD_ID --stream --project=YOUR_PROJECT_ID
```

## Step 4: Local Testing

Run tests locally before pushing:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=agents --cov=core --cov=chef_knowledge

# Run linting
pylint agents/ core/ chef_knowledge/
```

## Step 5: Set Up Notifications (Optional)

### Cloud Build notifications to Slack/Email

```bash
# Create a Pub/Sub topic for build notifications
gcloud pubsub topics create cloud-builds

# Subscribe to notifications
gcloud pubsub subscriptions create cloud-builds-sub \
  --topic=cloud-builds

# Update your trigger to publish to Pub/Sub
# (Configure in Cloud Console: Cloud Build > Triggers > Edit)
```

## Environment Variables

Add secrets to Cloud Build:

```bash
# Store API keys securely
echo -n "YOUR_API_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --project=YOUR_PROJECT_ID

# Grant Cloud Build access to the secret
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member=serviceAccount:$CLOUD_BUILD_SA \
  --role=roles/secretmanager.secretAccessor
```

Update `cloudbuild.yaml` to use secrets:

```yaml
env:
  - 'GEMINI_API_KEY=/workspace/secrets/gemini-api-key'
secretEnv: ['GEMINI_API_KEY']
availableSecrets:
  secretManager:
  - versionName: projects/$PROJECT_ID/secrets/gemini-api-key/versions/latest
    env: 'GEMINI_API_KEY'
```

## Next Steps

1. **Deploy to Cloud Run** - Update `cloudbuild.yaml` with deployment step
2. **Add more tests** - Expand test suite in `tests/`
3. **Set up monitoring** - Use Cloud Logging and Cloud Trace
4. **Enable auto-remediation** - Configure Cloud Build to auto-retry on failure

## Troubleshooting

### Build fails with "permission denied"
```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*cloudbuild*"
```

### Tests fail in Cloud Build but pass locally
- Check Python version matches (3.11)
- Verify all dependencies are in `requirements.txt` and `requirements-dev.txt`
- Check for environment-specific issues (Windows vs Linux paths)

### View detailed build logs
```bash
gcloud builds log BUILD_ID --limit=1000 --stream
```

## References
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Source Repositories](https://cloud.google.com/source-repositories/docs)
- [pytest Documentation](https://docs.pytest.org/)
